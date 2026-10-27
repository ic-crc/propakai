# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.1546-6.

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite this software
    package along with the underlying ITU-R standard:

    * **ITU-R Standard:** International Telecommunication Union (2019).
      *Recommendation ITU-R P.1546-6: Method for point-to-area predictions for terrestrial services
      in the frequency range 30 MHz to 4000 MHz*. Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.1546/en
"""

from os.path import join
from math import log10, exp, sqrt, atan, degrees, pi, pow as fpow
from enum import Enum
from bisect import bisect_left, bisect_right
from threading import Lock
from filelock import FileLock
import xlrd
from propakai import types
from propakai import _download_utils as _du
from propakai import p1057_7


__all__ = ['Path',
           'Environment',
           'basic_transmission_loss',
           'okumura_hata_field_strength']


class Path(Enum):
    """
    Enumerates integer values that can be used for the path_type_profile parameter of the
    basic_transmission_loss() function.
    """
    LAND     = 4
    COLD_SEA = 1
    WARM_SEA = 2


class _Path(Enum):
    LAND     = 4
    COLD_SEA = 1
    WARM_SEA = 2
    SEA      = 3


class Environment(Enum):
    """Enumerates environments for the basic_transmission_loss() function."""
    URBAN         = 1
    RURAL_OR_OPEN = 2


def basic_transmission_loss(f_mhz: float,
                            t_percent: float,
                            ha_m: float,
                            h2_m: float,
                            env2: Environment,
                            d_profile_km: types.FloatArray,
                            h_profile_mamsl: types.FloatArray|None,
                            path_type_profile: types.IntArray|None=None,
                            r1_m: float|None=None,
                            r2_m: float=15.0,
                            q_percent: float=50.0,
                            sigma_l_db: float|None=None,
                            wa_m: float=500.0
                            ) -> tuple[float, float]:
    """
    ITU-R P.1546-6, Annex 6.

    Computes the basic transmission loss (dB) and field strength (dBμV/m) for 1 kW e.r.p.
    using the step-by-step procedure in Annex 6.
    - Does not include parts related to the Regional Radiocommunication Conference RRC-06.
    - Does not include the adjustment for different climatic regions of Annex 7.

    Args:
        f_mhz (float): Frequency (MHz), with 30 <= f_mhz <= 4000.
        t_percent (float): Percentage of time (%) for which the basic transmission loss is not
            exceeded, with 1 <= t_percent <= 50.
        ha_m (float): Transmitter antenna height above ground (m), with 1 < ha_m. When over sea,
            ha_m is the transmitter antenna height above the surface of the sea (m). The
            Recommendation is not reliable in the case of a sea path and a ha_m value less than 3 m.
        h2_m (float): Receiver antenna height above ground (m), with 1 <= h2_m < 3000 for land
            paths and 3 <= h2_m < 3000 for sea paths.
        env2 (Environment): Environment around the receiver (URBAN or RURAL_OR_OPEN). Unused when
            the receiver is over sea (according to path_type_profile).
        d_profile_km (types.FloatArray): Distance from transmitter (km) profile of n points, up to
            the receiver, with 2 <= n (i.e. must at least include 0 and the tx-rx distance). The
            Recommendation is valid for distances up to 1000 km.
        h_profile_mamsl (types.FloatArray|None): Terrain height profile of n points (meters above
            mean sea level), at the corresponding distance from d_profile_km. If None, flat terrain
            is assumed.
        path_type_profile (types.IntArray|None, optional): Path type profile of n points (land = 4,
            cold sea = 1, warm sea = 2), at the corresponding distance from d_profile_km. If None,
            an all-land path is assumed. Default is None.
        r1_m (float, optional): Representative clutter height around the transmitter (m). Use None
            for an open/uncluttered transmitter. Default is None.
        r2_m (float, optional): Representative clutter height around the receiver (m). Only used
            when env2 is URBAN. Default is 15 m.
        q_percent (float, optional): Percentage location (%), with 1 <= q_percent <= 99. Default is
            50 %.
        sigma_l_db (float|None, optional): Standard deviation of the Gaussian distribution of the
            local means in the study area (dB). Used only for q_percent values different than 50.
            Computed automatically if required and not provided. Default is None.
        wa_m (float, optional): Prediction resolution (m) for computing sigma_l_db if required and
            not provided, with 50 <= wa_m <= 1000. Default is 500 m.

    Returns:
        Lb (float): Basic transmission loss (dB).
        E (float): Field strength (dBμV/m) for 1 kW e.r.p.
    """
    _input_validattion(f_mhz, t_percent, ha_m, h2_m, d_profile_km, h_profile_mamsl,
                       path_type_profile, q_percent)

    d_km = d_profile_km[-1]

    if d_km <= 0.04:
        # Step 17
        E = _fs_0_to_40m_dist(ha_m, h2_m, d_km, h_profile_mamsl)

        # required at Step 19 below
        first_path_type, second_path_type = _propagation_types(path_type_profile)
    else:
        # Step 1
        first_path_type, second_path_type = _propagation_types(path_type_profile)
        first_path_h1_m, second_path_h1_m = _compute_h1_m(first_path_type, second_path_type, ha_m,
                                                          d_profile_km, h_profile_mamsl)

        if d_km < 1.0:
            d_km = 1.0

        # Steps 2 to 10 inclusively
        E = _fs_tables_interpolation(f_mhz, t_percent, first_path_type, first_path_h1_m, d_km,
                                     ha_m, d_profile_km, h_profile_mamsl)

        # Step 11
        if second_path_type is not None: # i.e. if we have a mixed path
            E_first = E
            assert second_path_h1_m is not None
            E_second = _fs_tables_interpolation(f_mhz, t_percent, second_path_type,
                                                second_path_h1_m, d_km, ha_m, d_profile_km,
                                                h_profile_mamsl)
            if first_path_type == Path.LAND:
                E_land = E_first
                E_sea = E_second
            else:
                E_land = E_second
                E_sea = E_first
            assert path_type_profile is not None
            E = _mixed_path_field_strength(E_land, E_sea, d_profile_km, path_type_profile)

        # Step 12
        if h_profile_mamsl is not None:
            if path_type_profile is None or Path(path_type_profile[-1]) == Path.LAND: #if rx on land
                theta_tca_deg = _terrain_clearance_angle_from_rx_deg(h2_m, d_profile_km,
                                                                     h_profile_mamsl)
                E += _terrain_clearance_angle_correction(f_mhz, theta_tca_deg)

        # Step 13
        if h_profile_mamsl is not None:
            theta_eff_deg = _terrain_clearance_angle_from_tx_deg(ha_m, d_profile_km,
                                                                 h_profile_mamsl)
            theta_deg = _terrain_clearance_angle_from_rx_deg(h2_m, d_profile_km,
                                                             h_profile_mamsl)
            E_ts = _tropospheric_scattering_field_strength(f_mhz, t_percent, d_km,
                                                           theta_eff_deg, theta_deg)
            E = max(E, E_ts)

        # Step 14
        # If mixed path, use h1 value for land (although the rec. is not clear on this)
        temp_h1_m = first_path_h1_m
        if second_path_h1_m is not None:
            temp_h1_m = min(first_path_h1_m, second_path_h1_m)
        E += _rx_antenna_height_correction(f_mhz, temp_h1_m, h2_m, d_km, path_type_profile, r2_m,
                                           env2)

        # Step 15
        if r1_m is not None:
            E += _cluttered_transmitter_correction(f_mhz, ha_m, r1_m)

        # Step 16
        E += _antenna_height_diff_correction(ha_m, h2_m, d_km, h_profile_mamsl)

        # make sure d_km is restored to its original value
        d_km = d_profile_km[-1]

        # Step 17
        if d_km < 1.0:
            E = _fs_40_to_1000m_dist(E, ha_m, h2_m, d_km, h_profile_mamsl)

    # Step 18
    E = _apply_location_variability(E, q_percent, path_type_profile, sigma_l_db, f_mhz, wa_m)

    # Step 19
    if second_path_type is not None and t_percent < 50.0:
        E_max = _max_fs_mixed_path(t_percent, d_profile_km, path_type_profile)
    else:
        E_max = _max_fs(t_percent, first_path_type, d_km)
    E = min(E, E_max)

    # Step 20
    Lb = _equivalent_basic_transmission_loss(E, f_mhz)

    return (Lb, E) # (dB, dBuV/m)


def _input_validattion(f_mhz: float, t_percent: float, ha_m: float, h2_m: float,
                       d_profile_km: types.FloatArray, h_profile_mamsl: types.FloatArray|None,
                       path_type_profile: types.IntArray|None, q_percent: float) -> None:
    if f_mhz < 30.0 or f_mhz > 4000:
        raise ValueError('f_mhz is out of range.')
    if t_percent < 1.0 or t_percent > 50.0:
        raise ValueError('t_percent is out of range.')
    if ha_m <= 1.0:
        raise ValueError('ha_m is out of range.')
    if h2_m < 1.0 or h2_m >= 3000.0:
        raise ValueError('h2_m is out of range.')
    if len(d_profile_km) < 2:
        raise ValueError('d_profile_km must contain at least 2 distances.')
    if d_profile_km[-1] > 1000.0:
        raise ValueError('Distance (km) is out of range.')
    if h_profile_mamsl is not None:
        if len(h_profile_mamsl) != len(d_profile_km):
            raise ValueError('Unexpected number of items in h_profile_mamsl.')
    if path_type_profile is not None:
        if len(path_type_profile) != len(d_profile_km):
            raise ValueError('Unexpected number of items in path_type_profile.')
    if q_percent < 1.0 or q_percent > 99.0:
        raise ValueError('q_percent is out of range.')


def _fs_tables_entry(nominal_f_mhz: int, nominal_t_percent: int, path: Path,
                     nominal_h1_m: float, nominal_d_km: int) -> float:
    """
    ITU-R P.1546-6, Annex 2, 3, and 4.

    Gets a non-interpolated field strength value (dBuV/m) from the Recommendation's field strength
    tables.
    
    Args:
        nominal_f_mhz (int): Frequency (MHz). One of 100, 600, 2000.
        nominal_t_percent (int): Percentage of time for which the field strength is exceeded
            (percent). One of 1, 10, 50.
        path (Path): One of LAND, COLD_SEA, WARM_SEA.
        nominal_h1_m (float): Transmitting/base antenna height (m). One of 10, 20, 37.5, 75, 150,
            300, 600, 1200.
        nominal_d_km (float): One of the nominal distance (km), from the recommendation's Table 1.

    Returns:
        float: Non-interpolated field strength (dBuV/m) for 1 kW e.r.p.
    """
    if nominal_t_percent == 50 and (path==Path.COLD_SEA or path==Path.WARM_SEA):
        table_path = _Path.SEA
    else:
        table_path = _Path(path.value)
    key = (nominal_f_mhz, nominal_t_percent, table_path, nominal_h1_m)
    fs_tables = _thread_safe_get_fs_tables()
    by_dist_fs_list = fs_tables[key]
    index = bisect_left(_p1546_6_shared['nominal_dists_km'], nominal_d_km)
    fs_dBuVm = by_dist_fs_list[index]
    return fs_dBuVm


def _max_fs(t_percent: float, path: Path, d_km: float) -> float:
    """ITU-R P.1546-6, Annex 5, Section 2."""
    E_fs = 106.9 - 20.0*log10(d_km)
    if path == Path.LAND:
        return E_fs
    else:
        E_se = 2.38*(1.0-exp(-d_km/8.94))*log10(50.0/t_percent)
        return E_fs + E_se


def _compute_h1_m(path1: Path, path2: Path|None, ha_m: float,
                  d_profile_km: types.FloatArray,
                  h_profile_mamsl: types.FloatArray|None
                  ) -> tuple[float, float|None]:
    """ITU-R P.1546-6, Annex 5, Section 3."""
    if path2 is None and (path1 == Path.COLD_SEA or path1 == Path.WARM_SEA):
        # all-sea path
        return (ha_m, None)

    # either all-land or mixed path from now on
    # From Annex 5, Section 8 on mixed paths: "The value of h1 should be calculated using Annex 5,
    # § 3, taking the height of any sea surface as though land. Normally this value of h1 will be
    # used for both E_land(d) and E_sea(d). However, if h1 is less than 3 m it should still be used
    # for E_land(d), but a value of 3 m should be used for E_sea(d)."
    d_km = d_profile_km[-1]
    if h_profile_mamsl is None:
        # no terrain data
        heff_m = ha_m # assume flat terrain
        if d_km <= 3.0:
            h1_m = ha_m
        elif d_km < 15.0:
            h1_m = ha_m + (heff_m-ha_m)*(d_km-3.0)/12.0
        else:
            h1_m = heff_m
    else:
        # terrain data available
        avg_h_m = _averaged_terrain_height_m(d_profile_km, h_profile_mamsl,
                                             min(0.2*d_km, 3.0), min(d_km, 15.0))
        heff_or_hb_m = ha_m + h_profile_mamsl[0] - avg_h_m
        h1_m = heff_or_hb_m

    if path2 is None:
        # all-land path
        return (h1_m, None)
    else:
        # mixed path
        if path1 == Path.LAND:
            return (h1_m, max(h1_m, 3.0)) # land, sea
        else:
            return (max(h1_m, 3.0), h1_m) # sea, land


def _fs_height_interpolation(nominal_f_mhz: float, nominal_t_percent: float, path: Path,
                             h1_m: float, d_km: float, ha_m: float, d_profile_km: types.FloatArray,
                             h_profile_mamsl: types.FloatArray|None) -> float:
    """ITU-R P.1546-6, Annex 5, Section 4."""
    if h1_m >= 10.0:
        return _fs_height_interpolation_1(nominal_f_mhz, nominal_t_percent, path, h1_m, d_km)
    elif h1_m >= 0.0:
        return _fs_height_interpolation_2(nominal_f_mhz, nominal_t_percent, path, h1_m, d_km)
    else:
        return _fs_height_interpolation_3(nominal_f_mhz, nominal_t_percent, path, h1_m, d_km,
                                          ha_m, d_profile_km, h_profile_mamsl)


def _fs_height_interpolation_1(nominal_f_mhz: float, nominal_t_percent: float, path: Path,
                               h1_m: float, d_km: float) -> float:
    """ITU-R P.1546-6, Annex 5, Section 4.1 (10 <= h1_m <= 3000)."""
    h_inf, h_sup = _nominal_heights_m(h1_m)
    E = E_inf = _fs_distance_interpolation(nominal_f_mhz, nominal_t_percent, path, h_inf, d_km)
    if h_sup is not None:
        E_sup = _fs_distance_interpolation(nominal_f_mhz, nominal_t_percent, path, h_sup, d_km)
        E = E_inf + (E_sup-E_inf)*log10(h1_m/h_inf)/log10(h_sup/h_inf)
    E = min(E, _max_fs(nominal_t_percent, path, d_km))
    return E # (dBuV/m)


def _nominal_heights_m(h1_m: float) -> tuple[float, float|None]:
    """ITU-R P.1546-6, Annex 5, Section 4.1 (also see Annex 6, Step 8.1.1)."""
    nominal_heights_m = _p1546_6_shared['nominal_heights_m']
    if h1_m > 1200.0:
        return (600.0, 1200.0)
    index = bisect_left(nominal_heights_m, h1_m)
    if h1_m == nominal_heights_m[index]:
        return (h1_m, None)
    else:
        return (nominal_heights_m[index-1], nominal_heights_m[index])


def _fs_height_interpolation_2(nominal_f_mhz: float, nominal_t_percent: float, path: Path,
                               h1_m: float, d_km: float) -> float:
    """ITU-R P.1546-6, Annex 5, Section 4.2 (0 <= h1_m < 10)."""
    def _eq9_E(nominal_f_mhz: float, nominal_t_percent: float, path: Path, h1_m: float, d_km: float
              ) -> float:
        E10 = _fs_height_interpolation_1(nominal_f_mhz, nominal_t_percent, path, 10.0, d_km)
        E20 = _fs_height_interpolation_1(nominal_f_mhz, nominal_t_percent, path, 20.0, d_km)
        Ch1neg10 = _Ch1(nominal_f_mhz, -10.0)
        C1020 = E10-E20
        Ezero = E10 + 0.5*(C1020+Ch1neg10)
        E = Ezero + 0.1*h1_m*(E10-Ezero)
        return E

    if path == Path.LAND:
        E = _eq9_E(nominal_f_mhz, nominal_t_percent, path, h1_m, d_km)
    else:
        Dh1 = _D06(nominal_f_mhz, h1_m, 10.0)
        if d_km <= Dh1:
            E = _max_fs(nominal_t_percent, path, d_km)
        else:
            D20 = _D06(nominal_f_mhz, 20.0, 10.0)
            if d_km < D20:
                EDh1 = _max_fs(nominal_t_percent, path, Dh1)
                E10_D20 = _fs_height_interpolation_1(nominal_f_mhz, nominal_t_percent, path,
                                                     10.0, D20)
                E20_D20 = _fs_height_interpolation_1(nominal_f_mhz, nominal_t_percent, path,
                                                     20.0, D20)
                ED20 = E10_D20 + (E20_D20 - E10_D20)*log10(h1_m/10.0)/log10(20.0/10.0)
                E = EDh1 + (ED20-EDh1)*log10(d_km/Dh1)/log10(D20/Dh1)
            else:
                Fs = (d_km-D20)/d_km
                E10_d = _fs_height_interpolation_1(nominal_f_mhz, nominal_t_percent, path,
                                                   10.0, d_km)
                E20_d = _fs_height_interpolation_1(nominal_f_mhz, nominal_t_percent, path,
                                                   20.0, d_km)
                Ep = E10_d+(E20_d-E10_d)*log10(h1_m/10.0)/log10(20.0/10.0)
                Epp = _eq9_E(nominal_f_mhz, nominal_t_percent, path, h1_m, d_km)
                E = Ep*(1.0-Fs) + Epp*Fs

    return E # (dBuV/m)


def _fs_height_interpolation_3(nominal_f_mhz: float, nominal_t_percent: float, path: Path,
                               h1_m: float, d_km: float, ha_m: float,
                               d_profile_km: types.FloatArray,
                               h_profile_mamsl: types.FloatArray|None
                               ) -> float:
    """ITU-R P.1546-6, Annex 5, Section 4.3 (h1_m < 0)."""
    E = _fs_height_interpolation_2(nominal_f_mhz, nominal_t_percent, path, 0.0, d_km)
    if h_profile_mamsl is not None:
        theta_eff1_deg = _terrain_clearance_angle_from_tx_deg(ha_m, d_profile_km, h_profile_mamsl)
        Ch1_dB = _terrain_clearance_angle_correction(nominal_f_mhz, theta_eff1_deg)
    else:
        Ch1_dB = _Ch1(nominal_f_mhz, h1_m)
    assert Ch1_dB < 0.0
    return E + Ch1_dB # dBuV/m


def _Ch1(nominal_f_mhz: float, h1_m: float) -> float:
    """ITU-R P.1546-6, Annex 5, Section 4.3, eq.(12)."""
    Kv_map = {100: 1.35, 600: 3.31, 2000: 6.00}
    Kv = Kv_map[int(nominal_f_mhz)]
    theta_eff2_deg = degrees(atan(-h1_m/9000.0))
    v = Kv*theta_eff2_deg
    Ch1_dB = 6.03-_J(v)
    return Ch1_dB


def _J(v) -> float:
    """ITU-R P.1546-6, Annex 5, Section 4.3, eq. (12a), (12b)."""
    Jv = 0.0
    if v > -0.7806:
        Jv = 6.9 + 20.0*log10( sqrt((v-0.1)**2 + 1.0) + v - 0.1 )
    return Jv


def _terrain_clearance_angle_from_tx_deg(ha_m: float, d_profile_km: types.FloatArray,
                                         h_profile_mamsl: types.FloatArray) -> float:
    """
    ITU-R P.1546-6, Annex 5, Section 4.3.
    Returned angle positive above the horizon, negative below the horizon.
    """
    max_dist_km = 15.0
    clearance_angle_deg = -90
    tx_height_mamsl = ha_m + h_profile_mamsl[0]
    for d_km, h_m in zip(d_profile_km[1:], h_profile_mamsl[1:]): # skip 0km dist
        if d_km > max_dist_km:
            break
        y_m = h_m - tx_height_mamsl
        angle_deg = degrees(atan(y_m/(d_km*1000.0)))
        clearance_angle_deg = max(angle_deg, clearance_angle_deg)

    # ensure at least one angle will be calculated
    if clearance_angle_deg == -90:
        end_dist_km = min(max_dist_km, d_profile_km[-1])
        y_m = _interpolate_h_profile(d_profile_km, h_profile_mamsl, end_dist_km) - tx_height_mamsl
        angle_deg = degrees(atan(y_m/(end_dist_km*1000.0)))
        clearance_angle_deg = max(angle_deg, clearance_angle_deg)

    return clearance_angle_deg


def _fs_distance_interpolation(nominal_f_mhz: float, nominal_t_percent: float, path: Path,
                               nominal_h1_m: float, d_km: float) -> float:
    """ITU-R P.1546-6, Annex 5, Section 5."""
    d_inf, d_sup = _nominal_distances_km(d_km)
    E = E_inf = _fs_tables_entry(int(nominal_f_mhz), int(nominal_t_percent), path, nominal_h1_m,
                                 int(d_inf))
    if d_sup is not None:
        E_sup = _fs_tables_entry(int(nominal_f_mhz), int(nominal_t_percent), path, nominal_h1_m,
                                 int(d_sup))
        E = E_inf + (E_sup-E_inf)*log10(d_km/d_inf)/log10(d_sup/d_inf)
    return E # (dBuV/m)


def _nominal_distances_km(d_km: float) -> tuple[float, float|None]:
    """ITU-R P.1546-6, Annex 5, Section 5 (see also Annex 6, Step 4)."""
    nominal_dists_km = _p1546_6_shared['nominal_dists_km']
    index = bisect_left(nominal_dists_km, d_km)
    if d_km == nominal_dists_km[index]:
        return (d_km, None)
    else:
        return (nominal_dists_km[index-1], nominal_dists_km[index])


def _fs_time_percentage_interpolation(f_mhz: float, t_percent: float, path: Path, h1_m: float,
                                      d_km: float, ha_m: float, d_profile_km: types.FloatArray,
                                      h_profile_mamsl: types.FloatArray|None) -> float:
    """ITU-R P.1546-6, Annex 5, Section 7."""
    t_inf, t_sup = _nominal_time_percentages(t_percent)
    E = E_inf = _fs_frequency_interpolation(f_mhz, t_inf, path, h1_m, d_km, ha_m, d_profile_km,
                                            h_profile_mamsl)
    if t_sup is not None:
        E_sup = _fs_frequency_interpolation(f_mhz, t_sup, path, h1_m, d_km, ha_m, d_profile_km,
                                            h_profile_mamsl)
        Q_inf = p1057_7.q_inv(t_inf/100.0)
        Q_sup = p1057_7.q_inv(t_sup/100.0)
        Q_t = p1057_7.q_inv(t_percent/100.0)
        E = E_sup*(Q_inf-Q_t)/(Q_inf-Q_sup) + E_inf*(Q_t-Q_sup)/(Q_inf-Q_sup)
    return E # (dBuV/m)


def _nominal_time_percentages(t_percent: float) -> tuple[float, float|None]:
    """ITU-R P.1546-6, Annex 5, Section 7 (see also Annex 6, Step 2)."""
    if t_percent in (1.0, 10.0, 50.0):
        return (t_percent, None)
    if t_percent < 10.0:
        return (1.0, 10.0)
    else:
        return (10.0, 50.0)


def _fs_frequency_interpolation(f_mhz: float, nominal_t_percent: float, path: Path, h1_m: float,
                                d_km: float, ha_m: float, d_profile_km: types.FloatArray,
                                h_profile_mamsl: types.FloatArray|None) -> float:
    """ITU-R P.1546-6, Annex 5, Section 6."""
    d600_km = _D06(600.0, h1_m, 10.0)
    if path != Path.LAND and f_mhz < 100.0 and d_km < d600_km:
        # use alternate method
        df_km = _D06(f_mhz, h1_m, 10.0)
        if d_km <= df_km:
            E = _max_fs(nominal_t_percent, path, d_km)
        else:
            E_df = _max_fs(nominal_t_percent, path, df_km)
            E_d600 = _fs_frequency_interpolation(f_mhz, nominal_t_percent, path, h1_m, d600_km,
                                                 ha_m, d_profile_km, h_profile_mamsl)
            E = E_df + (E_d600-E_df)*log10(d_km/df_km)/log10(d600_km/df_km)
    else:
        # use normal method
        f_inf, f_sup = _nominal_frequencies_mhz(f_mhz)
        E = E_inf = _fs_height_interpolation(f_inf, nominal_t_percent, path, h1_m, d_km, ha_m,
                                             d_profile_km, h_profile_mamsl)
        if f_sup is not None:
            E_sup = _fs_height_interpolation(f_sup, nominal_t_percent, path, h1_m, d_km, ha_m,
                                             d_profile_km, h_profile_mamsl)
            E = E_inf + (E_sup-E_inf)*log10(f_mhz/f_inf)/log10(f_sup/f_inf) # eq.(14)
        if f_mhz > 2000.0:
            E = min(E, _max_fs(nominal_t_percent, path, d_km))
    return E # (dBuV/m)


def _nominal_frequencies_mhz(f_mhz: float) -> tuple[float, float|None]:
    """ITU-R P.1546-6, Annex 5, Section 6 (see also Annex 6, Step 3)."""
    if f_mhz in (100.0, 600.0, 2000.0):
        return (f_mhz, None)
    if f_mhz < 600.0:
        return (100.0, 600.0)
    else:
        return (600.0, 2000.0)


def _mixed_path_field_strength(e_land_dbuvm: float, e_sea_dbuvm: float,
                               d_profile_km: types.FloatArray,
                               path_type_profile: types.IntArray) -> float:
    """ITU-R P.1546-6, Annex 5, Section 8."""
    E_sea = e_sea_dbuvm
    E_land = e_land_dbuvm
    delta = E_sea - E_land
    V = max(1.0, 1.0+(delta/40.0))
    d_total_km = d_profile_km[-1]
    d_sea_km = _total_sea_distance_km(d_profile_km, path_type_profile)
    F_sea = d_sea_km/d_total_km
    A0 = 1.0 - fpow(1.0-F_sea, 2.0/3.0)
    A = fpow(A0, V)
    E_dBuVm = (1.0-A)*E_land + A*E_sea
    return E_dBuVm


def _rx_antenna_height_correction(f_mhz: float, h1_m: float, h2_m: float, d_km: float,
                                  path_type_profile: types.IntArray|None, r2_m: float,
                                  env2: Environment) -> float:
    """ITU-R P.1546-6, Annex 5, Section 9."""
    if path_type_profile is not None:
        rx_path_type = Path(path_type_profile[-1])
    else:
        rx_path_type = Path.LAND # assumes land

    Kh2 = 3.2 + 6.2*log10(f_mhz)
    if rx_path_type == Path.LAND:
        if env2 == Environment.URBAN:
            R2p = (1000.0*d_km*r2_m - 15.0*h1_m)/(1000.0*d_km-15.0)
            R2p = max(R2p, 1.0)
            if h2_m < R2p:
                hdif2_m = R2p - h2_m
                theta_clut2_deg = degrees(atan(hdif2_m/27.0))
                Knu = 0.0108*sqrt(f_mhz)
                v = Knu*sqrt(hdif2_m*theta_clut2_deg)
                correction_dB = 6.03 - _J(v)
            else:
                correction_dB = Kh2*log10(h2_m/R2p)
            if R2p < 10.0:
                correction_dB -= Kh2*log10(10.0/R2p)
        else: # non-urban
            correction_dB = Kh2*log10(h2_m/10.0)
    else: # sea
        if h2_m >= 10.0:
            correction_dB = Kh2*log10(h2_m/10.0)
        else:
            d10_km = _D06(f_mhz, h1_m, 10.0)
            if d_km >= d10_km:
                correction_dB = Kh2*log10(h2_m/10.0)
            else:
                dh2_km = _D06(f_mhz, h1_m, h2_m)
                if d_km <= dh2_km:
                    correction_dB = 0.0
                else:
                    C10 = Kh2*log10(h2_m/10.0)
                    correction_dB = C10*log10(d_km/dh2_km)/log10(d10_km/dh2_km)

    return correction_dB


def _cluttered_transmitter_correction(f_mhz: float, ha_m: float, r1_m: float) -> float:
    """ITU-R P.1546-6, Annex 5, Section 10."""
    Knu = 0.0108*sqrt(f_mhz)
    hdif1_m = ha_m - r1_m
    theta_clut1_deg = degrees(atan(hdif1_m/27.0))
    if r1_m >= ha_m:
        v = Knu*sqrt(hdif1_m*theta_clut1_deg)
    else:
        v = -Knu*sqrt(hdif1_m*theta_clut1_deg)
    correction_dB = -_J(v)
    return correction_dB


def _terrain_clearance_angle_correction(f_mhz: float, theta_tca_deg: float) -> float:
    """ITU-R P.1546-6, Annex 5, Section 11."""
    theta_tca_deg = max(theta_tca_deg, 0.55)
    theta_tca_deg = min(theta_tca_deg, 40.0)
    sqrt_f = sqrt(f_mhz)
    vp = 0.036*sqrt_f
    v = 0.065*theta_tca_deg*sqrt_f
    correction_dB = _J(vp) - _J(v)
    return correction_dB


def _terrain_clearance_angle_from_rx_deg(h2_m: float, d_profile_km: types.FloatArray,
                                         h_profile_mamsl: types.FloatArray) -> float:
    """
    ITU-R P.1546-6, Annex 5, Section 11.
    Returned angle positive above the horizon, negative below the horizon.
    """
    total_dist_km = d_profile_km[-1]
    reversed_d_profile_km = [total_dist_km - d for d in reversed(d_profile_km)]
    reversed_h_profile_mamsl = h_profile_mamsl[::-1]

    max_dist_km = 16.0
    clearance_angle_deg = -90
    rx_height_mamsl = h2_m + reversed_h_profile_mamsl[0]
    for d_km, h_m in zip(reversed_d_profile_km[1:], reversed_h_profile_mamsl[1:]): # skip 0km dist
        if d_km > max_dist_km:
            break
        y_m = h_m - rx_height_mamsl
        angle_deg = degrees(atan(y_m/(d_km*1000.0)))
        clearance_angle_deg = max(angle_deg, clearance_angle_deg)

    # ensure at least one angle will be calculated
    if clearance_angle_deg == -90:
        end_dist_km = min(max_dist_km, reversed_d_profile_km[-1])
        y_m = _interpolate_h_profile(reversed_d_profile_km, reversed_h_profile_mamsl, end_dist_km) \
            - rx_height_mamsl
        angle_deg = degrees(atan(y_m/(end_dist_km*1000.0)))
        clearance_angle_deg = max(angle_deg, clearance_angle_deg)

    return clearance_angle_deg


def _apply_location_variability(e_median_dbuvm: float, q_percent: float,
                                path_type_profile: types.IntArray|None,
                                sigma_l_db: float|None, f_mhz: float, wa_m: float) -> float:
    """ITU-R P.1546-6, Annex 5, Section 12."""
    if q_percent == 50.0:
        return e_median_dbuvm
    if path_type_profile is not None: # otherwise assumes LAND
        rx_path_type = Path(path_type_profile[-1])
        if rx_path_type == Path.WARM_SEA or rx_path_type == Path.COLD_SEA:
            return e_median_dbuvm
    if sigma_l_db is None:
        sigma_l_db = (0.024*f_mhz/1000.0 + 0.52)*fpow(wa_m, 0.28)
    E_dBuVm = e_median_dbuvm +  p1057_7.q_inv(q_percent/100.0)*sigma_l_db
    return E_dBuVm


def _tropospheric_scattering_field_strength(f_mhz: float, t_percent: float, d_km: float,
                                            theta_eff_deg: float, theta_deg: float) -> float:
    """ITU-R P.1546-6, Annex 5, Section 13.
    
    Args:
        theta_eff_deg (float): The h1 terminal's terrain clearance angle in degrees calculated
            using the method in § 4.3 case a), whether or not h1 is negative (degrees).
        theta_deg (float): The h2 terminal's clearance angle in degrees as calculated in § 11,
            noting that this is the elevation angle relative to the local horizontal (degrees).
    """
    k = 4.0/3.0
    a = 6370.0 # in km
    N0 = 325.0
    theta_s_deg = ((180.0*d_km)/(pi*k*a)) + theta_eff_deg + theta_deg
    theta_s_deg = max(theta_s_deg, 0.0)
    log_f = log10(f_mhz)
    Lf = 5.0*log_f - 2.5*fpow(log_f-3.3, 2)
    Gt = 10.1*fpow(-log10(0.02*t_percent), 0.7)
    E_ts_dBuVm = 24.4 - 20.0*log10(d_km) - 10.0*theta_s_deg - Lf + 0.15*N0 + Gt
    return E_ts_dBuVm


def _d_slope_km(ha_m: float, h2_m: float, d_km: float, h_profile_mamsl: types.FloatArray|None
                ) -> float:
    """ITU-R P.1546-6, Annex 5, Section 14."""
    if h_profile_mamsl is None:
        d_slope_km = sqrt(d_km**2 + 1E-6*((ha_m-h2_m)**2))
    else:
        h_tter_m = h_profile_mamsl[0]
        h_rter_m = h_profile_mamsl[-1]
        d_slope_km = sqrt(d_km**2 + 1E-6*(((ha_m+h_tter_m)-(h2_m+h_rter_m))**2))
    return d_slope_km


def _antenna_height_diff_correction(ha_m: float, h2_m: float, d_km: float,
                                    h_profile_mamsl: types.FloatArray|None) -> float:
    """ITU-R P.1546-6, Annex 5, Section 14."""
    d_slope_km = _d_slope_km(ha_m, h2_m, d_km, h_profile_mamsl)
    correction_dB = 20.0*log10(d_km/d_slope_km)
    return correction_dB


def _fs_0_to_40m_dist(ha_m: float, h2_m: float, d_km: float, h_profile_mamsl: types.FloatArray|None
                      ) -> float:
    """ITU-R P.1546-6, Annex 5, Section 15."""
    d_slope_km = _d_slope_km(ha_m, h2_m, d_km, h_profile_mamsl)
    E_dBuVm = 106.9-20.0*log10(d_slope_km)
    return E_dBuVm


def _fs_40_to_1000m_dist(e_sup_dbuvm: float, ha_m: float, h2_m: float, d_km: float,
                         h_profile_mamsl: types.FloatArray|None) -> float:
    """ITU-R P.1546-6, Annex 5, Section 15."""
    d_slope = _d_slope_km(ha_m, h2_m, d_km, h_profile_mamsl)
    d_inf = _d_slope_km(ha_m, h2_m, 0.04, h_profile_mamsl)
    d_sup = _d_slope_km(ha_m, h2_m, 1.0, h_profile_mamsl)
    E_inf = 106.9-20.0*log10(d_inf)
    E_sup = e_sup_dbuvm
    E_dBuVm = E_inf + (E_sup-E_inf)*log10(d_slope/d_inf)/log10(d_sup/d_inf)
    return E_dBuVm


def _equivalent_basic_transmission_loss(e_dbuvm: float, f_mhz: float) -> float:
    """ITU-R P.1546-6, Annex 5, Section 17."""
    Lb_dB = 139.3 - e_dbuvm + 20.0*log10(f_mhz)
    return Lb_dB


def _D06(f_mhz: float, h1_m: float, h2_m: float) -> float:
    """
    ITU-R P.1546-6, Annex 5, Section 18.
    
    The path length (km) which just achieves a clearance of 0.6 of the first Fresnel zone over a
    smooth curved Earth, for a given frequency and antenna heights h1 and h2.
    """
    h1_m = max(h1_m, 0.0)
    Df = 0.0000389*f_mhz*h1_m*h2_m
    Dh = 4.1*(sqrt(h1_m)+sqrt(h2_m))
    D06_km = (Df*Dh)/(Df+Dh)
    D06_km = max(D06_km, 0.001)
    return D06_km


def _propagation_types(path_type_profile: types.IntArray|None) -> tuple[Path, Path|None]:
    """ITU-R P.1546-6, Annex 6, Step 1."""
    if path_type_profile is None:
        return (Path.LAND, None) # assumes LAND when no path data available
    result = []
    found_paths_int = set(path_type_profile)
    found_paths = [Path(i) for i in found_paths_int]
    if Path.LAND in found_paths:
        result.append(Path.LAND)
    if Path.COLD_SEA in found_paths and Path.WARM_SEA in found_paths:
        result.append(Path.WARM_SEA)
    elif Path.COLD_SEA in found_paths:
        result.append(Path.COLD_SEA)
    elif Path.WARM_SEA in found_paths:
        result.append(Path.WARM_SEA)
    num_types = len(result)
    if num_types == 1:
        return (result[0], None)
    elif num_types == 2:
        return (result[0], result[1])
    else:
        raise ValueError('Could not determine a proper propagation type (land, warm sea, '
                         'cold sea).')


def _fs_tables_interpolation(f_mhz: float, t_percent: float, path: Path, h1_m: float, d_km: float,
                             ha_m: float, d_profile_km: types.FloatArray,
                             h_profile_mamsl: types.FloatArray|None) -> float:
    """
    ITU-R P.1546-6, Annex 6, Steps 2 to 10.
    
    Computes field strength (dBuV/m) by interpolating/extrapolating the Recommendation's field
    strength tables.
    
    Args:
        f_mhz (float): Frequency (MHz), with 30 <= f_mhz <= 4000.
        t_percent (float): Percentage of time for which the field strength is exceeded (percent),
            with 1 <= t_percent <= 50.
        path (Path): One of LAND, COLD_SEA, WARM_SEA.
        h1_m (float): Transmitting/base antenna height (m) as of Annex 5, § 3, with h1_m <= 3000
            for land, and 1 <= h1_m <= 3000 for sea.
        d_km (float): Horizontal path length (km), with 1 <= d_km <= 1000.
        ha_m (float): Only used when h1_m is negative (Annex 5, Section 4.3).
        d_profile_km (types.FloatArray): Only used when h1_m is negative (Annex 5, Section 4.3).
        h_profile_mamsl (types.FloatArray|None): Only used when h1_m is negative (Annex 5, Section
            4.3).

    Returns:
        E (float): Field strength (dBuV/m) for 1 kW e.r.p.
    """
    return _fs_time_percentage_interpolation(f_mhz, t_percent, path, h1_m, d_km, ha_m,
                                             d_profile_km, h_profile_mamsl)


def _max_fs_mixed_path(t_percent: float, d_profile_km: types.FloatArray,
                       path_type_profile: types.IntArray|None) -> float:
    """ITU-R P.1546-6, Annex 6, Step 19."""
    d_km = d_profile_km[-1]
    E_fs = 106.9 - 20.0*log10(d_km)
    ds_km = _total_sea_distance_km(d_profile_km, path_type_profile)
    E_se = 2.38*(1.0-exp(-d_km/8.94))*log10(50.0/t_percent)
    E_max_dBuVm = E_fs + (ds_km*E_se/d_km)
    return E_max_dBuVm


def okumura_hata_field_strength(f_mhz: float, h1_m: float, h2_m: float, d_km: float) -> float:
    """
    ITU-R P.1546-6, Annex 8.

    Computes field strength using the Okumura-Hata method.

    Args:
        f_mhz (float): Frequency (MHz).
        h1_m (float): Base station effective antenna height above ground (m),
            with 30 <= h1_m <= 200.
        h2_m (float): Mobile station antenna height above ground (m), with 1 <= h2_m <= 10.
        d_km (float): Distance (km), with 0 < d_km.

    Returns:
        E (float): Field strength (dBμVm) for 1 kW e.r.p.
    """
    log_f = log10(f_mhz)
    aH2 = (1.1*log_f - 0.7)*h2_m - (1.56*log_f - 0.8)
    if d_km > 20.0:
        H1p = h1_m / sqrt(1.0 + 0.000007*h1_m*h1_m)
        b = 1.0 + (0.14 + 0.000187*f_mhz + 0.00107*H1p)*fpow(log10(0.05*d_km), 0.8)
    else:
        b = 1.0
    E = 69.82 - 6.16*log_f + 13.82*log10(h1_m) + aH2 - (44.9-6.55*log10(h1_m))*fpow(log10(d_km), b)
    return E


def _total_sea_distance_km(d_profile_km: types.FloatArray, path_type_profile: types.IntArray|None
                           ) -> float:
    if path_type_profile is None:
        return 0.0 # assumes all LAND
    ds_km = 0.0
    lops_km = _length_of_path_sections_profile_km(d_profile_km)
    for index, val in enumerate(path_type_profile):
        path = Path(val)
        if path == Path.COLD_SEA or path == Path.WARM_SEA:
            ds_km += lops_km[index]
    return ds_km


def _length_of_path_sections_profile_km(d_profile_km: types.FloatArray) -> list[float]:
    """Returns list of n items containing the length of path sections (km)"""
    n = len(d_profile_km)
    lops = []
    lops.append((d_profile_km[1]-d_profile_km[0])/2.0)
    for i in range(1, n-1):
        lops.append( (d_profile_km[i]-d_profile_km[i-1])/2.0 +
                     (d_profile_km[i+1]-d_profile_km[i])/2.0 )
    lops.append((d_profile_km[n-1]-d_profile_km[n-2])/2.0)
    return lops


def _averaged_terrain_height_m(d_profile_km: types.FloatArray, h_profile_mamsl: types.FloatArray,
                               start_dist_km, end_dist_km) -> float:
    avg_height_m = 0
    total_d_km = 0
    n = len(d_profile_km)
    for i, h_m in enumerate(h_profile_mamsl):
        start_i_km = (d_profile_km[max(i-1, 0)] + d_profile_km[i])/2.0
        if start_i_km > end_dist_km:
            break
        end_i_km = (d_profile_km[i] + d_profile_km[min(i+1, n-1)])/2.0
        if end_i_km < start_dist_km:
            continue
        instersect_start_i_km = max(start_i_km, start_dist_km)
        intersect_end_i_km = min(end_i_km, end_dist_km)
        length_i_km = intersect_end_i_km - instersect_start_i_km
        avg_height_m += h_m*length_i_km
        total_d_km += length_i_km
    avg_height_m = avg_height_m / total_d_km
    return avg_height_m


def _interpolate_h_profile(d_profile_km: types.FloatArray, h_profile_mamsl: types.FloatArray,
                           dist_km: float) -> float:
    """
    Interpolates distance & terrain height profile data so to get a terrain height (m) value at
    distance dist_km.
    """
    # Find the index of the first distance greater than interpolate_dist_km
    i = bisect_right(d_profile_km, dist_km)

    # Clamp to the valid range
    if i == 0:
        return h_profile_mamsl[0]
    if i >= len(d_profile_km):
        return h_profile_mamsl[-1]

    # Linear interpolation
    d0, d1 = d_profile_km[i-1], d_profile_km[i]
    h0, h1 = h_profile_mamsl[i-1], h_profile_mamsl[i]
    t = (dist_km-d0)/(d1-d0)
    return h0 + t*(h1-h0)


def _thread_safe_get_fs_tables() -> dict:
    """
    Gets the field strength tables as a dictionary (see _read_fs_tables()) in a thread-safe manner,
    takes care of downloading the required ITU file as necessary.
    """
    fs_tables = _p1546_6_shared['fs_tables']
    if fs_tables is not None:
        return fs_tables
    with _p1546_6_shared['fs_tables_lock']:
        fs_tables = _p1546_6_shared['fs_tables'] # re-read under lock
        if fs_tables is None:
            try:
                fs_tables = _read_fs_tables()
            except FileNotFoundError:
                _download_rec_data()
                fs_tables = _read_fs_tables()
            _p1546_6_shared['fs_tables'] = fs_tables # only assign when load completed successfully
    return fs_tables


def _read_fs_tables() -> dict:
    """
    Reads field strength tables from installed ITU .xls file. Content is stored and returned as a
    dictionary with the following format:

    Key:
        nominal_f_mhz (int): A nominal frequency (MHz), 100, 600 or 2000.
        nominal_time_p (int): A nominal time percentage (%). 50, 10 or 1.
        path_type (_Path): A path type, LAND, SEA, COLD_SEA or WARM_SEA.
        nominal_h1 (float): A nominal height value (m), 10.0, 20.0, 37.5, 75.0, 150.0, 300.0,
            600.0 or 1200.0.

    Value:
        list[float]: A list of field strength values (dBuV/m), one for each of the nominal
            distances ordered ascendingly.
    """
    fs_tables = {}

    data_dir = _p1546_6_shared['DATA_DIR']
    file_path = join(_du.install_dir(), data_dir, r'Tabulated%20field%20strength%20values.xls')

    workbook = xlrd.open_workbook(file_path)
    for sheet_index in range(0, 24):
        sheet = workbook.sheet_by_index(sheet_index)

        f_str, f_unit = sheet.cell_value(rowx=1, colx=1).split()
        nominal_f_mhz = int(f_str)
        if f_unit == 'GHz':
            nominal_f_mhz *= 1000

        nominal_time_p = int(sheet.cell_value(rowx=2, colx=1))

        path_mapping = {
            'Land': _Path.LAND,
            'Sea': _Path.SEA,
            'Cold Sea': _Path.COLD_SEA,
            'Warm Sea': _Path.WARM_SEA
        }
        path_type_str = sheet.cell_value(rowx=3, colx=1)
        path_type = path_mapping[path_type_str]

        for col_index in range(2, 10):
            nominal_h1 = float(sheet.cell_value(rowx=5, colx=col_index))
            values = sheet.col_values(colx=col_index, start_rowx=6, end_rowx=84)
            key = (nominal_f_mhz, nominal_time_p, path_type, nominal_h1)
            fs_tables[key] = values # values: list of field strength values at nominal distances

    return fs_tables


def _download_rec_data() -> None:
    """Downloads field strength tables (.xls file) from ITU website if not already installed."""
    data_dir = _p1546_6_shared['DATA_DIR']
    full_path_data_dir = join(_du.install_dir(), data_dir)
    filenames = [r'Tabulated%20field%20strength%20values.xls']
    lock = FileLock(_du.get_lockfile_pathname(data_dir))
    with lock:
        if _du.files_all_exist(full_path_data_dir, filenames) is False:
            url = r'https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Software%20Products/' \
                  r'Tabulated%20field%20strength%20values.xls'
            _du.download(url, full_path_data_dir)
            _du.print_notice()
        else:
            _du.print_already_installed(full_path_data_dir, filenames)


_p1546_6_shared = {
    'DATA_DIR': 'p1546_6',
    'fs_tables_lock': Lock(),
    'fs_tables': None,
    'nominal_heights_m': (10.0, 20.0, 37.5, 75.0, 150.0, 300.0, 600.0, 1200.0),
    'nominal_dists_km': (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,25,30,35,40,45,50,55,
                         60,65,70,75,80,85,90,95,100,110,120,130,140,150,160,170,180,190,200,225,
                         250,275,300,325,350,375,400,425,450,475,500,525,550,575,600,625,650,675,
                         700,725,750,775,800,825,850,875,900,925,950,975,1000)
}
