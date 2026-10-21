# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.2001-6.

P.2001 : A general purpose wide-range terrestrial propagation model in the frequency range 30 MHz
to 50 GHz.

https://www.itu.int/rec/R-REC-P.2001/en
"""

from os.path import join
from math import sin, cos, radians, acos, atan2, fabs, asin, degrees, atan, log10, inf, sqrt, \
                 tan, exp, pi, log as ln, ceil, tanh, floor
from enum import Enum
from warnings import warn
from typing import Callable
from types import SimpleNamespace
from threading import Lock
from array import array
from filelock import FileLock
from propakai import _download_utils as _du
from propakai import types
from propakai import p1144_13
from propakai import p838_3


__all__ = ['RadioClimaticZone',
           'basic_transmission_loss',
           'path_length',
           'bearing',
           'intermediate_path_point']


class RadioClimaticZone(Enum):
    """Documents integer values that may be used in z parameter of basic_transmission_loss()."""
    COASTAL_LAND = 3
    INLAND       = 4
    SEA          = 1


class _MapId(Enum):
    """ITU-R P.2001-6, Annex, Section 2.4. Available digital maps."""
    DN_MEDIAN        =  1
    DN_SUBSLOPE      =  2
    DN_SUPSLOPE      =  3
    DNDZ_01          =  4
    ESARAIN_BETA_V5  =  5
    ESARAIN_MT_V5    =  6
    ESARAIN_PR6_V5   =  7
    FOES0_1          =  8
    FOES01           =  9
    FOES10           =  10
    FOES50           =  11
    H0               =  12
    SURFWV_50_FIXED  =  13
    TROPOCLIM        =  14


# Constants from ITU-R P.2001-6, Annex, Section 2.3.
_C_MS = 2.998e8 # Speed of propagation (m/s)
_RE_KM = 6371.0 # Average Earth radius (km)
_EPS_R_LAND = 22.0 # Relative permittivity for land
_EPS_R_SEA = 80.0 # Relative permittivity for sea
_SIG_LAND_SM = 0.003 # Conductivity for land (S/m)
_SIG_SEA_SM = 5.0 # Conductivity for sea (S/m)


def basic_transmission_loss(f_ghz: float, tpc_percent: float,
                            latt: float, lont: float, latr: float, lonr: float,
                            htg_m: float, hrg_m: float,
                            gt_dbi: float, gr_dbi: float,
                            vpol: bool,
                            d_km: types.FloatArray, h_mamsl: types.FloatArray,
                            z: types.IntArray|None=None
                            ) -> tuple[float, float, float, float, float]:
    """
    The basic transmission loss (dB) not exceeded for tpc_percent time.

    Args:
        f_ghz (float): Frequency (GHz), with 0.03 <= f_ghz <= 50.
        tpc_percent (float): Percentage of average year for which the predicted basic transmission
            loss is not exceeded (%), with 0 <= tpc_percent <= 100.0.
        latt (float): Latitude of transmitter (degrees), with -90 <= latt <= 90.
        lont (float): Longitude of transmitter (degrees), with -180 <= lont <= 180.
        latr (float): Latitude of receiver (degrees), with -90 <= latr <= 90.
        lonr (float): Longitude of receiver (degrees), with -180 <= lonr <= 180.
        htg_m (float): Height of electrical centre of transmitting antenna above ground (m), with
            0 < htg_m <= 8000.
        hrg_m (float): Height of electrical centre of receiving antenna above ground (m), with
            0 < htg_m <= 8000.
        gt_dbi (float): Gain of transmitting antenna in the azimuthal direction of the path towards
            the other antenna, and at the elevation angle above the local horizontal of the other
            antenna in the case of a line-of-sight (LoS) path, otherwise of the antenna's radio
            horizon, for median effective Earth radius (dBi).
        gr_dbi (float): Gain of receiving antenna in the azimuthal direction of the path towards
            the other antenna, and at the elevation angle above the local horizontal of the other
            antenna in the case of a line-of-sight (LoS) path, otherwise of the antenna's radio
            horizon, for median effective Earth radius (dBi).
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.
        d_km (types.FloatArray): Distance from transmitter profile of n points along the great-
            circle radio path (km), with 3 <= n. The profile points must be spaced at equal
            intervals of distance. 
        h_mamsl (types.FloatArray): Terrain height profile of n points (m above mean sea level).
        z (types.IntArray|None, optional): Radio climatic zone profile of n points (1=Sea,
            3=Coastal Land, 4=Inland). Inland is assumed everywhere when z is set to None.

    Returns:
        Lb (float): The basic transmission loss (dB) not exceeded for tpc_percent time (dB).
        Lbm1 (float): The sub-model 1 basic transmission loss not exceeded for tpc_percent time
            (dB). Propagation close to the surface of the Earth, consisting of diffraction,
            non-ducting clear-air effects and precipitation fading.
        Lbm2 (float): The sub-model 2 basic transmission loss not exceeded for tpc_percent time
            (dB). Anomalous propagation due to stratified atmosphere, consisting of ducting and
            layer reflection.
        Lbm3 (float): The sub-model 3 basic transmission loss not exceeded for tpc_percent time
            (dB). Propagation via atmospheric turbulence, consisting of troposcatter and
            precipitation fading for the troposcatter path.
        Lbm4 (float): The sub-model 4 basic transmission loss not exceeded for tpc_percent time
            (dB). Propagation via sporadic-E reflection.
    """
    _input_validation(f_ghz, tpc_percent, htg_m, hrg_m, d_km, h_mamsl, z)

    lops = _length_of_path_sections_profile(d_km)

    # START of Preliminary Calculations (TABLE 4)

    t4 = SimpleNamespace() # to store values from TABLE 4

    # § 3.1
    t4.p, t4.q = _limited_percentage_time(tpc_percent)

    # § 3.2
    t4.d = d_km[-1] # path length (km)
    t4.phi_mn, t4.phi_me = intermediate_path_point(latt, lont, latr, lonr, t4.d*0.5)
    t4.hmid = _mid_point_ground_height(h_mamsl)
    t4.omega = _fraction_of_path_over_sea(t4.d, z, lops)

    # § 3.3
    t4.hts = h_mamsl[0] + htg_m # transmitter height (masl)
    t4.hrs = h_mamsl[-1] + hrg_m # receiver height (masl)
    t4.hhi = max(t4.hts, t4.hrs) # higher antenna height (masl)
    t4.hlo = min(t4.hts, t4.hrs) # lower antenna height (masl)
    t4.eps_p = (t4.hhi-t4.hlo)/t4.d # positive value of path inclination (mrad)

    # § 3.4.1
    t4.Nd1km50 = _N_d1km50(t4.phi_mn, t4.phi_me)
    t4.Nd1kmp = _N_d1kmp(t4.phi_mn, t4.phi_me, t4.Nd1km50, t4.p, t4.q)

    # § 3.4.2
    t4.Nd65m1 = _N_d65m1(t4.phi_mn, t4.phi_me)

    # § 3.5
    t4.ae = (157.0*_RE_KM)/(157.0+t4.Nd1km50) # median effective Earth radius (km)
    t4.cp = (157.0+t4.Nd1kmp)/(157.0*_RE_KM) # effective Earth curvature (1/km)
    t4.ap = 1.0/max(t4.cp, 1E-6) # effective Earth radius exceeded for p% time limited not to become
                                 # infinite (km)
    t4.theta_e = t4.d/t4.ae # Angle subtended by d km at centre of spherical Earth (rad)

    # § 3.6
    t4.lmbda = 1E-9*_C_MS/f_ghz # wavelength (m)

    # § 3.7
    is_los, t4.dlt, t4.dlr, t4.ilt, t4.ilr, t4.theta_t, t4.theta_r, t4.theta_tpos, t4.theta_rpos = \
        _path_and_horizon_parameters(d_km, h_mamsl, t4.hts, t4.hrs, t4.ae, t4.lmbda)

    # § 3.8
    t4.hm, t4.htea, t4.hrea, t4.htep, t4.hrep = \
        _eff_heights_and_roughness_parameters(d_km, h_mamsl, t4.hts, t4.hrs, t4.ilt, t4.ilr)

    # § 3.9
    t4.dtcv, t4.drcv, t4.hcv, t4.phi_cve, t4.phi_cvn, t4.phi_tcve, t4.phi_tcvn, t4.phi_rcve, \
    t4.phi_rcvn = _troposcatter_parameters(t4.d, latt, lont, latr, lonr, t4.hts, t4.hrs,
                                           t4.theta_e, t4.theta_tpos, t4.theta_rpos, t4.ae)

    # § 3.10
    t4.gamma_o = _gamma_o(f_ghz)
    Aosur, t4.Awsur, t4.Awrsur = _gaseous_absorption_for_surface_path(f_ghz, t4.d, t4.phi_mn,
                                                                      t4.phi_me, t4.hmid, t4.hts,
                                                                      t4.hrs, t4.gamma_o)
    t4.Agsur = Aosur + t4.Awsur

    # § 3.11
    t4.Lbfs = _free_space_basic_transmission_loss(f_ghz, t4.d, t4.hts, t4.hrs)

    # § 4.1
    t4.Lbm1 = _sub_model_1(t4, f_ghz, vpol, d_km, h_mamsl, is_los)

    # § 4.2
    t4.Lbm2 = _sub_model_2(t4, f_ghz, z, lops)

    # § 4.3
    t4.Lbm3 = _sub_model_3(t4, f_ghz, latt, lont, latr, lonr, gt_dbi, gr_dbi, vpol, h_mamsl)

    # § 4.4
    t4.Lbm4 = _sub_model_4(t4, f_ghz, latt, lont, latr, lonr)

    # END of Preliminary Calculations

    Lb = _combine_sub_models(t4.Lbm1, t4.Lbm2, t4.Lbm3, t4.Lbm4)

    return Lb, t4.Lbm1, t4.Lbm2, t4.Lbm3, t4.Lbm4


def _input_validation(f_ghz: float, tpc_percent: float, htg_m: float, hrg_m: float,
                      d_km: types.FloatArray, h_mamsl: types.FloatArray, z: types.IntArray|None
                      ) -> None:
    if f_ghz < 0.03 or f_ghz > 50.0:
        # warning to allow experimental use of out of range frequencies
        warn('f_ghz is out of range.')
    if tpc_percent < 0.0 or tpc_percent > 100.0:
        raise ValueError('tpc_percent is out of range.')
    if htg_m <= 0.0 or htg_m > 8000.0:
        raise ValueError('htg_m is out of range.')
    if hrg_m <= 0.0 or hrg_m > 8000.0:
        raise ValueError('hrg_m is out of range.')
    n = len(d_km)
    if n < 3:
        raise ValueError('d_km must contain at least 3 distances.')
    if len(h_mamsl) != n:
        raise ValueError('Unexpected number of items in h_mamsl.')
    if z is not None:
        if len(z) != n:
            raise ValueError('Unexpected number of items in z.')


def _length_of_path_sections_profile(d_km: types.FloatArray) -> list[float]:
    """
    Args:
        d_km (types.FloatArray): Distance from transmitter profile of n points (km).

    Returns:
        lops (list[float]): Length of path sections of n points (km).
    """
    n = len(d_km)
    lops = [(d_km[1] - d_km[0]) / 2.0]
    for i in range(1, n-1):
        lops.append((d_km[i] - d_km[i-1]) / 2.0 + (d_km[i+1] - d_km[i]) / 2.0)
    lops.append((d_km[n-1] - d_km[n-2]) / 2.0)
    return lops


def _init_digital_maps_params() -> dict:
    """ITU-R P.2001-6, Annex, Section 2.4."""
    bilinear = p1144_13.square_grid_bilinear_interpolation
    nearest = p1144_13.nearest_neighbor_interpolation
    maps_params = {
        _MapId.DN_MEDIAN: ('DN_Median.txt', 90.0, 1.5, 121, 0.0, 1.5, 241, bilinear),
        _MapId.DN_SUPSLOPE: ('DN_SupSlope.txt', 90.0, 1.5, 121, 0.0, 1.5, 241, bilinear),
        _MapId.DN_SUBSLOPE: ('DN_SubSlope.txt', 90.0, 1.5, 121, 0.0, 1.5, 241, bilinear),
        _MapId.DNDZ_01: ('dndz_01.txt', 90.0, 1.5, 121, 0.0, 1.5, 241, bilinear),
        _MapId.ESARAIN_PR6_V5: ('Esarain_Pr6_v5.txt', 90.0, 1.125, 161, 0.0, 1.125, 321, bilinear),
        _MapId.ESARAIN_MT_V5: ('Esarain_Mt_v5.txt', 90.0, 1.125, 161, 0.0, 1.125, 321, bilinear),
        _MapId.ESARAIN_BETA_V5: ('Esarain_Beta_v5.txt', 90.0, 1.125, 161, 0.0, 1.125, 321,bilinear),
        _MapId.H0: ('h0.txt', 90.0, 1.5, 121, 0.0, 1.5, 241, bilinear),
        _MapId.SURFWV_50_FIXED: ('Surfwv_50_fixed.txt', 90.0, 1.5, 121, 0.0, 1.5, 241, bilinear),
        _MapId.FOES50: ('FoEs50.txt', 90.0, 1.5, 121, 0.0, 1.5, 241, bilinear),
        _MapId.FOES10: ('FoEs10.txt', 90.0, 1.5, 121, 0.0, 1.5, 241, bilinear),
        _MapId.FOES01: ('FoEs01.txt', 90.0, 1.5, 121, 0.0, 1.5, 241, bilinear),
        _MapId.FOES0_1: ('FoEs0.1.txt', 90.0, 1.5, 121, 0.0, 1.5, 241, bilinear),
        _MapId.TROPOCLIM: ('TropoClim.txt', 89.75, 0.5, 360, -179.75, 0.5, 720, nearest)

    }
    return maps_params


def _digital_map_value(map_id: _MapId, lat: float, lon: float) -> float:
    """ITU-R P.2001-6, Annex, Section 2.4."""
    params = _p2001_6_shared['digital_maps_params'][map_id]
    return _interpolate_digital_map(lat, lon, *params)


def _interpolate_digital_map(lat: float, lon: float, filename: str,
                             first_row_lat: float, lat_spacing: float, num_rows: int,
                             first_col_lon: float, lon_spacing: float, num_cols: int,
                             interpolation_func: Callable) -> float:
    """ITU-R P.2001-6, Annex, Section 2.4."""
    if lon < 0 and first_col_lon >= 0:
        lon += 360
    r = (first_row_lat - lat) / lat_spacing
    c = (lon - first_col_lon) / lon_spacing
    arr = _thread_safe_get_digital_map_array(filename)
    return interpolation_func(arr, num_rows, num_cols, r, c)


def _limited_percentage_time(tpc_percent: float) -> tuple[float, float]:
    """ITU-R P.2001-6, Annex, Section 3.1."""
    p = tpc_percent + 0.00001*((50.0-tpc_percent)/50.0)
    q = 100.0 - p
    return p, q


def _mid_point_ground_height(h_mamsl: types.FloatArray) -> float:
    """ITU-R P.2001-6, Annex, Section 3.2."""
    n = len(h_mamsl)
    if n % 2 == 1: # if n is odd
        # extra -1 to account for zero-based array while the rec. is 1-based
        hmid = h_mamsl[((n+1)//2) -1]
    else: # n is even
        # extra -1 as well for same reason
        hmid = 0.5 * (h_mamsl[(n//2) -1] + h_mamsl[(n//2)])
    return hmid


def _fraction_of_path_over_sea(d: float, z: types.IntArray|None, lops: list[float]) -> float:
    """
    ITU-R P.2001-6, Annex, Section 3.2.

    Args:
        d (float): Great-circle path distance between transmit and receive antennas (km).
        z (types.IntArray|None): Radio climatic zone profile of n points (1=Sea, 3=Coastal Land,
            4=Inland). Inland is assumed everywhere when z is set to None.
        lops (list[float]): Length of path sections profile of n points (km).

    Returns:
        omega (float): Fraction of the total path over sea, omega, from 0 to 1.
    """
    n = len(lops)
    d_total_sea_km = 0.0  # aggregate length of the path sections over sea (km)
    water_section_count = 0

    if z is not None:
        for i in range(n):
            if z[i] == RadioClimaticZone.SEA.value:
                d_total_sea_km += lops[i]
                water_section_count += 1

    if water_section_count == n:
        omega = 1.0  # to make sure omega is set to exactly 1.0
    else:
        omega = d_total_sea_km / d

    return omega


def _N_d1km50(lat: float, lon: float) -> float:
    """
    ITU-R P.2001-6, Annex, Section 3.4.1.

    The median value of average refractivity gradient in the lowest 1 km of the atmosphere
    (N-Units). Numerically equal to delta N as defined in ITU-R P.452 but with opposite sign.
    """
    delta_N = _digital_map_value(_MapId.DN_MEDIAN, lat, lon)
    return -delta_N


def _N_d1kmp(lat: float, lon: float, nd1km50: float, p: float, q: float) -> float:
    """
    ITU-R P.2001-6, Annex, Section 3.4.1.

    Average refractivity gradient in the lowest 1 km of the atmosphere exceeded for p% of an
    average year (N-Units). Normally negative but can be zero or positive.
    """
    if p < 50:
        SdNsup = _digital_map_value(_MapId.DN_SUPSLOPE, lat, lon)
        Ndkmp = nd1km50 + SdNsup * log10(0.02*p)
    else:
        SdNsub = _digital_map_value(_MapId.DN_SUBSLOPE, lat, lon)
        Ndkmp = nd1km50 - SdNsub * log10(0.02*q)
    return Ndkmp


def _N_d65m1(lat, lon) -> float:
    """
    ITU-R P.2001-6, Annex, Section 3.4.2.

    Refractivity gradient in the lowest 65 m of the atmosphere exceeded for 1% of an average year
    (N-Units).
    """
    return _digital_map_value(_MapId.DNDZ_01, lat, lon)


def _path_and_horizon_parameters(d_km: types.FloatArray, h_mamsl: types.FloatArray,
                                 hts: float, hrs: float, ae: float, lmbda: float
                            ) -> tuple[bool, float, float, int, int, float, float, float, float]:
    """
    ITU-R P.2001-6, Annex, Section 3.7.

    Path classification and terminal horizon parameters.

    Args:
        d_km (types.FloatArray): Distance from transmitter profile of n points along the great-
            circle radio path (km), with 3 <= n. The profile points must be spaced at equal
            intervals of distance. 
        h_mamsl (types.FloatArray): Terrain height profile of n points (m above mean sea level).
        hts (float): Transmitter height (mamsl).
        hrs (float): Receiver height (mamsl).
        ae (float): Median effective Earth radius (km).
        lmbda (float): Wavelength (m).
    
    Returns:
        is_los (bool): Wether the path is Los or NLoS.
        dlt (float): Transmitter to horizon distance (km). For LoS paths, set to distance to
            point with largest knife-edge loss.
        dlr (float): Receiver to horizon distance (km). For LoS paths, set to distance to
            point with largest knife-edge loss.
        ilt (int): Profile index of transmitter horizon. (zero-based)
        ilr (int): Profile index of receiver horizon. (zero-based)
        theta_t (float): Horizon elevation angle relative to the local horizontal as viewed from
            transmitter (mrad).
        theta_r (float): Horizon elevation angle relative to the local horizontal as viewed from
            receiver (mrad).
        theta_tpos (mrad): theta_t limited to be positive (not less than zero) (mrad).
        theta_rpos (mrad): theta_r limited to be positive (not less than zero) (mrad).
    """
    n = len(d_km)
    d = d_km[-1]
    im = 0
    dim = 0

    theta_tim = -inf
    for i in range(1, n-1): # excludes transmit and receive locations
        hi = h_mamsl[i]
        di = d_km[i]
        theta_ti = (hi-hts)/di - 500.0*di/ae
        if theta_ti > theta_tim:
            theta_tim = theta_ti
            im = i
            dim = di

    theta_tr = (hrs-hts)/d - 500.0*d/ae

    if theta_tim < theta_tr:
        # Case 1. Path is LoS
        is_los = True
        vmax = -inf
        im = 0
        dim = 0
        for i in range(1, n-1):  # excludes transmit and receive locations
            hi = h_mamsl[i]
            di = d_km[i]
            vi = (hi + 500*di*(d-di)/ae - (hts*(d-di)+hrs*di)/d) * sqrt(0.002*d/(lmbda*di*(d-di)))
            if vi > vmax:
                vmax = vi
                im = i
                dim = di
        dlt = dim
        dlr = d - dim
        ilt = im
        ilr = im
        theta_t = theta_tr
        theta_r = -theta_tr - 1000.0*d/ae

    else:
        # Case 2. Path is NLoS
        is_los = False
        dlt = dim
        ilt = im
        theta_t = theta_tim
        theta_rim = -inf
        for i in range(1, n-1):  # excludes transmit and receive locations
            hi = h_mamsl[i]
            di = d_km[i]
            theta_ri = (hi-hrs)/(d-di) - 500*(d-di)/ae
            if theta_ri > theta_rim:
                theta_rim = theta_ri
                im = i
                dim = di
        dlr = d-dim
        ilr = im
        theta_r = theta_rim

    theta_tpos = max(theta_t, 0.0)
    theta_rpos = max(theta_r, 0.0)

    return is_los, dlt, dlr, ilt, ilr, theta_t, theta_r, theta_tpos, theta_rpos


def _eff_heights_and_roughness_parameters(d_km: types.FloatArray, h_mamsl: types.FloatArray,
                                          hts: float, hrs: float, ilt: int, ilr: int
                                          ) -> tuple[float, float, float, float, float]:
    """
    ITU-R P.2001-6, Annex, Section 3.8.
    
    Effective heights and path roughness parameter.

    Args:
        d_km (types.FloatArray): Distance from transmitter profile of n points along the great-
            circle radio path (km), with 3 <= n. The profile points must be spaced at equal
            intervals of distance. 
        h_mamsl (types.FloatArray): Terrain height profile of n points (m above mean sea level).
        hts (float): Transmitter height (mamsl).
        hrs (float): Receiver height (mamsl).
        ilt (int): Profile index of transmitter horizon. (zero-based)
        ilr (int): Profile index of receiver horizon. (zero-based)

    Returns:
        hm (float): Path roughness parameter (m).
        htea (float): Effective transmitter height above smooth surface for anomalous (ducting/
            layer-reflection) model (m).
        hrea (float): Effective receiver height above smooth surface for anomalous (ducting/
            layer-reflection) model (m).
        htep (float): Effective transmitter height above smooth surface for diffraction model (m).
        hrep (float): Effective receiver, heights above smooth surface for diffraction model (m).
    """
    n = len(d_km)
    d = d_km[-1]
    v1 = v2 = 0
    for i in range(1, n):
        di = d_km[i]
        dim1 = d_km[i-1]
        hi = h_mamsl[i]
        him1 = h_mamsl[i-1]
        v1 += (di-dim1)*(hi+him1)
        v2 += (di-dim1)*(hi*(2*di+dim1)+him1*(di+2*dim1))
    h_stip = (2*v1*d-v2)/(d*d)
    h_srip = (v2-v1*d)/(d*d)

    h1 = h_mamsl[0]
    hn = h_mamsl[-1]
    h_stipa = min(h_stip, h1)
    h_sripa = min(h_srip, hn)
    m_ses = (h_sripa-h_stipa)/d
    h_tea = hts-h_stipa
    h_rea = hrs-h_sripa

    hm = -inf
    for i in range(ilt, ilr+1):
        hi = h_mamsl[i]
        di = d_km[i]
        hmi = hi-(h_stipa+m_ses*di)
        hm = max(hm, hmi)

    h_obs = alpha_obt = alpha_obr = -inf
    for i in range(1, n-1):
        di = d_km[i]
        hi = h_mamsl[i]
        Hi = hi-(hts*(d-di)+hrs*di)/d
        h_obs = max(h_obs, Hi)
        alpha_obt = max(alpha_obt, Hi/di)
        alpha_obr = max(alpha_obr, Hi/(d-di))

    if h_obs <= 0:
        h_st = h_stip
        h_sr = h_srip
    else:
        gt = alpha_obt/(alpha_obt+alpha_obr)
        gr = alpha_obr/(alpha_obt+alpha_obr)
        h_st = h_stip-h_obs*gt
        h_sr = h_srip-h_obs*gr

    if h_st > h1:
        h_st = h1
    if h_sr > hn:
        h_sr = hn
    h_tep = hts-h_st
    h_rep = hrs-h_sr

    return hm, h_tea, h_rea, h_tep, h_rep


def _troposcatter_parameters(d: float, latt: float, lont: float, latr: float, lonr: float,
                             hts: float, hrs: float, theta_e: float, theta_tpos: float,
                             theta_rpos: float, ae: float
                        ) -> tuple[float, float, float, float, float, float, float, float, float]:
    """
    ITU-R P.2001-6, Annex, Section 3.9.
    
    Tropospheric-scatter path segments.

    Args:
        d (float): Path length (km).
        latt (float): Latitude of transmitter (degrees), with -90 <= latt <= 90.
        lont (float): Longitude of transmitter (degrees), with -180 <= lont <= 180.
        latr (float): Latitude of receiver (degrees), with -90 <= latr <= 90.
        lonr (float): Longitude of receiver (degrees), with -180 <= lonr <= 180.
        hts (float): Transmitter height (mamsl).
        hrs (float): Receiver height (mamsl).
        theta_e (float): Angle subtended by d km at centre of spherical Earth (rad).
        theta_tpos (float): Horizon elevation angle relative to the local horizontal as viewed from
            transmitter and limited to be positive (mrad).
        theta_rpos (float): Horizon elevation angle relative to the local horizontal as viewed from
            receiver and limited to be positive (mrad).
        ae (float): Median effective Earth radius (km).

    Returns:
        dtcv (float): Transmitter to troposcatter common volume distance (km).
        drcv (float): Receiver to troposcatter common volume distance (km).
        hcv (float): Height of troposcatter common volume (mamsl).
        phi_cve (float): Troposcatter common volume longitude (degrees).
        phi_cvn (float): Troposcatter common volume latitude (degrees).
        phi_tcve (float): Longitude of mid-point of path segment from transmitter to the
            troposcatter common volume (degrrees).
        phi_tcvn (float): Latitude of mid-point of path segment from transmitter to the
            troposcatter common volume (degrees).
        phi_rcve (float): Longitude of mid-point of path segment from receiver to the troposcatter
            common volume (degrees).
        phi_rcvn (float): Latitude, of mid-point of path segment from receiver to the troposcatter
            common volume degrees).
    """
    tan_rpos = tan(0.001*theta_rpos+0.5*theta_e)
    num = d*tan_rpos-0.001*(hts-hrs)
    denom = tan(0.001*theta_tpos+0.5*theta_e)+tan_rpos
    d_tcv = num/denom
    d_tcv = max(d_tcv, 0.0)
    d_tcv = min(d_tcv, d)
    d_rcv = d-d_tcv

    phi_cvn, phi_cve = intermediate_path_point(latt, lont, latr, lonr, d_tcv)
    h_cv = hts + 1000*d_tcv*tan(0.001*theta_tpos) + 1000*d_tcv*d_tcv/(2*ae)
    phi_tcvn, phi_tcve = intermediate_path_point(latt, lont, latr, lonr, 0.5*d_tcv)
    phi_rcvn, phi_rcve = intermediate_path_point(latt, lont, latr, lonr, d-0.5*d_rcv)

    return d_tcv, d_rcv, h_cv, phi_cve, phi_cvn, phi_tcve, phi_tcvn, phi_rcve, phi_rcvn


def _free_space_basic_transmission_loss(f: float, d: float, hts: float, hrs: float) -> float:
    """
    ITU-R P.2001-6, Annex, Section 3.11.

    Args:
        f (float): Frequency (GHz).
        d (float): Path length (km).
        hts (float): Transmitter height (mamsl).
        hrs (float): Receiver height (mamsl).

    Retruns:
        Lbfs (float): Free-space basic transmission loss (dB).
    """
    delta_h = (hts-hrs)/1000.0
    dfs = sqrt(d*d + delta_h*delta_h)
    Lbfs = 92.4 + 20.0*log10(f) + 20.0*log10(dfs)
    return Lbfs


def _J(v) -> float:
    """
    ITU-R P.2001-6, Annex, Section 3.12.
    
    Knife-edge diffraction loss (dB).
    """
    Jv = 0.0
    if v > -0.78:
        Jv = 6.9 + 20.0*log10(sqrt((v-0.1)**2 + 1.0) + v - 0.1)
    return Jv


def _sub_model_1(t4: SimpleNamespace, f: float, vpol: bool, d_km: types.FloatArray,
                 h_mamsl: types.FloatArray, is_los: bool) -> float:
    """
    ITU-R P.2001-6, Annex, Section 4.1.

    Sub-model 1. Propagation close to the surface of the Earth, consisting of diffraction,
    non-ducting clear-air effects and precipitation fading.

    Args:
        t4 (SimpleNamespace): Computed values from the recommendation's TABLE 4.
        f (float): Frequency (GHz).
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.
        d_km (types.FloatArray): Distance from transmitter profile of n points along the great-
            circle radio path (km), with 3 <= n. The profile points must be spaced at equal
            intervals of distance. 
        h_mamsl (types.FloatArray): Terrain height profile of n points (m above mean sea level).
        is_los (bool): Whether the path is LoS or NLoS for median time, as determined by § 3.7.

    Returns:
        Lbm1 (float): Sub-model 1 basic transmission loss not exceeded for p% time (dB).
    """
    Ld = _diffraction_loss(f, t4.lmbda, vpol, d_km, h_mamsl, t4.ap, t4.cp, t4.omega, t4.hts,
                           t4.hrs, t4.htep, t4.hrep)

    Q0ca = _Q0ca(is_los, f, t4.d, t4.hlo, t4.eps_p, t4.Nd65m1, t4.phi_mn, t4.dlt, t4.dlr, t4.hts,
                 t4.hrs, h_mamsl, t4.ilt, t4.ilr, t4.theta_t, t4.theta_r)

    is_rain_path, a, b, c, dr, Q0ra, kmod, alpha_mod, G, P, Fwvr = \
        _precipitation_fading_preleminary_calculations(f=f, q=t4.q, phi_n=t4.phi_mn,
                            phi_e=t4.phi_me, hrainlo=t4.hlo, hrainhi=t4.hhi, drain=t4.d, vpol=vpol)

    def _Qiter(A: float) -> float:
        Qcaf = _Qcaf(A, Q0ca)
        Qrain = _Qrain(A, is_rain_path, a, b, c, dr, kmod, alpha_mod, G, P)
        return Qrain*(Q0ra/100) + Qcaf*(1-Q0ra/100)

    A1 = _Aiter(t4.q, _Qiter)

    Lbm1 = t4.Lbfs + Ld + A1 + Fwvr*(t4.Awrsur-t4.Awsur) + t4.Agsur

    return Lbm1


def _sub_model_2(t4: SimpleNamespace, f: float, z: types.IntArray|None, lops: list[float]) -> float:
    """
    ITU-R P.2001-6, Annex, Section 4.2.
    
    Sub-model 2. Anomalous propagation due to stratified atmosphere, consisting of ducting and
    layer reflection.

    Args:
        t4 (SimpleNamespace): Computed values from the recommendation's TABLE 4.
        f (float): Frequency (GHz).
        z (types.IntArray|None): Radio climatic zone profile of n points (1=Sea, 3=Coastal Land,
            4=Inland). Inland is assumed everywhere when z is set to None.
        lops (list[float]): Length of path sections profile of n points (km).

    Returns:
        Lbm2 (float): basic transmission loss not exceeded for p% time due to anomalous propagation
            (dB).
    """
    beta0, tau = _point_incidence_of_ducting(t4.d, t4.phi_mn, z, lops) # D.2
    Ast, Asr = _site_shielding_losses(f, t4.dlt, t4.dlr, t4.theta_t, t4.theta_r) # D.3
    Act, Acr = _over_sea_surface_duct_coupling_corrections(t4.d, z, lops, t4.omega, t4.dlt, t4.dlr,
                                                           t4.hts, t4.hrs) # D.4
    Aac = _total_coupling_loss(f, t4.dlt, t4.dlr, t4.omega, Ast, Asr, Act, Acr) # D.5
    Aad = _angular_distance_dependent_loss(f, t4.d, t4.ae, t4.dlt, t4.dlr, t4.theta_t,
                                           t4.theta_r) # D.6
    Aat = _distance_and_time_dependent_loss(t4.p, t4.q, t4.d, beta0, tau, t4.hm, t4.htea, t4.hrea,
                                            t4.ae, t4.dlt, t4.dlr) # D.7
    Lba = Aac + Aad + Aat # D.8
    Lbm2 = Lba + t4.Agsur
    return Lbm2


def _sub_model_3(t4: SimpleNamespace, f: float, latt: float, lont: float, latr: float, lonr: float,
                 gt: float, gr: float, vpol: bool, h_mamsl: types.FloatArray) -> float:
    """
    ITU-R P.2001-6, Annex, Section 4.3.

    Sub-model 3. Propagation via atmospheric turbulence, consisting of troposcatter and
    precipitation fading for the troposcatter path.

    Args:
        t4 (SimpleNamespace): Computed values from the recommendation's TABLE 4.
        f (float): Frequency (GHz).
        latt (float): Latitude of transmitter (degrees).
        lont (float): Longitude of transmitter (degrees).
        latr (float): Latitude of receiver (degrees).
        lonr (float): Longitude of receiver (degrees).
        gt (float): Gain of transmitting antenna in the azimuthal direction of the path towards
            the other antenna, and at the elevation angle above the local horizontal of the other
            antenna in the case of a line-of-sight (LoS) path, otherwise of the antenna's radio
            horizon, for median effective Earth radius (dBi).
        gr (float): Gain of receiving antenna in the azimuthal direction of the path towards
            the other antenna, and at the elevation angle above the local horizontal of the other
            antenna in the case of a line-of-sight (LoS) path, otherwise of the antenna's radio
            horizon, for median effective Earth radius (dBi).
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.
        h_mamsl (types.FloatArray): Terrain height profile of n points (m above mean sea level).

    Returns:
        Lbm3 (float): The sub-model 3 basic transmission loss not exceeded for p% time (dB).
    """
    Lbs = _troposcatter_basic_transmission_loss(f, t4.d, t4.p, latt, lont, latr, lonr, t4.phi_cvn,
                                                t4.phi_cve, t4.ae, t4.theta_e, t4.theta_t,
                                                t4.theta_r, gt, gr, t4.Lbfs)

    is_rain_path, a, b, c, dr, Q0ra, kmod, alpha_mod, G, P, Fwvrtx = \
        _precipitation_fading_preleminary_calculations(f=f, q=t4.q, phi_n=t4.phi_tcvn,
                        phi_e=t4.phi_tcve, hrainlo=t4.hts, hrainhi=t4.hcv, drain=t4.dtcv, vpol=vpol)

    def _Qiter_tx(A: float) -> float:
        Qrain = _Qrain(A, is_rain_path, a, b, c, dr, kmod, alpha_mod, G, P)
        Qcaftropo = _Qcaftropo(A)
        return Qrain*(Q0ra/100) + Qcaftropo*(1-Q0ra/100)

    A2t = _Aiter(t4.q, _Qiter_tx)

    is_rain_path, a, b, c, dr, Q0ra, kmod, alpha_mod, G, P, Fwvrrx = \
        _precipitation_fading_preleminary_calculations(f=f, q=t4.q, phi_n=t4.phi_rcvn,
                        phi_e=t4.phi_rcve, hrainlo=t4.hrs, hrainhi=t4.hcv, drain=t4.drcv, vpol=vpol)

    def _Qiter_rx(A: float) -> float:
        Qrain = _Qrain(A, is_rain_path, a, b, c, dr, kmod, alpha_mod, G, P)
        Qcaftropo = _Qcaftropo(A)
        return Qrain*(Q0ra/100) + Qcaftropo*(1-Q0ra/100)

    A2r = _Aiter(t4.q, _Qiter_rx)

    A2 = (A2t*(1+0.018*t4.dtcv)+A2r*(1+0.018*t4.drcv))/(1+0.018*t4.d)

    Aos, Aws, Awrs = _gaseous_absorption_for_troposcatter_path(f, latt, lont, latr, lonr, h_mamsl,
                                        t4.theta_tpos, t4.theta_rpos, t4.dtcv, t4.drcv, t4.gamma_o)

    Ags = Aos + Aws

    Lbm3 = Lbs + A2 + 0.5*(Fwvrtx+Fwvrrx)*(Awrs-Aws) + Ags

    return Lbm3


def _sub_model_4(t4: SimpleNamespace, f: float, latt: float, lont: float, latr: float, lonr: float
                 ) -> float:
    """
    ITU-R P.2001-6, Annex, Section 4.4.

    Sub-model 4. Propagation via sporadic-E reflection.

    Args:
        t4 (SimpleNamespace): Computed values from the recommendation's TABLE 4.
        f (float): Frequency (GHz).
        latt (float): Latitude of transmitter (degrees).
        lont (float): Longitude of transmitter (degrees).
        latr (float): Latitude of receiver (degrees).
        lonr (float): Longitude of receiver (degrees).
    
    Returns:
        Lbm4 (float): Basic transmission loss not exceeded for p% time due to sporadic-E scatter
            (dB).
    """
    LbEs1 = _sporadic_E_1_hop_basic_transmission_loss(f, t4.d, t4.p, t4.phi_mn, t4.phi_me, t4.ae,
                                                      t4.dlt, t4.dlr, t4.theta_t, t4.theta_r)
    LbEs2 = _sporadic_E_2_hop_basic_transmission_loss(f, t4.d, t4.p, latt, lont, latr, lonr, t4.ae,
                                                      t4.dlt, t4.dlr, t4.theta_t, t4.theta_r)
    Lbe = _sporadic_E_basic_transmission_loss(LbEs1, LbEs2)
    Lbm4 = Lbe
    return Lbm4


def _combine_sub_models(lbm1: float, lbm2: float, lbm3: float, lbm4: float) -> float:
    """
    ITU-R P.2001-6, Annex, Sections 5.1, 5.2.
    """
    Lm = min(lbm1, lbm2)
    Lbm12 = Lm-10*log10(pow(10, -0.1*(lbm1-Lm))+pow(10, -0.1*(lbm2-Lm)))
    Lb = Lm-5*log10(pow(10, -0.2*(Lbm12-Lm))+pow(10, -0.2*(lbm3-Lm))+pow(10, -0.2*(lbm4-Lm)))
    return Lb


def _diffraction_loss(f: float, lmbda: float, vpol: bool, d_km: types.FloatArray,
                      h_mamsl: types.FloatArray, ap: float, cp: float, omega: float,
                      hts: float, hrs: float, htep: float, hrep: float) -> float:
    """
    ITU-R P.2001-6, Attachment A (A.1).

    Args:
        f (float): Frequency (GHz).
        lmbda (float): Wavelength (m).
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.
        d_km (types.FloatArray): Distance from transmitter profile of n points along the great-
            circle radio path (km), with 3 <= n. The profile points must be spaced at equal
            intervals of distance. 
        h_mamsl (types.FloatArray): Terrain height profile of n points (m above mean sea level).
        ap (float): Effective Earth radius exceeded for p% time limited not to become infinite (km).
        cp (float): Effective Earth curvature (1/km).
        omega (float): Fraction of the total path over sea.
        hts (float): Transmitter height (mamsl).
        hrs (float): Receiver height (mamsl).
        htep (float): Effective transmitter height above smooth surface for diffraction model (m).
        hrep (float): Effective receiver, heights above smooth surface for diffraction model (m).

    Returns:
        Ld (float): Diffraction loss not exceeded for p% time (dB).
    """
    d = d_km[-1]
    Ldsph = _spherical_earth_diffraction_loss(f, lmbda, vpol, d, ap, omega, htep, hrep)
    Ldba = _bullington_diffraction_loss(lmbda, d_km, h_mamsl, cp, hts, hrs)
    Ldbs = _bullington_diffraction_loss_for_smooth_profile(lmbda, d_km, ap, htep, hrep)
    Ld = Ldba + max(Ldsph-Ldbs, 0.0)
    return Ld


def _spherical_earth_diffraction_loss(f: float, lmbda: float, vpol: bool, d: float, ap: float,
                                      omega: float, htep: float, hrep: float) -> float:
    """
    ITU-R P.2001-6, Attachment A (A.2).

    Args:
        f (float): Frequency (GHz).
        lmbda (float): Wavelength (m).
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.
        d (float): Path length (km).
        ap (float): Effective Earth radius exceeded for p% time limited not to become infinite (km).
        omega (float): Fraction of the total path over sea.
        htep (float): Effective transmitter height above smooth surface for diffraction model (m).
        hrep (float): Effective receiver, heights above smooth surface for diffraction model (m).

    Returns:
        Ldsph (float: The spherical-Earth diffraction loss not exceeded for p% time (dB).
    """
    dlos = sqrt(2*ap)*(sqrt(0.001*htep)+sqrt(0.001*hrep))
    if d >= dlos:
        Ldsph = _first_term_spherical_earth_diffraction_loss(f, vpol, d, ap, omega, htep, hrep)
    else:
        msph = 250*d*d/(ap*(htep+hrep))
        csph = (htep-hrep)/(htep+hrep)
        bsph = 2*sqrt((msph+1)/(3*msph))*cos(pi/3 + 1/3*acos(3*csph/2*sqrt(3*msph/pow(msph+1, 3))))
        d1 = (d/2)*(1+bsph)
        d2 = d-d1
        hsph = ((htep-500*d1*d1/ap)*d2 + (hrep-500*d2*d2/ap)*d1)/d
        hreq = 17.456*sqrt(d1*d2*lmbda/d)
        if hsph > hreq:
            Ldsph = 0.0
        else:
            aem = 500*(d/(sqrt(htep)+sqrt(hrep)))**2
            Ldft = Ldsph = _first_term_spherical_earth_diffraction_loss(f, vpol, d, aem, omega,
                                                                        htep, hrep)
            if Ldft < 0.0:
                Ldsph = 0.0
            else:
                Ldsph = (1-(hsph/hreq))*Ldft
    return Ldsph


def _first_term_spherical_earth_diffraction_loss(f: float, vpol: bool, d: float, adft: float,
                                                 omega: float, htep: float, hrep: float) -> float:
    """
    ITU-R P.2001-6, Attachment A (A.3).

    Args:
        f (float): Frequency (GHz).
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.
        d (float): Path length (km).
        adft (float): Effective Earth radius (km).
        omega (float): Fraction of the total path over sea.
        htep (float): Effective transmitter height above smooth surface for diffraction model (m).
        hrep (float): Effective receiver, heights above smooth surface for diffraction model (m).

    Returns:
        Ldft (float): First term spherical Earth diffraction loss (dB).
    """
    Ldft_land = 0.0
    Ldft_sea = 0.0
    if omega != 1.0:
        Ldft_land = _first_term_sub_calculation(f, vpol, d, adft, _EPS_R_LAND, _SIG_LAND_SM, htep,
                                                hrep)
    if omega != 0.0:
        Ldft_sea = _first_term_sub_calculation(f, vpol, d, adft, _EPS_R_SEA, _SIG_SEA_SM, htep,
                                               hrep)
    Ldft = omega*Ldft_sea + (1.0-omega)*Ldft_land
    return Ldft


def _first_term_sub_calculation(f: float, vpol: bool, d: float, adft: float, eps_r: float,
                                sigma: float, htep: float, hrep: float) -> float:
    """
    ITU-R P.2001-6, Attachment A (A.3).

    Args:
        f (float): Frequency (GHz).
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.
        d (float): Path length (km).
        adft (float): Effective Earth radius (km).
        eps_r (float): Terrain relative permittivity.
        sigma (float): Terrain conductivity (S/m).
        htep (float): Effective transmitter height above smooth surface for diffraction model (m).
        hrep (float): Effective receiver, heights above smooth surface for diffraction model (m).

    Returns:
        Ldft (float): First term spherical Earth diffraction loss (dB).
    """
    K = 0.036*pow(adft*f, -1.0/3.0) * pow(pow(eps_r-1.0, 2) + pow(18.0*sigma/f, 2), -0.25)
    if vpol:
        K *= sqrt(pow(eps_r, 2) + pow(18.0*sigma/f, 2))

    K2 = K*K
    K4 = K2*K2
    beta = (1.0+1.6*K2+0.67*K4)/(1.0+4.5*K2+1.53*K4)

    X = 21.88*beta*pow(f/(adft*adft), 1.0/3.0)*d

    Yt = Yr = 0.9575*beta*pow(f*f/adft, 1.0/3.0)
    Yt *= htep
    Yr *= hrep

    if X >= 1.6:
        FX = 11.0 + 10.0*log10(X) - 17.6*X
    else:
        FX = -20.0*log10(X) - 5.6488*pow(X, 1.425)

    def _G(y: float) -> float:
        B = beta*y
        if B > 2:
            GY = 17.6*sqrt(B-1.1) - 5.0*log10(B-1.1) - 8.0
        else:
            GY = 20.0*log10(B + 0.1*B*B*B)
        return max(GY, 2.0 + 20.0*log10(K))

    Ldft = -FX - _G(Yt) - _G(Yr)

    return Ldft


def _bullington_diffraction_loss(lmbda: float, d_km: types.FloatArray, h_mamsl: types.FloatArray,
                                 cp: float, hts: float, hrs: float) -> float:
    """
    ITU-R P.2001-6, Attachment A (A.4).

    Args:
        lmbda (float): Wavelength (m).
        d_km (types.FloatArray): Distance from transmitter profile of n points along the great-
            circle radio path (km), with 3 <= n. The profile points must be spaced at equal
            intervals of distance. 
        h_mamsl (types.FloatArray): Terrain height profile of n points (m above mean sea level).
        cp (float): Effective Earth curvature (1/km).
        hts (float): Transmitter height (mamsl).
        hrs (float): Receiver height (mamsl).

    Returns:
        Ldba (float): The Bullington diffraction loss for the actual path profile (dB).
    """
    n = len(d_km)
    d = d_km[-1]

    Stim = -inf
    for i in range(1, n-1):
        di = d_km[i]
        hi = h_mamsl[i]
        Stim = max(Stim, (hi + 500.0*cp*di*(d-di)-hts)/di)
    Str = (hrs-hts)/d

    if Stim < Str:
        # Case 1. Path is LoS for effective Earth curvature not exceeded for p% time
        vamax = -inf
        for i in range(1, n-1):
            di = d_km[i]
            hi = h_mamsl[i]
            vamax = max(vamax, (hi + 500.0*cp*di*(d-di) - (hts*(d-di)+hrs*di)/d)
                        *sqrt(0.002*d/(lmbda*di*(d-di))))
        Ldbka = _J(vamax)
    else:
        # Case 2. Path is NLoS for effective Earth curvature not exceeded for p% time
        Srim = -inf
        for i in range(1, n-1):
            di = d_km[i]
            hi = h_mamsl[i]
            Srim = max(Srim, (hi + 500.0*cp*di*(d-di)-hrs)/(d-di))
        db = (hrs-hts+Srim*d)/(Stim+Srim)
        vb = (hts+Stim*db-(hts*(d-db)+hrs*db)/d) * sqrt(0.002*d/(lmbda*db*(d-db)))
        Ldbka = _J(vb)

    Ldba = Ldbka+(1.0-exp(-Ldbka/6.0))*(10.0+0.02*d)

    return Ldba


def _bullington_diffraction_loss_for_smooth_profile(lmbda: float, d_km: types.FloatArray, ap: float,
                                                    htep: float, hrep: float) -> float:
    """
    ITU-R P.2001-6, Attachment A (A.5).

    Args:
        lmbda (float): Wavelength (m).
        d_km (types.FloatArray): Distance from transmitter profile of n points along the great-
            circle radio path (km), with 3 <= n. The profile points must be spaced at equal
            intervals of distance. 
        ap (float): Effective Earth radius exceeded for p% time limited not to become infinite (km).
        htep (float): Effective transmitter height above smooth surface for diffraction model (m).
        hrep (float): Effective receiver, heights above smooth surface for diffraction model (m).

    Returns:
        Ldbs (float): The Bullington diffraction loss for the smooth path (dB).
    """
    n = len(d_km)
    d = d_km[-1]

    Stim = -inf
    for i in range(1, n-1):
        di = d_km[i]
        Stim = max(Stim, 500.0*(d-di)/ap-htep/di)
    Str = (hrep-htep)/d

    if Stim < Str:
        # Case 1. Path is LoS for effective Earth radius exceeded for p% time
        vsmax = -inf
        for i in range(1, n-1):
            di = d_km[i]
            vsmax = max(vsmax, (500.0*di*(d-di)/ap - (htep*(d-di)+hrep*di)/d)
                        *sqrt(0.002*d/(lmbda*di*(d-di))))
        Ldbks = _J(vsmax)
    else:
        # Case 2. Path is NLoS for effective Earth radius exceeded for p% time
        Srim = -inf
        for i in range(1, n-1):
            di = d_km[i]
            Srim = max(Srim, 500.0*di/ap-hrep/(d-di))
        db = (hrep-htep+Srim*d)/(Stim+Srim)
        vb = (htep+Stim*db-(htep*(d-db)+hrep*db)/d) * sqrt(0.002*d/(lmbda*db*(d-db)))
        Ldbks = _J(vb)

    Ldbs = Ldbks+(1.0-exp(-Ldbks/6.0))*(10.0+0.02*d)

    return Ldbs


def _Q0ca(is_los: bool, f: float, d: float, hlo: float, eps_p: float, nd65m1: float, phi_mn: float,
          dlt: float, dlr: float, hts: float, hrs: float, h_mamsl: types.FloatArray, ilt: int,
          ilr: int, theta_t: float, theta_r: float) -> float:
    """
    ITU-R P.2001-6, Attachment B (B.2).

    Args:
        is_los (bool): Whether the path is LoS or NLoS for median time, as determined by § 3.7.
        f (float): Frequency (GHz).
        d (float): Path length (km).
        hlo (float): Lower antenna height (mamsl).
        eps_p (float): Positive value of path inclination (mrad).
        nd65m1 (float):  Refractivity gradient in the lowest 65 m of the atmosphere exceeded for 1%
            of an average year (N-Units).
        phi_mn (float): Path mid-point latitude (degrees).
        dlt (float): Transmitter to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        dlr (float): Receiver to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        hts (float): Transmitter height (mamsl).
        hrs (float): Receiver height (mamsl).
        h_mamsl (types.FloatArray): Terrain height profile of n points (m above mean sea level).
        ilt (int): Profile index of transmitter horizon. (zero-based)
        ilr (int): Profile index of receiver horizon. (zero-based)
        theta_t (float): Horizon elevation angle relative to the local horizontal as viewed from
            transmitter (mrad).
        theta_r (float): Horizon elevation angle relative to the local horizontal as viewed from
            receiver (mrad).

    Returns:
        Q0ca (float): The notional zero-fade annual percentage time for the whole path (%).
    """
    if is_los:
        Q0ca = _Q0ca_B3(f, d, hlo, eps_p, nd65m1, phi_mn)
    else:
        Q0cat = _Q0ca_B3(f, dlt, min(hts, h_mamsl[ilt]), fabs(theta_t), nd65m1, phi_mn)
        Q0car = _Q0ca_B3(f, dlr, min(hrs, h_mamsl[ilr]), fabs(theta_r), nd65m1, phi_mn)
        Q0ca = max(Q0cat, Q0car)
    return Q0ca


def _Q0ca_B3(f: float, dca: float, hca: float, eps_ca: float, nd65m1: float, phi_mn: float
             ) -> float:
    """
    ITU-R P.2001-6, Attachment B (B.3).

    Args:
        f (float): Frequency (GHz).
        dca (float): (km).
        hca (float): (mamsl).
        eps_ca (float): (mrad).
        nd65m1 (float):  Refractivity gradient in the lowest 65 m of the atmosphere exceeded for 1%
            of an average year (N-Units).
        phi_mn (float): Path mid-point latitude (degrees).

    Returns:
        Q0ca (float): The notional zero-fade annual percentage time (%).
    """
    K = pow(10, -(4.6+0.0027*nd65m1))
    qw = K*pow(dca, 3.1)*pow(1+eps_ca, -1.29)*pow(f, 0.8)*pow(10, -0.00089*hca)

    if abs(phi_mn) <= 45.0:
        Cg = 10.5 - 5.6*log10(1.1 + pow(fabs(cos(2*radians(phi_mn))), 0.7)) - 2.7*log10(dca) + \
             1.7*log10(1+eps_ca)
    else:
        Cg = 10.5 - 5.6*log10(1.1 - pow(fabs(cos(2*radians(phi_mn))), 0.7)) - 2.7*log10(dca) + \
             1.7*log10(1+eps_ca)

    if Cg > 10.8:
        Cg = 10.8

    Q0ca = pow(10, -0.1*Cg)*qw
    return Q0ca


def _Qcaf(a: float, q0ca: float) -> float:
    """
    ITU-R P.2001-6, Attachment B (B.4).

    Percentage time a given clear-air fade level is exceeded on a surface path.

    Args:
        a (float): Clear-air fade (dB).
        q0ca (float): The notional zero-fade annual percentage time for the whole path (%).

    Returns:
        Qcaf (float): The percentage of the non-rain time a given fade in dB below the median
            signal level is exceeded (%).
    """
    A = a
    if A >= 0:
        qt = 3.576-1.955*log10(q0ca)
        qa = 2+(1+0.3*pow(10, -0.05*A))*(pow(10, -0.016*A))*(qt+4.3*(pow(10, -0.05*A)+A/800))
        Qcaf = 100*(1-exp(-pow(10, -0.05*qa*A)*ln(2)))
    else:
        qs = -4.05-2.35*log10(q0ca)
        qe = 8+(1+0.3*pow(10, 0.05*A))*pow(10, 0.035*A)*(qs+12*(pow(10, 0.05*A)-A/800))
        Qcaf = 100*exp(-pow(10, 0.05*qe*A)*ln(2))
    return Qcaf


def _Qcaftropo(a: float) -> float:
    """
    ITU-R P.2001-6, Attachment B (B.5).

    Percentage time a given clear-air fade level is exceeded on a troposcatter path.

    Args:
        a (float): Clear-air fade (dB).

    Returns:
        float: The percentage of the non-rain time a given fade in dB below the median signal level
            is exceeded (%).
    """
    if a < 0:
        return 100
    else:
        return 0


def _precipitation_fading_preleminary_calculations(f: float, q: float, phi_n: float, phi_e: float,
                                                   hrainlo: float, hrainhi: float, drain: float,
                                                   vpol: bool) -> float:
    """
    ITU-R P.2001-6, Annex C (C.2).

    Args:
        f (float): Frequency (GHz).
        q (float): Percentage of average year for which predicted basic transmission loss is
            exceeded, given by 100 - p (%).
        phi_n (float): Latitude for obtaining rain climatic parameters (degrees).
        phi_e (float): Longitude for obtaining rain climatic parameters (degrees).
        hrainlo (float): hrainlo and hrainhi are the heights of the ends of the path for a
            precipitation calculation (mamsl).
        hrainhi (float): hrainlo and hrainhi are the heights of the ends of the path for a
            precipitation calculation (mamsl).
        drain (float): Length of the path for rain calculations (km).
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.

    Returns:
        is_rain_path (bool): Whether the path is classified as "rain" or "non-rain".
        a (float): A parameters defining the cumulative distribution of rain rate.
        b (float): A parameters defining the cumulative distribution of rain rate.
        c (float): A parameters defining the cumulative distribution of rain rate.
        dr (float): Path length for precipitation calculations (km).
        Q0ra (float): Percentage of an average year in which rain occurs (%).
        kmod (float): Modified regression coefficient.
        alpha_mod (float): Modified regression coefficient.
        Gm (list[float]): Attenuation multiplier array.
        Pm (list[float]): Probability array.
        Fwvr (float): Factor used to estimate the effect of additional water vapour under rainy
            conditions. 
    """
    Pr6 = _digital_map_value(_MapId.ESARAIN_PR6_V5, phi_n, phi_e)
    MT = _digital_map_value(_MapId.ESARAIN_MT_V5, phi_n, phi_e)
    Brain = _digital_map_value(_MapId.ESARAIN_BETA_V5, phi_n, phi_e)
    h0 = _digital_map_value(_MapId.H0, phi_n, phi_e)
    hR = 360+1000*h0
    hRtop = hR+2400
    if Pr6 == 0 or hrainlo >= hRtop:
        # "no-rain" path
        is_rain_path = False
        Q0ra = 0
        Fwvr = 0
        #return is_rain_path, a, b, c, dr, Q0ra, kmod, alpha_mod, Gm, Pm, Fwvr
        return is_rain_path, 0, 0, 0, 0, Q0ra, 0, 0, [0], [0], Fwvr

    # "rain" path
    is_rain_path = True
    Mc = Brain*MT
    Ms = (1-Brain)*MT
    Q0ra = Pr6*(1-exp(-0.0079*Ms/Pr6))
    a1 = 1.09
    b1 = (Mc+Ms)/(21797*Q0ra)
    c1= 26.02*b1
    Qtran = Q0ra*exp(a1*(2*b1-c1)/(c1*c1))

    if vpol:
        tau = 90
    else:
        tau = 0
    eps_rain_rad = 0.001*(hrainhi-hrainlo)/drain
    eps_rain_deg = degrees(eps_rain_rad)
    if f >= 1:
        k, alpha = p838_3.coefficients(f_ghz=f, theta_deg=eps_rain_deg, tau_deg=tau)
    else:
        k, alpha = p838_3.coefficients(f_ghz=1, theta_deg=eps_rain_deg, tau_deg=tau)
        k *= f

    dr = min(drain, 300)
    drmin = max(dr, 1)

    #kmod = pow(1.763, alpha)*k*(0.6546*exp(-0.009516*drmin)+0.3499*exp(-0.01182*drmin)) # TODO -0.01182  in P.2001-6
    kmod = pow(1.763, alpha)*k*(0.6546*exp(-0.009516*drmin)+0.3499*exp(-0.001182*drmin)) # TODO -0.001182 in P.2001-5 and earlier ??
    alpha_mod = (0.753+0.197/drmin)*alpha+0.1572*exp(-0.02268*drmin)-0.1594*exp(-0.0003617*drmin)

    table_C1 = _p2001_6_shared['TABLE_C.1']
    len_table_C1 = len(table_C1)
    assert len_table_C1 == 49, 'Wrong size for TABLE C.1'
    HEIGHT_COL = 0
    PROB_COL = 1
    G = [0]*len_table_C1
    P = [0]*len_table_C1
    G[0] = 1
    # we will use zero-based indexes instead of 1-based
    m = 0
    n = 0
    for n in range(0, len_table_C1):
        Hn = table_C1[n][HEIGHT_COL]
        hT = hR + Hn
        if hrainlo >= hT:
            continue
        if hrainhi > hT-1200:
            G[m] = _path_averaged_factor(hT, hrainlo, hrainhi)
            P[m] = table_C1[n][PROB_COL]
            if n < len_table_C1-1:
                m += 1
        else:
            P[m] = P[m] + table_C1[n][PROB_COL]
            G[m] = 1
    M = m+1 # +1 since we used zero-based indexes
    P = P[:M]
    G = G[:M]
    Fwvr = 0.0
    for Gm, Pm in zip(G, P):
        Fwvr += Gm*Pm
    Rwvr = 6*(log10(Q0ra/q)/log10(Q0ra/Qtran))-3
    Fwvr *= 0.5*(1+tanh(Rwvr))

    return is_rain_path, a1, b1, c1, dr, Q0ra, kmod, alpha_mod, G, P, Fwvr


def _Qrain(attenuation: float, is_rain_path: bool, a: float, b: float, c: float, dr: float,
           kmod: float, alpha_mod: float, g_array: list[float], p_array: list[float]) -> float:
    """
    ITU-R P.2001-6, Annex C (C.3).

    Percentage time a given precipitation fade level is exceeded (%).
    """
    A = attenuation
    G = g_array
    P = p_array
    if A < 0:
        Qrain = 100.0
    else:
        if is_rain_path:
            drlim = max(dr, 0.001)
            Qrain = 0.0
            for Pm, Gm in zip(P, G):
                Rm = pow(A/(Gm*drlim*kmod), 1/alpha_mod)
                Qrain += Pm*exp(-a*Rm*(b*Rm+1)/(c*Rm+1))
            Qrain *= 100
        else:
            Qrain = 0.0
    return Qrain


def _attenuation_multiplier(delta_h: float) -> float:
    """
    ITU-R P.2001-6, Annex C (C.4).

    Melting-layer model.

    Returns:
        (float): Attenuation multiplier.
    """
    if 0 < delta_h:
        gamma = 0.0
    elif delta_h < -1200:
        gamma = 1.0
    else:
        x = 4*(1-exp(delta_h/70))**2
        gamma = x / (1 + (1-exp(-(delta_h/600)**2))**2 * (x-1))
    return gamma


def _path_averaged_factor(ht: float, hlo: float, hhi: float) -> float:
    """
    ITU-R P.2001-6, Annex C (C.5).

    Returns:
        G (float): The path-averaged factor.
    """
    slo = 1 + floor((ht-hlo)/100)
    shi = 1 + floor((ht-hhi)/100)
    if slo < 1:
        G = 0
    elif shi > 12:
        G = 1
    elif slo == shi:
        G = _attenuation_multiplier(0.5*(hlo+hhi)-ht)
    else:
        G = 0
        sfirst = max(shi, 1)
        slast = min(slo, 12)
        for s in range(sfirst, slast+1):
            if shi < s < slo:
                delta_h = 100*(0.5-s)
                Q = 100/(hhi-hlo)
            elif s == slo:
                delta_h = 0.5*(hlo-ht-100*(s-1))
                Q = (ht-100*(s-1)-hlo)/(hhi-hlo)
            elif s == shi:
                delta_h = 0.5*(hhi-ht-100*s)
                Q = (hhi-(ht-100*s))/(hhi-hlo)
            else:
                raise RuntimeError('No matching condition.')
            gamma_slice = _attenuation_multiplier(delta_h)
            G = G + Q*gamma_slice
        if slo > 12:
            Q = (ht-1200-hlo)/(hhi-hlo)
            G = G + Q
    return G


def _longest_continuous_land(d: float, z: types.IntArray|None, lops: list[float]
                             ) -> tuple[float, float]:
    """
    ITU-R P.2001-6, Annex D (D.1).

    Args:
        d (float): Great-circle path distance (km).
        z (types.IntArray|None): Radio climatic zone profile of n points (1=Sea, 3=Coastal Land,
            4=Inland). Inland is assumed everywhere when z is set to None.
        lops (list[float]): Length of path sections profile of n points (km).

    Returns:
        dtm (float): Longest continuous land (inland + coastal) section of the great-circle
            path (km).
        dlm (float): Longest continuous inland section of the great-circle path (km).

    Raises:
        ValueError: If z contains an unrecognized RadioClimaticZone value.
    """
    dtm = 0.0
    dlm = 0.0

    if z is None:
        dtm = dlm = d  # assumes INLAND for whole path
    else:
        n = len(lops)
        temp_dtm = 0.0
        temp_dlm = 0.0

        for i in range(n):
            if z[i] == RadioClimaticZone.INLAND.value:
                temp_dtm += lops[i]
                temp_dlm += lops[i]
            elif z[i] == RadioClimaticZone.COASTAL_LAND.value:
                temp_dtm += lops[i]
                dlm = max(dlm, temp_dlm)
                temp_dlm = 0.0
            elif z[i] == RadioClimaticZone.SEA.value:
                dtm = max(dtm, temp_dtm)
                temp_dtm = 0.0
                dlm = max(dlm, temp_dlm)
                temp_dlm = 0.0
            else:
                raise ValueError(f'Unknown RadioClimaticZone value: {z[i]}')

        dtm = max(dtm, temp_dtm)
        dlm = max(dlm, temp_dlm)

    return dtm, dlm


def _point_incidence_of_ducting(d: float, phi_mn: float, z: types.IntArray|None, lops: list[float]
                                ) -> tuple[float, float]:
    """
    ITU-R P.2001-6, Annex D (D.2).

    Args:
        d (float): Great-circle path distance (km).
        phi_mn (float): Path mid-point latitude (degrees).
        z (types.IntArray|None): Radio climatic zone profile of n points (1=Sea, 3=Coastal Land,
            4=Inland). Inland is assumed everywhere when z is set to None.
        lops (list[float]): Length of path sections profile of n points (km).

    Returns:
        beta0 (float): The point incidence of anomalous propagation (%), for the path centre
            location.
        tau (float): A parameter depending on the longest inland section of the path.
    """
    dtm, dlm = _longest_continuous_land(d, z, lops)
    abs_phi_nm = fabs(phi_mn)
    tau = 1-exp(-0.000412*pow(dlm, 2.41))
    u1 = pow(pow(10, -dtm/(16-6.6*tau))+pow(10, -(2.48+1.77*tau)), 0.2)
    u1 = min(u1, 1.0)

    if abs_phi_nm <= 70:
        u4 = pow(10, (-0.935+0.0176*abs_phi_nm)*log10(u1))
        beta0 = pow(10, -0.015*abs_phi_nm+1.67)*u1*u4
    else:
        u4 = pow(10, 0.3*log10(u1))
        beta0 = 4.17*u1*u4

    return beta0, tau


def _site_shielding_losses(f: float, dlt: float, dlr: float, theta_t: float, theta_r: float
                           ) -> tuple[float, float]:
    """
    ITU-R P.2001-6, Annex D (D.3).

    Args:
        f (float): Frequency (GHz).
        dlt (float): Transmitter to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        dlr (float): Receiver to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        theta_t (float): Horizon elevation angle relative to the local horizontal as viewed from
            transmitter (mrad).
        theta_r (float): Horizon elevation angle relative to the local horizontal as viewed from
            receiver (mrad).

    Returns:
        Ast (float): Transmitter site-shielding losses with respect to the duct (dB).
        Asr (float): Receiver site-shielding losses with respect to the duct (dB).
    """
    gtr = 0.1*dlt
    grr = 0.1*dlr
    theta_st = theta_t-gtr
    theta_sr = theta_r-grr
    Ast = Asr = 0.0
    if theta_st > 0:
        Ast = 20*log10(1+0.361*theta_st*sqrt(f*dlt))+0.264*theta_st*pow(f, 1.0/3.0)
    if theta_sr > 0:
        Asr = 20*log10(1+0.361*theta_sr*sqrt(f*dlr))+0.264*theta_sr*pow(f, 1.0/3.0)
    return Ast, Asr


def _dct(d: float, z: types.IntArray|None, lops: list[float]) -> float:
    """
    ITU-R P.2001-6, Annex D (D.4).

    Args:
        d (float): Great-circle path distance between transmit and receive antennas (km).
        z (types.IntArray|None): Radio climatic zone profile of n points (1=Sea, 3=Coastal Land,
            4=Inland). Inland is assumed everywhere when z is set to None.
        lops (list[float]): Length of path sections profile of n points (km).

    Returns:
        dct (float): Distance of the transmitter from the coast in the direction of the receiver
            (km).
    """
    if z is None:
        return d
    n = len(lops)
    dct = 0.0
    for i in range(n):
        if z[i] != RadioClimaticZone.SEA.value:
            dct += lops[i]
        else:
            break
    return dct


def _dcr(d: float, z: types.IntArray|None, lops: list[float]) -> float:
    """
    ITU-R P.2001-6, Annex D (D.4).

    Args:
        d (float): Great-circle path distance between transmit and receive antennas (km).
        z (types.IntArray|None): Radio climatic zone profile of n points (1=Sea, 3=Coastal Land,
            4=Inland). Inland is assumed everywhere when z is set to None.
        lops (list[float]): Length of path sections profile of n points (km).

    Returns:
        dcr (float): Distance of the receiver from the coast in the direction of the transmitter
            (km).
    """
    if z is None:
        return d
    n = len(lops)
    dcr = 0.0
    for i in range(n):
        if z[n-1-i] != RadioClimaticZone.SEA.value:
            dcr += lops[n-1-i]
        else:
            break
    return dcr


def _over_sea_surface_duct_coupling_corrections(d: float, z: types.IntArray|None, lops: list[float],
                                                omega: float, dlt: float, dlr: float, hts: float,
                                                hrs: float) -> tuple[float, float]:
    """
    ITU-R P.2001-6, Annex D (D.4).

    Args:
        d (float): Great-circle path distance between transmit and receive antennas (km).
        z (types.IntArray|None): Radio climatic zone profile of n points (1=Sea, 3=Coastal Land,
            4=Inland). Inland is assumed everywhere when z is set to None.
        lops (list[float]): Length of path sections profile of n points (km).
        omega (float): Fraction of the total path over sea.
        dlt (float): Transmitter to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        dlr (float): Receiver to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        hts (float): Transmitter height (mamsl).
        hrs (float): Receiver height (mamsl).
    
    Returns:
        Act (float): Over-sea surface duct coupling corrections for the transmitter (dB).
        Acr (float): Over-sea surface duct coupling corrections for the receiver (dB).
    """
    Act = Acr = 0.0
    if omega >= 0.75:
        dct = _dct(d, z, lops)
        if dct <= dlt and dct <= 5:
            Act = -3*exp(-0.25*dct**2)*(1+tanh(0.07*(50-hts)))
        dcr = _dcr(d, z, lops)
        if dcr <= dlr and dcr <= 5:
            Acr = -3*exp(-0.25*dcr**2)*(1+tanh(0.07*(50-hrs)))
    return Act, Acr


def _total_coupling_loss(f: float, dlt: float, dlr: float, omega: float, ast: float, asr: float,
                         act: float, acr: float) -> float:
    """
    ITU-R P.2001-6, Annex D (D.5).
    
    Args:
        f (float): Frequency (GHz).
        dlt (float): Transmitter to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        dlr (float): Receiver to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        omega (float): Fraction of the total path over sea.
        ast (float): Transmitter site-shielding losses with respect to the duct (dB).
        asr (float): Receiver site-shielding losses with respect to the duct (dB).
        act (float): Over-sea surface duct coupling corrections for the transmitter (dB).
        acr (float): Over-sea surface duct coupling corrections for the receiver (dB).

    Returns:
        Aac (float): Total coupling losses between the antennas and the anomalous propagation
            mechanism (dB).
    """
    Alf = 0.0
    if f < 0.5:
        Alf = (45.375-137.0*f+92.5*f*f)*omega
    Aac = 102.45+20*log10(f*(dlt+dlr))+Alf+ast+asr+act+acr
    return Aac


def _angular_distance_dependent_loss(f: float, d: float, ae: float, dlt: float, dlr: float,
                                     theta_t: float, theta_r) -> float:
    """
    ITU-R P.2001-6, Annex D (D.6).

    Args:
        f (float): Frequency (GHz).
        d (float): Path length (km).
        ae (float): Median effective Earth radius (km).
        dlt (float): Transmitter to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        dlr (float): Receiver to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        theta_t (float): Horizon elevation angle relative to the local horizontal as viewed from
            transmitter (mrad).
        theta_r (float): Horizon elevation angle relative to the local horizontal as viewed from
            receiver (mrad).

    Returns:
        Aad (float): Angular-distance dependent loss (dB).
    """
    gamma_d = 5E-5*ae*pow(f, 1.0/3.0)
    gtr = 0.1*dlt
    grr = 0.1*dlr
    theta_at = min(theta_t, gtr)
    theta_ar = min(theta_r, grr)
    theta_a = 1000*d/ae+theta_at+theta_ar
    Aad = 0.0
    if theta_a > 0:
        Aad = gamma_d*theta_a
    return Aad


def _distance_and_time_dependent_loss(p: float, q: float, d: float, beta0: float, tau: float,
                                      hm: float, htea: float, hrea: float, ae: float, dlt: float,
                                      dlr: float) -> float:
    """
    ITU-R P.2001-6, Annex D (D.7).

    Args:
        p (float): Percentage of average year for which predicted basic transmission loss is not
            exceeded (%), limited to range 0.00001 <= p <= 99.99999.
        q (float): Percentage of average year for which predicted basic transmission loss is
            exceeded, given by 100 - p (%).
        d (float): Path length (km).
        beta0 (float): Point incidence of anomalous propagation (%) for the path centre location.
        tau (float):
        hm (float): Path roughness parameter (m).
        htea (float): Effective transmitter height above smooth surface for anomalous (ducting/
            layer-reflection) model (m).
        hrea (float): Effective receiver height above smooth surface for anomalous (ducting/
            layer-reflection) model (m).
        ae (float): Median effective Earth radius (km).
        dlt (float): Transmitter to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        dlr (float): Receiver to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.

    Returns:
        Aat (float): Time-dependent loss (dB).
    """
    dar = min(d-dlt-dlr, 40)
    if hm > 10:
        u3 = exp(-4.6E-5*(hm-10)*(43+6*dar))
    else:
        u3 = 1.0
    alpha = -0.6-3.5E-9*pow(d, 3.1)*tau
    if alpha < -3.4:
        alpha = -3.4
    u2 = pow(500*d*d/(ae*(sqrt(htea)+sqrt(hrea))**2), alpha)
    if u2 > 1:
        u2 = 1.0
    beta_duct = beta0*u2*u3
    log_beta_duct = log10(beta_duct)
    gamma = 1.076*exp(-1E-6*pow(d, 1.13)*(9.51-4.8*log_beta_duct+0.198*log_beta_duct**2))/ \
            pow(2.0058-log_beta_duct, 1.012)
    Aat = -12 + (1.2+0.0037*d)*log10(p/beta_duct) + 12*pow(p/beta_duct, gamma) + 50/q
    return Aat


def _troposcatter_basic_transmission_loss(f: float, d: float, p: float, latt: float, lont: float,
                                          latr: float, lonr: float, phi_cvn: float, phi_cve: float,
                                          ae: float, theta_e: float, theta_t: float, theta_r: float,
                                          gt: float, gr: float, lbfs: float
                                          ) -> float:
    """
    ITU-R P.2001-6, Attachment E.

    Args:
        f (float): Frequency (GHz).
        d (float): Path length (km).
        p (float): Percentage of average year for which predicted basic transmission loss is not
            exceeded (%), limited to range 0.00001 <= p <= 99.99999.
        latt (float): Latitude of transmitter (degrees).
        lont (float): Longitude of transmitter (degrees).
        latr (float): Latitude of receiver (degrees).
        lonr (float): Longitude of receiver (degrees).
        phi_cvn (float): Troposcatter common volume latitude (degrees).
        phi_cve (float): Troposcatter common volume longitude (degrees).
        ae (float): Median effective Earth radius (km).
        theta_e (float): Angle subtended by d km at centre of spherical Earth (rad).
        theta_t (float): Horizon elevation angle relative to the local horizontal as viewed from
            transmitter (mrad).
        theta_r (float): Horizon elevation angle relative to the local horizontal as viewed from
            receiver (mrad).
        gt (float): Gain of transmitting antenna in the azimuthal direction of the path towards
            the other antenna, and at the elevation angle above the local horizontal of the other
            antenna in the case of a line-of-sight (LoS) path, otherwise of the antenna's radio
            horizon, for median effective Earth radius (dBi).
        gr (float): Gain of receiving antenna in the azimuthal direction of the path towards
            the other antenna, and at the elevation angle above the local horizontal of the other
            antenna in the case of a line-of-sight (LoS) path, otherwise of the antenna's radio
            horizon, for median effective Earth radius (dBi).
        lbfs (float): Free-space basic transmission loss (dB).
        
    Returns:
        Lbs (float): The troposcatter basic transmission loss not exceeded for p% time (dB).
    """
    clim = int(_digital_map_value(_MapId.TROPOCLIM, phi_cvn, phi_cve))
    if clim == 0:
        climt = int(_digital_map_value(_MapId.TROPOCLIM, latt, lont))
        climr = int(_digital_map_value(_MapId.TROPOCLIM, latr, lonr))
        if climt != 0 and climr != 0:
            clim = min(climt, climr)
        else:
            clim = max(climt, climr)

    M = [116.0, 129.60, 119.73, 109.30, 128.50, 119.73, 123.20][clim]
    #gamma = [20.27, 30.33, 20.27, 10.32, 30.27, 20.27, 30.27][clim] # TODO values from P.2001-6
    gamma =  [ 0.27,  0.33,  0.27,  0.32,  0.27,  0.27,  0.27][clim] # TODO values from P.2001-4 and earlier
    eq = [7, 8, 6, 9, 10, 6, 6][clim]

    theta = 1000*theta_e+theta_t+theta_r
    H = 0.25E-3*theta*d
    htrop = 0.125E-6*theta*theta*ae
    LN = 20*log10(5+gamma*H)+4.34*gamma*htrop
    ds = 0.001*theta*ae

    if eq == 6:
        Y90 = -2.2-(8.1-0.23*min(f, 4))*exp(-0.137*htrop)
    elif eq == 7:
        Y90 = -9.5-3*exp(-0.137*htrop)
    elif eq == 8:
        if ds < 100:
            Y90 = -8.2
        elif 100 <= ds < 1000:
            Y90 = 1.006E-8*ds**3-2.569E-5*ds**2+0.02242*ds-10.2
        else:
            Y90 = -3.4
    elif eq == 9:
        if ds < 100:
            Y90 = -10.845
        elif 100 <= ds < 465:
            Y90 = -4.5E-7*ds**3+4.45E-4*ds**2-0.122*ds-2.645
        else:
            Y90 = -8.4
    else: # eq == 10
        if ds < 100:
            Y90 = -11.5
        elif 100 <= ds < 550:
            Y90 = -8.519E-8*ds**3+7.444E-4*ds**2-4.18E-4*ds-12.1
        else:
            Y90 = -4.0

    if p >= 50:
        C = 1.26*pow(-log10((100-p)/50), 0.63)
    else:
        C = -1.26*pow(-log10(p/50), 0.63)
    Yp = C*Y90
    theta = max(theta, 1E-6)
    Ldist = max(10*log10(d)+30*log10(theta)+LN, 20*log10(d)+0.573*theta+20)
    Lfreq = 25*log10(f)-2.5*(log10(0.5*f))**2
    Lcoup = 0.07*exp(0.055*(gt+gr))
    Lbs = M + Lfreq + Ldist + Lcoup - Yp
    Lbs = max(Lbs, lbfs)
    return Lbs


def _gaseous_absorption_for_surface_path(f: float, d: float, phi_mn: float, phi_me: float,
                                         hmid: float, hts: float, hrs: float, gamma_o: float
                                         ) -> tuple[float, float, float]:
    """
    ITU-R P.2001-6, Attachment F (F.2).

    Args:
        f (float): Frequency (GHz).
        d (float): Path length (km).
        phi_mn (float): Path mid-point latitude (degrees).
        phi_me (float): Path mid-point longitude (degrees).
        hmid (float): Ground height at mid point of path (mamsl).
        hts (float): Transmitter height (mamsl).
        hrs (float): Receiver height (mamsl).
        gamma_o: Sea-level specific attenuation due to oxygen (dB/km).

    Returns:
        Aosur (float): Attenuation due to oxygen for the surface path (dB).
        Awsur (float): Attenuation due to water-vapour under non-rain conditions for the surface
            path (dB).
        Awrsur (float): Attenuation due to water-vapour under rain conditions for the surface
            path(dB).
    """
    rho_sur = _digital_map_value(_MapId.SURFWV_50_FIXED, phi_mn, phi_me)
    hsur = hmid
    gamma_w = _gamma_w(f, hsur, rho_sur)
    rho_surr = _rho_surr(hsur, rho_sur)
    gamma_wr = _gamma_w(f, hsur, rho_sur=rho_surr)
    hrho = 0.5*(hts+hrs)
    Aosur = gamma_o*d*exp(-hrho/5000)
    exp_hrho_2000 = exp(-hrho/2000)
    Awsur = gamma_w*d*exp_hrho_2000
    Awrsur = gamma_wr*d*exp_hrho_2000
    return Aosur, Awsur, Awrsur


def _gaseous_absorption_for_troposcatter_path(f: float, latt: float, lont: float, latr: float,
                                              lonr: float, h_mamsl: types.FloatArray,
                                              theta_tpos: float, theta_rpos: float, dtcv: float,
                                              drcv: float, gamma_o: float
                                              ) -> tuple[float, float, float]:
    """
    ITU-R P.2001-6, Attachment F (F.3).

    Gaseous absorption for a troposcatter path

    Args:
        f (float): Frequency (GHz).
        latt (float): Latitude of transmitter (degrees).
        lont (float): Longitude of transmitter (degrees).
        latr (float): Latitude of receiver (degrees).
        lonr (float): Longitude of receiver (degrees).
        h_mamsl (types.FloatArray): Terrain height profile of n points (m above mean sea level).
        theta_tpos (float): Horizon elevation angle relative to the local horizontal as viewed from
            transmitter and limited to be positive (mrad).
        theta_rpos (float): Horizon elevation angle relative to the local horizontal as viewed from
            receiver and limited to be positive (mrad).
        dtcv (float): Transmitter to troposcatter common volume distance (km).
        drcv (float): Receiver to troposcatter common volume distance (km).
        gamma_o: Sea-level specific attenuation due to oxygen (dB/km).

    Returns:
        Aos (float): Attenuation due to oxygen for the complete troposcatter path (dB).
        Aws (float): Attenuation due to water vapour under non-rain condition for the complete
            troposcatter path (dB).
        Awrs (float): Attenuation due to water vapour under rain condition for the complete
            troposcatter path (dB).
    """
    rho_sur = _digital_map_value(_MapId.SURFWV_50_FIXED, latt, lont)
    Aotcv, Awtcv, Awrtcv = _gaseous_absorption_for_tcv_troposcatter_path(
        f, h_mamsl[0], rho_sur, theta_tpos, dtcv, gamma_o)

    rho_sur = _digital_map_value(_MapId.SURFWV_50_FIXED, latr, lonr)
    Aorcv, Awrcv, Awrrcv = _gaseous_absorption_for_tcv_troposcatter_path(
        f, h_mamsl[-1], rho_sur, theta_rpos, drcv, gamma_o)

    Aos = Aotcv + Aorcv
    Aws = Awtcv + Awrcv
    Awrs = Awrtcv + Awrrcv

    return Aos, Aws, Awrs


def _gaseous_absorption_for_tcv_troposcatter_path(f: float, hsur: float, rho_sur: float,
                                                  theta_elev: float, dcv: float, gamma_o: float
                                                  ) -> tuple[float, float, float]:
    """
    ITU-R P.2001-6, Attachment F (F.4).

    Gaseous absorption for terminal/common-volume troposcatter path.

    Args:
        f (float): Frequency (GHz).
        hsur (float): Terrain height (mamsl).
        rho_sur (float): Surface water-vapour density under non-rain conditions (g/m3).
        theta_elev (float): Elevation angle of path (mrad).
        dcv (float): Horizontal distance to the common volume (km).
        gamma_o: Sea-level specific attenuation due to oxygen (dB/km).
    
    Returns:
        Ao (float): Attenuation due to oxygen for the terminal/common-volume troposcatter path
            (dB).
        Aw (float): Attenuation due to water vapour under non-rain condition for the terminal/
            common-volume troposcatter path (dB).
        Awr (float): Attenuation due to water vapour under rain condition for the terminal/
            common-volume troposcatter path (dB).
    """
    gamma_w = _gamma_w(f, hsur, rho_sur)
    rho_surr = _rho_surr(hsur, rho_sur)
    gamma_wr = _gamma_w(f, hsur, rho_surr)

    s = sin(0.001*theta_elev)
    do = 5/(0.65*s+0.35*sqrt(s*s+0.00304))
    dw = 2/(0.65*s+0.35*sqrt(s*s+0.00122))

    deo = do*(1-exp(-dcv/do))*exp(-hsur/5000)
    dew = dw*(1-exp(-dcv/dw))*exp(-hsur/2000)

    Ao = gamma_o*deo
    Aw = gamma_w*dew
    Awr = gamma_wr*dew

    return Ao, Aw, Awr


def _rho_surr(hsur: float, rho_sur: float) -> float:
    """
    ITU-R P.2001-6, Attachment F (F.5).

    Args:
        hsur (float): Terrain height for location of interest (mamsl).
        rho_sur (float): Surface water-vapour density for location of interest (g/m3). Values may
            be obtained from thed ata file surfwv_50_fixed.txt.

    Returns:
        rho_surr (float): Surface water-vapour density under rain conditions (g/m3).
    """
    if hsur <= 2600:
        rho_surr = rho_sur+0.4+0.0003*hsur
    else:
        rho_surr = rho_sur+5*exp(-hsur/1800)
    return rho_surr


def _gamma_o(f: float) -> float:
    """
    ITU-R P.2001-6, Attachment F (F.6).

    Args:
        f (float): Frequency (GHz).

    Returns:
        gamma_o (float): Sea-level specific attenuation due to oxygen (dB/km).
    """
    f2 = f*f
    gamma_o = (7.2/(f2+0.34) + 0.62/(pow(54-f,1.16)+0.83))*f2*1E-3
    return gamma_o


def _gamma_w(f: float, hsur: float, rho_sur: float) -> float:
    """
    ITU-R P.2001-6, Attachment F (F.6).

    Args:
        f (float): Frequency (GHz).
        hsur (float): Terrain height for location of interest (mamsl).
        rho_sur (float): Surface water-vapour density for location of interest (g/m3). Values may
            be obtained from thed ata file surfwv_50_fixed.txt.
    
    Returns:
        gamma_w (float): Sea-level specific attenuation due to water-vapour (dB/km).
    """
    rho_sea = rho_sur*exp(hsur/2000)
    eta = 0.955+0.006*rho_sea
    gamma_w = (0.046+0.0019*rho_sea+(3.98*eta/((f-22.235)**2+9.42*eta**2))*(1+ \
             ((f-22)/(f+22))**2))*f*f*rho_sea*1E-4
    return gamma_w


def _foEs(p: float, lat: float, lon: float) -> float:
    """
    ITU-R P.2001-6, Attachment G (G.1).

    Args:
        p (float): Percentage of average year for which predicted basic transmission loss is not
            exceeded (%), limited to range 0.00001 <= p <= 99.99999.
        lat (float): Latitude of interest (degrees).
        lon (float): Longitude of interest (degrees).

    Returns:
        foEs (float): (MHz).
    """
    if p < 1:
        p1 = 0.1
        p2 = 1
        map1 = _MapId.FOES0_1
        map2 = _MapId.FOES01
    elif p <= 10:
        p1 = 1
        p2 = 10
        map1 = _MapId.FOES01
        map2 = _MapId.FOES10
    else:
        p1 = 10
        p2 = 50
        map1 = _MapId.FOES10
        map2 = _MapId.FOES50

    foEs1 = _digital_map_value(map1, lat, lon)
    foEs2 = _digital_map_value(map2, lat, lon)
    foEs = foEs1+(foEs2-foEs1)*(log10(p/p1)/log10(p2/p1))
    return foEs


def _sporadic_E_1_hop_basic_transmission_loss(f: float, d: float, p: float, phi_mn: float,
                                              phi_me: float, ae: float, dlt: float, dlr: float,
                                              theta_t: float, theta_r: float) -> float:
    """
    ITU-R P.2001-6, Attachment G (G.2).
    
    Args:
        f (float): Frequency (GHz).
        d (float): Path length (km).
        p (float): Percentage of average year for which predicted basic transmission loss is not
            exceeded (%), limited to range 0.00001 <= p <= 99.99999.
        phi_mn (float): Path mid-point latitude (degrees).
        phi_me (float): Path mid-point longitude (degrees).
        ae (float): Median effective Earth radius (km).
        dlt (float): Transmitter to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        dlr (float): Receiver to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        theta_t (float): Horizon elevation angle relative to the local horizontal as viewed from
            transmitter (mrad).
        theta_r (float): Horizon elevation angle relative to the local horizontal as viewed from
            receiver (mrad).

    Returns:
        LbEs1 (float): Sporadic-E 1-hop basic transmission loss (dB).
    """
    foEs = _foEs(p, phi_mn, phi_me)
    gamma1 = (40/(1+(d/130)+(d/250)**2)+0.2*(d/2600)**2)*(1000*f/foEs)**2+exp((d-1660)/280)
    hes = 120
    l1 = 2*sqrt(ae**2+(ae+hes)**2-2*ae*(ae+hes)*cos(d/(2*ae)))
    Lbfs1 = 92.4 + 20*log10(f) + 20*log10(l1)
    alpha1 = d/(2*ae)
    eps_r1 = 0.5*pi-atan(ae*sin(alpha1)/(hes+ae*(1-cos(alpha1))))-alpha1
    delta_1t = 0.001*theta_t-eps_r1
    delta_1r = 0.001*theta_r-eps_r1

    def _v1(f, dl, delta, theta) -> float:
        v1 = 3.651*sqrt(1000*f*dl*(1-cos(delta))/cos(0.001*theta))
        if delta >= 0:
            return v1
        else:
            return -v1

    v1t = _v1(f, dlt, delta_1t, theta_t)
    v1r = _v1(f, dlr, delta_1r, theta_r)
    Lp1t = _J(v1t)
    Lp1r = _J(v1r)
    LbEs1 = Lbfs1 + gamma1 + Lp1t + Lp1r
    return LbEs1


def _sporadic_E_2_hop_basic_transmission_loss(f: float, d: float, p: float, latt: float,
                                              lont: float, latr: float, lonr: float, ae: float,
                                              dlt: float, dlr: float, theta_t: float,
                                              theta_r: float) -> float:
    """
    ITU-R P.2001-6, Attachment G (G.3).
    
    Args:
        f (float): Frequency (GHz).
        d (float): Path length (km).
        p (float): Percentage of average year for which predicted basic transmission loss is not
            exceeded (%), limited to range 0.00001 <= p <= 99.99999.
        latt (float): Latitude of transmitter (degrees).
        lont (float): Longitude of transmitter (degrees).
        latr (float): Latitude of receiver (degrees).
        lonr (float): Longitude of receiver (degrees).
        ae (float): Median effective Earth radius (km).
        dlt (float): Transmitter to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        dlr (float): Receiver to horizon distance (km). For LoS paths, set to distance to point
            with largest knife-edge loss.
        theta_t (float): Horizon elevation angle relative to the local horizontal as viewed from
            transmitter (mrad).
        theta_r (float): Horizon elevation angle relative to the local horizontal as viewed from
            receiver (mrad).
        
    Returns:
        LbEs2 (float): Sporadic-E 2-hop basic transmission loss (dB).
    """
    lat025, lon025 = intermediate_path_point(latt, lont, latr, lonr, 0.25*d)
    lat075, lon075 = intermediate_path_point(latt, lont, latr, lonr, 0.75*d)
    foEs025 = _foEs(p, lat025, lon025)
    foEs075 = _foEs(p, lat075, lon075)
    foEs2h = min(foEs025, foEs075)

    gamma2 = (40/(1+(d/260)+(d/500)**2)+0.2*(d/5200)**2)*(1000*f/foEs2h)**2+exp((d-3220)/560)
    hes = 120
    l2 = 4*sqrt(ae**2+(ae+hes)**2-2*ae*(ae+hes)*cos(d/(4*ae)))
    Lbfs2 = 92.4 + 20*log10(f) + 20*log10(l2)
    alpha2 = d/(4*ae)
    eps_r2 = 0.5*pi-atan(ae*sin(alpha2)/(hes+ae*(1-cos(alpha2))))-alpha2
    delta_2t = 0.001*theta_t-eps_r2
    delta_2r = 0.001*theta_r-eps_r2

    def _v2(f, dl, delta, theta) -> float:
        v1 = 3.651*sqrt(1000*f*dl*(1-cos(delta))/cos(0.001*theta))
        if delta >= 0:
            return v1
        else:
            return -v1

    v2t = _v2(f, dlt, delta_2t, theta_t)
    v2r = _v2(f, dlr, delta_2r, theta_r)
    Lp2t = _J(v2t)
    Lp2r = _J(v2r)
    LbEs2 = Lbfs2 + gamma2 + Lp2t + Lp2r
    return LbEs2


def _sporadic_E_basic_transmission_loss(lbes1: float, lbes2: float) -> float:
    """
    ITU-R P.2001-6, Attachment G (G.4).
    
    Args:
        lbes1 (float): Sporadic-E 1-hop basic transmission loss (dB).
        lbes2 (float): Sporadic-E 2-hop basic transmission loss (dB).

    Returns:
        Lbe (float): Basic sporadic-E transmission loss (dB).
    """
    if lbes1 < lbes2-20:
        Lbe = lbes1
    elif lbes2 < lbes1-20:
        Lbe = lbes2
    else:
        Lbe = -10*log10(pow(10, -0.1*lbes1)+pow(10, -0.1*lbes2))
    return Lbe


def path_length(lat0: float, lon0: float, lat1: float, lon1: float) -> float:
    """
    ITU-R P.2001-6, Attachment H (H.2).

    Calculates the great-circle path length between two points on the surface of the Earth (km).
    
    Args:
        lat0 (float): Latitude of first point (degrees), with -90 <= lat0 <= 90.
        lon0 (float): Longitude of first point (degrees), with -180 <= lon0 <= 180.
        lat1 (float): Latitude of second point (degrees), with -90 <= lat1 <= 90.
        lon1 (float): Longitude of second point (degrees), with -180 <= lon1 <= 180.

    Returns:
        float: The great-circle path length between two points on the surface of the Earth (km).
    """
    lat0 = radians(lat0)
    lon0 = radians(lon0)
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    x = (sin(lat0)*sin(lat1)) + (cos(lat0)*cos(lat1)*cos(lon1-lon0))
    x = min(x, 1) # to avoid domain error in acos() in some cases where (lat0, lon0)==(lat1, lon1)
    path_length_km = acos(x) * _RE_KM
    return path_length_km


def bearing(lat0: float, lon0: float, lat1: float, lon1: float) -> float:
    """
    ITU-R P.2001-6, Attachment H (H.2).

    Calculates the bearing of the great-circle path between two points on the surface of the Earth,
    in degrees.

    Args:
        lat0 (float): Latitude of first point (degrees), with -90 <= lat0 <= 90.
        lon0 (float): Longitude of first point (degrees), with -180 <= lon0 <= 180.
        lat1 (float): Latitude of second point (degrees), with -90 <= lat1 <= 90.
        lon1 (float): Longitude of second point (degrees), with -180 <= lon1 <= 180.

    Returns:
        float: The bearing of the great-circle path from the first point towards the second point
            (degrees), with 0 <= bearing <= 360. Corresponds to the angle between due north at the
            first point eastwards (clockwise) to the direction of the path.
    """
    phi_tn = radians(lat0)
    sin_phi_tn = sin(phi_tn)
    cos_phi_tn = cos(phi_tn)
    phi_te = radians(lon0)
    phi_rn = radians(lat1)
    sin_phi_rn = sin(phi_rn)
    cos_phi_rn = cos(phi_rn)
    phi_re = radians(lon1)

    delta_lon = phi_re-phi_te
    r = sin_phi_tn*sin_phi_rn+cos_phi_tn*cos_phi_rn*cos(delta_lon)
    x1 = sin_phi_rn-r*sin_phi_tn
    y1 = cos_phi_tn*cos_phi_rn*sin(delta_lon)
    if fabs(x1) < 1E-9 and fabs(y1) < 1E-9:
        Bt2r = phi_re
    else:
        Bt2r = atan2(y1, x1)

    bearing_deg = degrees(Bt2r)
    if bearing_deg < 0:
        bearing_deg += 360
    return bearing_deg


def intermediate_path_point(lat0: float, lon0: float, lat1: float, lon1: float,
                            dist_km: float) -> tuple[float, float]:
    """
    ITU-R P.2001-6, Attachment H (H.3).

    Calculates the latitude and longitude of any point along a great-circle path on the surface of
    the Earth.

    Args:
        lat0 (float): Latitude at the first end of the path (degrees), with -90 <= lat0 <= 90.
        lon0 (float): Longitude at the first end of the path (degrees), with -180 <= lon0 <= 180.
        lat1 (float): Latitude at the second end of the path (degrees), with -90 <= lat1 <= 90.
        lon1 (float): Longitude at the second end of the path (degrees), with -180 <= lon1 <= 180.
        dist_km (float): Great-circle distance of an intermediate point from the first end of the
            path (km).

    Returns:
        lat (float): Latitude of the intermediate point along the great-circle path (degrees).
        lon (float): Longitude of the intermediate point along the great-circle path (degrees).
    """
    phi_tn = radians(lat0)
    sin_phi_tn = sin(phi_tn)
    cos_phi_tn = cos(phi_tn)
    phi_te = radians(lon0)
    phi_rn = radians(lat1)
    sin_phi_rn = sin(phi_rn)
    cos_phi_rn = cos(phi_rn)
    phi_re = radians(lon1)
    phi_pnt = dist_km/_RE_KM
    sin_phi_pnt = sin(phi_pnt)
    cos_phi_pnt = cos(phi_pnt)

    delta_lon = phi_re-phi_te
    r = sin_phi_tn*sin_phi_rn+cos_phi_tn*cos_phi_rn*cos(delta_lon)
    x1 = sin_phi_rn-r*sin_phi_tn
    y1 = cos_phi_tn*cos_phi_rn*sin(delta_lon)
    if fabs(x1) < 1E-9 and fabs(y1) < 1E-9:
        Bt2r = phi_re
    else:
        Bt2r = atan2(y1, x1)

    s = sin_phi_tn*cos_phi_pnt+cos_phi_tn*sin_phi_pnt*cos(Bt2r)
    phi_pntn = asin(s)
    x2 = cos_phi_pnt-s*sin_phi_tn
    y2 = cos_phi_tn*sin_phi_pnt*sin(Bt2r)
    if fabs(x2) < 1E-9 and fabs(y2) < 1E-9:
        phi_pnte = Bt2r
    else:
        phi_pnte = phi_te+atan2(y2, x2)

    interm_lat = degrees(phi_pntn)
    interm_lon = degrees(phi_pnte)
    if interm_lon < -180:
        interm_lon += 360
    if interm_lon > 180:
        interm_lon -= 360

    return (interm_lat, interm_lon)


def _Aiter(q: float, qiter: Callable, ainit: float=10.0, aacc=0.01) -> float:
    """
    ITU-R P.2001-6, Attachment I (I.2).

    Iterative procedure to invert a cumulative distribution function.

    Args:
        q (float): Exceedence time percentage (%).
        qiter (Callable): The cumulative distribution function.
        ainit (float, optional): Initial value of trial (dB). Default is 10.
        aacc (float, optional): Absolute accuracy of _Aiter (dB). Default is 0.01.

    Returns:
        A (float): Attenuation level for the propagation mechanism (dB).
    """
    Ahigh = ainit/2
    Alow = -ainit/2
    Astep = ainit
    qhigh = qiter(Ahigh)
    qlow = qiter(Alow)

    # Stage 1: initial search range iteration
    iter_count = 0
    while iter_count <= 10:
        if q < qhigh:
            Alow = Ahigh
            qlow = qhigh
            Astep = 2*Astep
            Ahigh = Ahigh+Astep
            qhigh = qiter(Ahigh)
        elif q > qlow:
            Ahigh = Alow
            qhigh = qlow
            Astep = 2*Astep
            Alow = Alow-Astep
            qlow = qiter(Alow)
        else:
            break
        iter_count += 1

    # Stage 2: binary search
    Atry = 0.5*(Alow+Ahigh)
    niter = ceil(3.32*log10(Astep/aacc))
    iter_count = 0
    while iter_count <= niter:
        qtry = qiter(Atry)
        if qtry < q:
            Ahigh = Atry
        else:
            Alow = Atry
        Atry = 0.5*(Alow+Ahigh)
        iter_count += 1

    return Atry


def _thread_safe_get_digital_map_array(filename: str) -> array:
    # NOTE: It is not safe to concurrently access a Python dictionary from one thread while it is
    # being modified by another thread, even if you are only reading a specific key/value that is
    # not being directly modified. This is why we always use the lock here.
    with _p2001_6_shared['digital_maps_lock']:
        dmaps = _p2001_6_shared['digital_maps']
        if filename not in dmaps:
            pathname = join(_du.install_dir(), _p2001_6_shared['DATA_DIR'], filename)
            try:
                arr = p1144_13.load_digital_map(pathname)
            except FileNotFoundError:
                _download_rec_data()
                arr = p1144_13.load_digital_map(pathname)
            dmaps[filename] = arr
        map_array = dmaps[filename]
    return map_array


def _download_rec_data() -> None:
    data_dir = _p2001_6_shared['DATA_DIR']
    full_path_data_dir = join(_du.install_dir(), data_dir)
    filenames = ['DN_Median.txt','DN_SubSlope.txt','DN_SupSlope.txt','dndz_01.txt',
                 'Esarain_Beta_v5.txt','Esarain_Mt_v5.txt','Esarain_Pr6_v5.txt','FoEs0.1.txt',
                 'FoEs01.txt','FoEs10.txt','FoEs50.txt','h0.txt','surfwv_50_fixed.txt',
                 'TropoClim.txt']
    lock = FileLock(_du.get_lockfile_pathname(data_dir))
    with lock:
        if _du.files_all_exist(full_path_data_dir, filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.2001-6-202509-I!!ZIP-E.zip'
            zip_pathname = _du.download(url, full_path_data_dir)
            _du.extract_files(zip_pathname, filenames, create_dirs=True, delete_zip_archive=True)
            _du.print_notice()
        else:
            _du.print_already_installed(full_path_data_dir, filenames)


_p2001_6_shared = {
    'DATA_DIR': 'p2001_6',
    'digital_maps_lock': Lock(),
    'digital_maps': {},
    'digital_maps_params': _init_digital_maps_params(),
    'TABLE_C.1': [
        (-2400,0.000555), (-2300,0.000802), (-2200,0.001139), (-2100,0.001594), (-2000,0.002196),
        (-1900,0.002978), (-1800,0.003976), (-1700,0.005227), (-1600,0.006764), (-1500,0.008617),
        (-1400,0.010808), (-1300,0.013346), (-1200,0.016225), (-1100,0.019419), (-1000,0.022881),
        ( -900,0.026542), ( -800,0.030312), ( -700,0.034081), ( -600,0.037724), ( -500,0.041110),
        ( -400,0.044104), ( -300,0.046583), ( -200,0.048439), ( -100,0.049589), (    0,0.049978),
        (  100,0.049589), (  200,0.048439), (  300,0.046583), (  400,0.044104), (  500,0.041110),
        (  600,0.037724), (  700,0.034081), (  800,0.030312), (  900,0.026542), ( 1000,0.022881),
        ( 1100,0.019419), ( 1200,0.016225), ( 1300,0.013346), ( 1400,0.010808), ( 1500,0.008617),
        ( 1600,0.006764), ( 1700,0.005227), ( 1800,0.003976), ( 1900,0.002978), ( 2000,0.002196),
        ( 2100,0.001594), ( 2200,0.001139), ( 2300,0.000802), ( 2400,0.000555)
    ]
}
