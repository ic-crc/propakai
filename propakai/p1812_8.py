# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.1812-8.

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite this software
    package along with the underlying ITU-R standard:

    * **ITU-R Standard:** International Telecommunication Union (2025).
      *Recommendation ITU-R P.1812-8: A path-specific propagation prediction method for
      point-to-area terrestrial services in the frequency range 30 MHz to 6 GHz*. Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.1812/en


Notes:
    This module was converted from C++ to Python with the assistance of an AI tool (Claude by
    Anthropic). The converted code has been reviewed and validated against ITU validation
    examples.
"""

from os.path import join
from math import log10, log as ln, sqrt, inf, atan, exp, tanh, cos, acos, pi, fabs
from enum import Enum
from warnings import warn
from threading import Lock
from array import array
from filelock import FileLock
from propakai import _download_utils as _du
from propakai import types
from propakai import p1144_13
from propakai import p2001_6


__all__ = ['RadioClimaticZone',
           'ClutterCategory',
           'basic_transmission_loss',
           'field_strength',
           'dn50',
           'n050']


class RadioClimaticZone(Enum):
    """Documents integer values that may be used in rcz parameter of basic_transmission_loss()."""
    COASTAL_LAND = 3
    INLAND       = 4
    SEA          = 1


class ClutterCategory(Enum):
    """Documents integer values that may be used in cc parameter of basic_transmission_loss()."""
    WATER_SEA           = 1
    OPEN_RURAL          = 2
    SUBURBAN            = 3
    URBAN_TREES_FOREST  = 4
    DENSE_URBAN         = 5


def basic_transmission_loss(f_ghz: float, p_percent: float, pl_percent: float, latt: float,
                            lont: float, latr: float, lonr: float, htg_m: float, hrg_m: float,
                            vpol: bool, d_km: types.FloatArray, h_mamsl: types.FloatArray,
                            cc: types.IntArray|None=None, rch_m: types.FloatArray|None=None,
                            sh_mamsl: types.FloatArray|None=None, rcz: types.IntArray|None=None,
                            dct_km: float|None=None, dcr_km: float|None=None,
                            delta_n: float|None=None, n0: float|None=None, wa_m: float=100.0
                            ) -> float:
    """
    The basic transmission loss not exceeded for p_percent time and pl_percent locations.

    Args:
        f_ghz (float): Frequency (GHz), with 0.03 <= f_ghz <= 6.0.
        p_percent (float): Percentage of average year for which the calculated basic transmission
            loss is not exceeded (%), with 1.0 <= p_percent <= 50.0.
        pl_percent (float): Percentage of locations for which the calculated basic transmission
            loss is not exceeded (%), with 1.0 <= pl_percent <= 99.0.
        latt (float): Latitude of transmitter (degrees), with -80 <= latt <= 80.
        lont (float): Longitude of transmitter (degrees), with -180 <= lont <= 180.
        latr (float): Latitude of receiver (degrees), with -80 <= latr <= 80.
        lonr (float): Longitude of receiver (degrees), with -180 <= lonr <= 180.
        htg_m (float): Transmit antenna centre height above ground level (m), with
            1 <= htg_m <= 3000.
        hrg_m (float): Receive antenna centre height above ground level (m), with
            1 <= htr_m <= 3000.
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.
        d_km (types.FloatArray): Distance from transmitter profile of n points (km), with 3 <= n.
        h_mamsl (types.FloatArray): Terrain height profile of n points (m above mean sea level).
        cc (types.IntArray|None, optional): Clutter category profile of n points (1=Water/Sea,
            2=Open/Rural, 3=Suburban, 4=Urban/Trees/Forest, 5=Dense Urban). cc is ignored when
            either rch_m or sh_mamsl is specfied, otherwise Open/Rural is assumed everywhere when
            cc is set to None.
        rch_m (types.FloatArray|None, optional): Representative clutter height (m) profile of n
            points. rch_m is ignored if sh_mamsl is specified.
        sh_mamsl (types.FloatArray|None, optional): Surface height (m above mean sea level) profile
            of n points.
        rcz (types.IntArray|None, optional): Radio climatic zone profile of n points (1=Sea,
            3=Coastal Land, 4=Inland). Inland is assumed everywhere when rcz is set to None.
        dct_km (float|None, optional): Distance of the transmitter from the coast (km), in the
            direction of the other terminal. For a terminal on a ship or sea platform the distance
            is zero. When set to None, dct_km is automatically estimated using the radio climate
            zone (rcz) and distance (d_km) profiles.
        dcr_km (float|None, optional): Distance of the receiver from the coast (km), in the
            direction of the other terminal. For a terminal on a ship or sea platform the distance
            is zero. When set to None, dcr_km is automatically estimated using the radio climate
            zone (rcz) and distance (d_km) profiles.
        delta_n (float|None, optional): Average radio-refractivity lapse-rate through the lowest 1
            km of the atmosphere (N-units/km). When set to None, delta_n is automatically obtained
            using one of the recommendation's digital map at mid-distance between latt/lont and
            latr/lonr.
        n0 (float|None, optional): Sea-level surface refractivity (N-units). When set to None, n0
            is automatically obtained using one of the recommendation's digital map at mid-distance
            between latt/lont and latr/lonr.
        wa_m (float, optional): Prediction resolution (m), the width of the square area over which
            the location variability applies. Default value is 100 m.

    Returns:
        Lb (float): The basic transmission loss (dB) not exceeded for p_percent time and pl_percent
            locations.
    """
    _input_validattion(f_ghz, p_percent, pl_percent, htg_m, hrg_m, d_km, h_mamsl, cc, rch_m, rcz)

    g, r = _g_profile(h_mamsl, cc, rch_m, sh_mamsl)
    lops = _length_of_path_sections_profile(d_km)
    n = len(d_km)
    hts = h_mamsl[0] + htg_m
    hrs = h_mamsl[n-1] + hrg_m
    dn = d_km[n-1]
    centre_lat, centre_lon = p2001_6.intermediate_path_point(latt, lont, latr, lonr, dn/2.0)
    dtm, dlm = _longest_continuous_land(dn, rcz, lops)
    b0 = _b0(centre_lat, dtm, dlm)
    if delta_n is None:
        delta_n = dn50(centre_lat, centre_lon)
    if n0 is None:
        n0 = n050(centre_lat, centre_lon)
    ae, ab = _effective_earth_radius(delta_n)
    omega = _over_water_percent(dn, rcz, lops)
    if dct_km is None:
        if omega >= 0.75: # otherwise dct and dcr are not used
            assert rcz is not None
            dct_km = _dct(rcz, lops)
        else:
            dct_km = 500.0
    if dcr_km is None:
        if omega >= 0.75: # otherwise dct and dcr are not used
            assert rcz is not None
            dcr_km = _dcr(rcz, lops)
        else:
            dcr_km = 500.0

    dlt, dlr, thetat, thetar, theta, hstd, hsrd, hte, hre, hm =_path_profile_parameters(f_ghz,
                                                                htg_m, hrg_m, d_km, h_mamsl, ae)
    lbfs, lb0p, lb0b = _los_propagation_loss(f_ghz, p_percent, b0, hts, hrs, dn, dlt, dlr)
    ldp, lbd50, lbd = _diffraction_loss(f_ghz, p_percent, b0, hts, hrs, vpol, ae, ab, d_km, g,
                                        omega, hstd, hsrd, lbfs, lb0p)
    lbs = _troposcatter_loss(f_ghz, p_percent, dn, theta, n0)
    lba = _ducting_layer_reflection_loss(f_ghz, p_percent, ae, b0, dlm, dn, hts, hrs, dlt, dlr,
                                         thetat, thetar, hte, hre, hm, omega, dct_km, dcr_km)
    lbc = _50p_loc_basic_transmission_loss(p_percent, b0, dn, theta, omega, lb0p, lb0b, ldp, lbd50,
                                           lba, lbd, lbs)
    lb = _basic_transmission_loss(f_ghz, wa_m, pl_percent, hrg_m, r, lb0p, lbc)

    return lb


def field_strength(f_ghz: float, lb_db: float) -> float:
    """
    The field strength exceeded for p_percent time and pl_percent locations.

    Args:
        f_ghz (float): Frequency (GHz), with 0.03 <= f_ghz <= 6.0.
        lb_db (float): Basic transmission loss (dB), obtained from the basic_transmission_loss()
            function.

    Returns:
        Ep (float): The field strength normalized to 1 kW effective radiated power exceeded for
            p_percent time and pl_percent locations (dBuVm).
    """
    return 199.36 + 20.0*log10(f_ghz) - lb_db


def _input_validattion(f_ghz: float, p_percent: float, pl_percent: float, htg_m: float,
                       hrg_m: float,d_km: types.FloatArray, h_mamsl: types.FloatArray,
                       cc: types.IntArray|None, rch_m: types.FloatArray|None,
                       rcz: types.IntArray|None) -> None:
    if f_ghz < 0.03 or f_ghz > 6.0:
        # warning to allow experimental use of out of range frequencies
        warn('f_ghz is out of range.')
    if p_percent < 1.0 or p_percent > 50.0:
        raise ValueError('p_percent is out of range.')
    if pl_percent < 1.0 or pl_percent > 99.0:
        raise ValueError('pl_percent is out of range.')
    if htg_m < 1.0 or htg_m > 3000.0:
        raise ValueError('htg_m is out of range.')
    if hrg_m < 1.0 or hrg_m > 3000.0:
        raise ValueError('hrg_m is out of range.')
    n = len(d_km)
    if n < 3:
        raise ValueError('d_km must contain at least 3 distances.')
    if len(h_mamsl) != n:
        raise ValueError('Unexpected number of items in h_mamsl.')
    if cc is not None:
        if len(cc) != n:
            raise ValueError('Unexpected number of items in cc.')
    if rch_m is not None:
        if len(rch_m) != n:
            raise ValueError('Unexpected number of items in rch_m.')
    if rcz is not None:
        if len(rcz) != n:
            raise ValueError('Unexpected number of items in rcz.')


def _length_of_path_sections_profile(d: types.FloatArray) -> list[float]:
    """
    Args:
        d (types.FloatArray): Distance from transmitter profile of n points (km).

    Returns:
        lops (list[float]): Length of path sections of n points (km).
    """
    n = len(d)
    lops = [(d[1] - d[0]) / 2.0]

    for i in range(1, n - 1):
        lops.append((d[i] - d[i - 1]) / 2.0 + (d[i + 1] - d[i]) / 2.0)

    lops.append((d[n - 1] - d[n - 2]) / 2.0)

    return lops


def _g_profile(h: types.FloatArray, cc: types.IntArray | None, rch: types.FloatArray | None,
               sh: types.FloatArray | None) -> tuple[list[float], float]:
    """
    ITU-R P.1812-8, Annex 1, Section 3.2.

    Args:
        h (types.FloatArray): Terrain height profile of n points (m above mean sea level).
        cc (types.IntArray | None): Clutter category profile of n points, as defined by
            ClutterCategory. If set to None, OPEN_RURAL is assumed.
        rch (types.FloatArray | None): Representative clutter height profile of n points (m).
            If set to None, cc is used to determine the representative clutter height.
        sh (types.FloatArray | None): Surface height profile of n points (m). If set to None,
            rch or cc is used to determine the surface height.

    Returns:
        g (list[float]): Terrain height (m amsl) + representative clutter height (m) of n
            elements.
        r (float): Height of representative clutter at the receiver/mobile location (m).
    """
    n = len(h)
    g = [h[0]]

    if sh is not None:
        for i in range(1, n - 1):
            g.append(sh[i])
        r = sh[n - 1] - h[n - 1]
    elif rch is not None:
        for i in range(1, n - 1):
            g.append(h[i] + rch[i])
        r = rch[n - 1]
    elif cc is not None:
        for i in range(1, n - 1):
            g.append(h[i] + _repr_height(cc[i]))
        r = _repr_height(cc[n - 1])
    else:
        open_rural_rch = 0.0
        for i in range(1, n - 1):
            g.append(h[i] + open_rural_rch)
        r = open_rural_rch

    g.append(h[n - 1])

    return g, r


def _repr_height(cc: int) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 3.2 (TABLE 2).

    Args:
        cc (int): Clutter category, as defined by ClutterCategory.

    Returns:
        height (float): Representative clutter height (m).

    Raises:
        ValueError: If cc is not a recognized ClutterCategory value.
    """
    _REPR_HEIGHT = {
        ClutterCategory.WATER_SEA.value:          0.0,
        ClutterCategory.OPEN_RURAL.value:         0.0,
        ClutterCategory.SUBURBAN.value:           10.0,
        ClutterCategory.URBAN_TREES_FOREST.value: 15.0,
        ClutterCategory.DENSE_URBAN.value:        20.0,
    }

    if cc not in _REPR_HEIGHT:
        raise ValueError(f'Unknown ClutterCategory value: {cc}')

    return _REPR_HEIGHT[cc]


def _dct(rcz: types.IntArray, lops: list[float]) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 3.4.

    Args:
        rcz (types.IntArray): Radio climatic zone profile of n points, as defined by
            RadioClimaticZone.
        lops (list[float]): Length of path sections profile of n points (km).

    Returns:
        dct (float): Distance of the transmitter from the coast in the direction of the receiver.
            For a terminal on a ship or sea platform the distance is zero (km).
    """
    n = len(lops)
    dct = 0.0

    for i in range(n):
        if rcz[i] != RadioClimaticZone.SEA.value:
            dct += lops[i]
        else:
            break

    return dct


def _dcr(rcz: types.IntArray, lops: list[float]) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 3.4.

    Args:
        rcz (types.IntArray): Radio climatic zone profile of n points, as defined by
            RadioClimaticZone.
        lops (list[float]): Length of path sections profile of n points (km).

    Returns:
        dcr (float): Distance of the receiver from the coast in the direction of the transmitter.
            For a terminal on a ship or sea platform the distance is zero (km).
    """
    n = len(lops)
    dcr = 0.0

    for i in range(n):
        if rcz[n - 1 - i] != RadioClimaticZone.SEA.value:
            dcr += lops[n - 1 - i]
        else:
            break

    return dcr


def dn50(lat: float, lon: float) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 3.5.

    Get value from the DN50 digital map.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        float: Median annual radio-refractivity lapse-rate through the lowest 1 km of the
            atmosphere (N-units/km)
    """
    # lat from +90 to -90, lon from 0 to 360
    lat_interval = 1.5
    lon_interval = 1.5
    num_rows = 121 # (180/1.5)+1
    row_size = 241 # (360/1.5)+1

    if lon < 0.0:
        lon += 360.0
    r = (90.0 - lat) / lat_interval
    c = lon / lon_interval
    arr = _thread_safe_get_dn50_array()

    return p1144_13.square_grid_bilinear_interpolation(arr, num_rows, row_size, r, c)


def n050(lat: float, lon: float) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 3.5.

    Get value from the N050 digital map.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        float: Median annual sea-level surface refractivity (N-units).
    """
    # lat from +90 to -90, lon from 0 to 360
    lat_interval = 1.5
    lon_interval = 1.5
    num_rows = 121 # (180/1.5)+1
    row_size = 241 # (360/1.5)+1

    if lon < 0.0:
        lon += 360.0
    r = (90.0 - lat) / lat_interval
    c = lon / lon_interval
    arr = _thread_safe_get_n050_array()

    return p1144_13.square_grid_bilinear_interpolation(arr, num_rows, row_size, r, c)


def _longest_continuous_land(dn: float, rcz: types.IntArray | None, lops: list[float]
                             ) -> tuple[float, float]:
    """
    ITU-R P.1812-8, Annex 1, Section 3.6.

    Args:
        dn (float): Great-circle path distance (km).
        rcz (types.IntArray | None): Radio climatic zone profile of n points. If set to None, INLAND
            is assumed.
        lops (list[float]): Length of path sections profile of n points (km).

    Returns:
        dtm (float): Longest continuous land (inland + coastal) section of the great-circle
            path (km).
        dlm (float): Longest continuous inland section of the great-circle path (km).

    Raises:
        ValueError: If rcz contains an unrecognized RadioClimaticZone value.
    """
    dtm = 0.0
    dlm = 0.0

    if rcz is None:
        dtm = dlm = dn  # assumes INLAND for whole path
    else:
        n = len(lops)
        temp_dtm = 0.0
        temp_dlm = 0.0

        for i in range(n):
            if rcz[i] == RadioClimaticZone.INLAND.value:
                temp_dtm += lops[i]
                temp_dlm += lops[i]
            elif rcz[i] == RadioClimaticZone.COASTAL_LAND.value:
                temp_dtm += lops[i]
                dlm = max(dlm, temp_dlm)
                temp_dlm = 0.0
            elif rcz[i] == RadioClimaticZone.SEA.value:
                dtm = max(dtm, temp_dtm)
                temp_dtm = 0.0
                dlm = max(dlm, temp_dlm)
                temp_dlm = 0.0
            else:
                raise ValueError(f'Unknown RadioClimaticZone value: {rcz[i]}')

        dtm = max(dtm, temp_dtm)
        dlm = max(dlm, temp_dlm)

    return dtm, dlm


def _b0(lat: float, dtm: float, dlm: float) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 3.6.

    Args:
        lat (float): Path centre latitude (degrees).
        dtm (float): Longest continuous land (inland + coastal) section of the great-circle
            path (km).
        dlm (float): Longest continuous inland section of the great-circle path (km).

    Returns:
        b0 (float): Time percentage for which refractivity lapse-rates exceeding 100 N-units/km
            can be expected in the first 100 m of the lower atmosphere (%).
    """
    abs_lat = fabs(lat)
    tau = 1 - exp(-0.000412 * pow(dlm, 2.41))
    u1 = pow(pow(10.0, -dtm / (16 - 6.6 * tau)) + pow(10.0, -5.0 * (0.496 + 0.354 * tau)), 0.2)
    u1 = min(u1, 1.0)

    if abs_lat <= 70:
        u4 = pow(u1, -0.935 + 0.0176 * abs_lat)
        b0 = pow(10.0, -0.015 * abs_lat + 1.67) * u1 * u4
    else:
        u4 = pow(u1, 0.3)
        b0 = 4.17 * u1 * u4

    return b0


def _effective_earth_radius(delta_n: float) -> tuple[float, float]:
    """
    ITU-R P.1812-8, Annex 1, Section 3.7.

    Args:
        delta_n (float): Average radio-refractivity lapse-rate through the lowest 1 km of the
            atmosphere (N-units/km).

    Returns:
        ae (float): Median value of effective Earth radius for specified path (km).
        ab (float): Effective Earth radius exceeded for B0 time (km).
    """
    a = 6371.0
    k50 = 157.0 / (157.0 - delta_n)
    ae = k50 * a
    ab = 3.0 * a

    return ae, ab


def _over_water_percent(dn: float, rcz: types.IntArray | None, lops: list[float]) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 4.1.

    Args:
        dn (float): Great-circle path distance between transmit and receive antennas (km).
        rcz (types.IntArray | None): Radio climatic zone profile of n points. If set to None, INLAND
            is assumed.
        lops (list[float]): Length of path sections profile of n points (km).

    Returns:
        omega (float): Fraction of the total path over water [0, 1].
    """
    n = len(lops)
    db = 0.0  # aggregate length of the path sections over water (km)
    water_section_count = 0

    if rcz is not None:
        for i in range(n):
            if rcz[i] == RadioClimaticZone.SEA.value:
                db += lops[i]
                water_section_count += 1

    if water_section_count == n:
        omega = 1.0  # to make sure omega is set to exactly 1.0
    else:
        omega = db / dn

    return omega


def _los_propagation_loss(f: float, p: float, b0: float, hts: float, hrs: float, dn: float,
                          dlt: float, dlr: float) -> tuple[float, float, float]:
    """
    ITU-R P.1812-8, Annex 1, Section 4.2.

    Args:
        f (float): Frequency (GHz).
        p (float): Percentage of average year for which the calculated signal level is
            exceeded (%).
        b0 (float): Time percentage for which refractivity lapse-rates exceeding 100 N-units/km
            can be expected in the first 100 m of the lower atmosphere (%).
        hts (float): Transmit antenna centre height above mean sea level (m).
        hrs (float): Receive antenna centre height above mean sea level (m).
        dn (float): Great-circle path distance (km).
        dlt (float): Transmitting antenna horizon distance (km).
        dlr (float): Receiving antenna horizon distance (km).

    Returns:
        lbfs (float): Basic transmission loss due to free-space propagation (dB).
        lb0p (float): Basic transmission loss not exceeded for time percentage p%, due to LoS
            propagation (dB).
        lb0b (float): Basic transmission loss not exceeded for time percentage B0%, due to LoS
            propagation (dB).
    """
    delta_h = (hts - hrs) / 1000.0
    es = 2.6 * (1 - exp(-(dlt + dlr) / 10.0))

    dfs = sqrt(dn * dn + delta_h * delta_h) # distance between transmit and receive antennas (km)
    lbfs = 92.4 + 20 * log10(f) + 20 * log10(dfs)

    esp = es * log10(p / 50.0) # correction for multipath and focusing effects at p% time (dB)
    lb0p = lbfs + esp

    esb = es * log10(b0 / 50.0) # correction for multipath and focusing effects at B0% time (dB)
    lb0b = lbfs + esb

    return lbfs, lb0p, lb0b


def _bullington_diffraction_loss(f: float, htc: float, hrc: float, ce: float,
                                 d: types.FloatArray, g: list[float]) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 4.3.1.

    Args:
        f (float): Frequency (GHz).
        htc (float): Transmitting antenna height (m).
        hrc (float): Receiving antenna height (m).
        ce (float): Effective Earth curvature (1/km).
        d (types.FloatArray): Distance from transmitter profile of n points (km).
        g (list[float]): Terrain height (m amsl) + representative clutter height (m) profile
            of n points.

    Returns:
        lbull (float): Bullington diffraction loss (dB).
    """
    n = len(d)
    dn = d[n - 1]
    lam = _wavelength(f)

    stim = -inf
    for i in range(1, n - 1):
        stim = max(stim, (g[i] + 500.0 * ce * d[i] * (dn - d[i]) - htc) / d[i])
    str_ = (hrc - htc) / dn

    if stim < str_:  # if diffraction path is LoS
        vmax = -inf
        for i in range(1, n - 1):
            vmax = max(vmax, (g[i] + 500.0 * ce * d[i] * (dn - d[i])
                              - (htc * (dn - d[i]) + hrc * d[i]) / dn)
                       * sqrt(0.002 * dn / (lam * d[i] * (dn - d[i]))))
        v = vmax
    else:  # else diffraction path is transhorizon
        srim = -inf
        for i in range(1, n - 1):
            srim = max(srim, (g[i] + 500.0 * ce * d[i] * (dn - d[i]) - hrc) / (dn - d[i]))
        dbp = (hrc - htc + srim * dn) / (stim + srim)
        vb = (htc + stim * dbp - (htc * (dn - dbp) + hrc * dbp) / dn) \
            * sqrt(0.002 * dn / (lam * dbp * (dn - dbp)))
        v = vb

    if v <= -0.78:
        luc = 0
    else:
        luc = 6.9 + 20.0 * log10(sqrt(pow(v - 0.1, 2) + 1.0) + v - 0.1)

    lbull = luc + (1.0 - exp(-luc / 6.0)) * (10.0 + 0.02 * dn)

    return lbull


def _spherical_earth_diffraction_loss(f: float, vpol: bool, dn: float, ap: float, omega: float,
                                      htesph: float, hresph: float) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 4.3.2.

    Args:
        f (float): Frequency (GHz).
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.
        dn (float): Great-circle path distance between transmit and receive antennas (km).
        ap (float): General effective Earth radius (km).
        omega (float): Fraction of the total path over water.
        htesph (float): Effective transmitting antenna height (m).
        hresph (float): Effective receiving antenna height (m).

    Returns:
        ldsph (float): Spherical Earth diffraction loss (dB).
    """
    dlos = sqrt(2 * ap) * (sqrt(0.001 * htesph) + sqrt(0.001 * hresph))

    if dn >= dlos:
        ldsph = _first_term_spherical_earth_diffraction_loss(f, vpol, dn, ap, omega, htesph,
                                                             hresph)
    else:
        mc = 250.0 * dn * dn / (ap * (htesph + hresph))
        c_ = (htesph - hresph) / (htesph + hresph)
        b = 2.0 * sqrt((mc + 1.0) / (3.0 * mc)) \
            * cos(pi / 3.0 + 1.0 / 3.0 * acos(3.0 * c_ / 2.0
            * sqrt(3.0 * mc / pow(mc + 1.0, 3))))
        dse1 = dn * (1.0 + b) / 2.0
        dse2 = dn - dse1
        hse = ((htesph - 500.0 * dse1 * dse1 / ap) * dse2 \
               + (hresph - 500.0 * dse2 * dse2 / ap) * dse1) / dn
        hreq = 17.456 * sqrt(dse1 * dse2 * _wavelength(f) / dn)

        if hse > hreq:
            ldsph = 0
        else:
            x = dn / (sqrt(htesph) + sqrt(hresph))
            aem = 500.0 * x * x
            ldft = _first_term_spherical_earth_diffraction_loss(f, vpol, dn, aem, omega, htesph,
                                                                hresph)
            if ldft < 0:
                ldsph = 0
            else:
                ldsph = (1.0 - (hse / hreq)) * ldft

    return ldsph


def _first_term_spherical_earth_diffraction_loss(f: float, vpol: bool, dn: float, adft: float,
                                                 omega: float, htesph: float,
                                                 hresph: float) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 4.3.3.

    Args:
        f (float): Frequency (GHz).
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.
        dn (float): Great-circle path distance between transmit and receive antennas (km).
        adft (float): Effective Earth radius (km).
        omega (float): Fraction of the total path over water.
        htesph (float): Effective transmitting antenna height (m).
        hresph (float): Effective receiving antenna height (m).

    Returns:
        ldft (float): First term spherical Earth diffraction loss (dB).
    """
    ldft_land = 0.0
    ldft_sea = 0.0

    if omega != 1.0:
        ldft_land = _first_term_sub_calculation(f, vpol, dn, adft, 22.0, 0.003, htesph, hresph)
    if omega != 0.0:
        ldft_sea = _first_term_sub_calculation(f, vpol, dn, adft, 80.0, 5.0, htesph, hresph)
    ldft = omega * ldft_sea + (1.0 - omega) * ldft_land

    return ldft


def _first_term_sub_calculation(f: float, vpol: bool, dn: float, adft: float, perm: float,
                                conduct: float, htesph: float, hresph: float) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 4.3.3.

    Args:
        f (float): Frequency (GHz).
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.
        dn (float): Great-circle path distance between transmit and receive antennas (km).
        adft (float): Effective Earth radius (km).
        perm (float): Terrain relative permittivity.
        conduct (float): Terrain conductivity (S/m).
        htesph (float): Effective transmitting antenna height (m).
        hresph (float): Effective receiving antenna height (m).

    Returns:
        ldft (float): First term spherical Earth diffraction loss (dB).
    """
    k = 0.036 * pow(adft * f, -1.0 / 3.0) \
        * pow(pow(perm - 1.0, 2) + pow(18.0 * conduct / f, 2), -0.25)
    if vpol:
        k *= sqrt(pow(perm, 2) + pow(18.0 * conduct / f, 2))

    k2 = k * k
    k4 = k2 * k2
    bdft = (1.0 + 1.6 * k2 + 0.67 * k4) / (1.0 + 4.5 * k2 + 1.53 * k4)

    x = 21.88 * bdft * pow(f / (adft * adft), 1.0 / 3.0) * dn

    yt = yr = 0.9575 * bdft * pow(f * f / adft, 1.0 / 3.0)
    yt *= htesph
    yr *= hresph

    if x >= 1.6:
        fx = 11.0 + 10.0 * log10(x) - 17.6 * x
    else:
        fx = -20.0 * log10(x) - 5.6488 * pow(x, 1.425)

    def g(y: float) -> float:
        b = bdft * y
        if b > 2:
            gy = 17.6 * sqrt(b - 1.1) - 5.0 * log10(b - 1.1) - 8.0
        else:
            gy = 20.0 * log10(b + 0.1 * b * b * b)
        return max(gy, 2.0 + 20.0 * log10(k))

    ldft = -fx - g(yt) - g(yr)

    return ldft


def _delta_bullington_diffraction_loss(f: float, htc: float, hrc: float, vpol: bool, ap: float,
                                       ce: float, d: types.FloatArray, g: list[float],
                                       omega: float, hstd: float, hsrd: float) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 4.3.4.

    Args:
        f (float): Frequency (GHz).
        htc (float): Transmitting antenna height (m).
        hrc (float): Receiving antenna height (m).
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.
        ap (float): General effective Earth radius (km).
        ce (float): Effective Earth curvature (1/km).
        d (types.FloatArray): Distance from transmitter profile of n points (km).
        g (list[float]): Terrain height (m amsl) + representative clutter height (m) profile of n
            points.
        omega (float): Fraction of the total path over water.
        hstd (float): Modified smooth-Earth surface at the transmitting station location (m amsl).
        hsrd (float): Modified smooth-Earth surface at the receiving station location (m amsl).

    Returns:
        ld (float): Complete "delta-Bullington" diffraction loss (dB).
    """
    g0 = [0.0] * len(d)

    lbulla = _bullington_diffraction_loss(f, htc, hrc, ce, d, g)
    htc_prime = htc - hstd
    hrc_prime = hrc - hsrd
    lbulls = _bullington_diffraction_loss(f, htc_prime, hrc_prime, ce, d, g0)
    ldsph = _spherical_earth_diffraction_loss(f, vpol, d[-1], ap, omega, htc_prime, hrc_prime)
    ld = lbulla + max(ldsph - lbulls, 0.0)

    return ld


def _diffraction_loss(f: float, p: float, b0: float, htc: float, hrc: float, vpol: bool,
                      ae: float, ab: float, d: types.FloatArray, g: list[float], omega: float,
                      hstd: float, hsrd: float, lbfs: float, lb0p: float
                      ) -> tuple[float, float, float]:
    """
    ITU-R P.1812-8, Annex 1, Section 4.3.5.

    Args:
        f (float): Frequency (GHz).
        p (float): Percentage of average year for which the calculated basic transmission loss is
            not exceeded (%).
        b0 (float): Time percentage for which refractivity lapse-rates exceeding 100 N-units/km
            can be expected in the first 100 m of the lower atmosphere (%).
        htc (float): Transmitting antenna height (m).
        hrc (float): Receiving antenna height (m).
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.
        ae (float): Median effective Earth radius (km).
        ab (float): Effective Earth radius exceeded for B0 time (km).
        d (types.FloatArray): Distance from transmitter profile of n points (km).
        g (list[float]): Terrain height (m amsl) + representative clutter height (m) profile of n
            points.
        omega (float): Fraction of the total path over water.
        hstd (float): Modified smooth-Earth surface at the transmitting station location (m amsl).
        hsrd (float): Modified smooth-Earth surface at the receiving station location (m amsl).
        lbfs (float): Basic transmission loss due to free-space propagation (dB).
        lb0p (float): Basic transmission loss not exceeded for time percentage p%, due to LoS
            propagation (dB).

    Returns:
        ldp (float): Diffraction loss not exceeded for p% time (dB).
        lbd50 (float): Median basic transmission loss associated with diffraction (dB).
        lbd (float): Basic transmission loss associated with diffraction not exceeded for p%
            time (dB).
    """
    ld50 = _delta_bullington_diffraction_loss(f, htc, hrc, vpol, ae, 1.0 / ae, d, g, omega,
                                              hstd, hsrd)

    if 49.99 < p < 50.01:  # if roughly evaluates to 50%
        ldp = ld50
    else:
        ldb = _delta_bullington_diffraction_loss(f, htc, hrc, vpol, ab, 1.0 / ab, d, g, omega,
                                                 hstd, hsrd)
        if p > b0:
            fi = _I(p / 100.0) / _I(b0 / 100.0)
        else:
            fi = 1
        ldp = ld50 + (ldb - ld50) * fi

    lbd50 = lbfs + ld50
    lbd = lb0p + ldp

    return ldp, lbd50, lbd


def _troposcatter_loss(f: float, p: float, dn: float, theta: float, n0: float) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 4.4.

    Args:
        f (float): Frequency (GHz), with 0.03 <= f <= 6.0.
        p (float): Percentage of average year for which the calculated basic transmission loss is
            not exceeded (%), with 1.0 <= p <= 50.0.
        dn (float): Great-circle path distance between transmit and receive antennas (km).
        theta (float): Path angular distance (mrad).
        n0 (float): Sea-level surface refractivity (N-units).

    Returns:
        lbs (float): Basic transmission loss due to troposcatter (dB).
    """
    lf = 25.0 * log10(f) - 2.5 * log10(f / 2.0) * log10(f / 2.0)
    lbs = 190.1 + lf + 20.0 * log10(dn) + 0.573 * theta - 0.15 * n0 \
          - 10.125 * pow(log10(50.0 / p), 0.7)

    return lbs


def _ducting_layer_reflection_loss(f: float, p: float, ae: float, b0: float, dlm: float,
                                   dn: float, hts: float, hrs: float, dlt: float, dlr: float,
                                   thetat: float, thetar: float, hte: float, hre: float,
                                   hm: float, omega: float, dct: float, dcr: float) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 4.5.

    Args:
        f (float): Frequency (GHz).
        p (float): Percentage of average year for which the calculated basic transmission loss is
            not exceeded (%).
        ae (float): Median effective Earth radius (km).
        b0 (float): Time percentage for which refractivity lapse-rates exceeding 100 N-units/km
            can be expected in the first 100 m of the lower atmosphere (%).
        dlm (float): Longest continuous inland section of the great-circle path (km).
        dn (float): Great-circle path distance (km).
        hts (float): Transmit antenna centre height above mean sea level (m).
        hrs (float): Receive antenna centre height above mean sea level (m).
        dlt (float): Transmitting antenna horizon distance (km).
        dlr (float): Receiving antenna horizon distance (km).
        thetat (float): Transmit horizon elevation angle (mrad).
        thetar (float): Receive horizon elevation angle (mrad).
        hte (float): Effective height of the transmitting antenna for the ducting/layer-reflection
            model (m).
        hre (float): Effective height of the receiving antenna for the ducting/layer-reflection
            model (m).
        hm (float): Terrain roughness (m).
        omega (float): Fraction of the total path over water.
        dct (float): Distance of the transmitter from the coast in the direction of the receiver.
            For a terminal on a ship or sea platform the distance is zero (km).
        dcr (float): Distance of the receiver from the coast in the direction of the transmitter.
            For a terminal on a ship or sea platform the distance is zero (km).

    Returns:
        lba (float): Basic transmission loss associated with ducting/layer-reflection not exceeded
            for p% time (dB).
    """
    # calculations for Af
    theta_ppt = thetat - 0.1 * dlt
    theta_ppr = thetar - 0.1 * dlr
    ast = asr = 0.0
    if theta_ppt > 0:
        ast = 20.0 * log10(1.0 + 0.361 * theta_ppt * sqrt(f * dlt)) \
              + 0.264 * theta_ppt * pow(f, 1.0 / 3.0)
    if theta_ppr > 0:
        asr = 20.0 * log10(1.0 + 0.361 * theta_ppr * sqrt(f * dlr)) \
              + 0.264 * theta_ppr * pow(f, 1.0 / 3.0)
    act = acr = 0.0
    if omega >= 0.75:
        if dct <= dlt and dct <= 5.0:
            act = -3.0 * exp(-0.25 * dct * dct) * (1.0 + tanh(0.07 * (50.0 - hts)))
        if dcr <= dlr and dcr <= 5.0:
            acr = -3.0 * exp(-0.25 * dcr * dcr) * (1.0 + tanh(0.07 * (50.0 - hrs)))
    alf = 0.0
    if f < 0.5:
        alf = 45.375 - 137.0 * f + 92.5 * f * f
    af = 102.45 + 20.0 * log10(f) + 20.0 * log10(dlt + dlr) \
         + alf + ast + asr + act + acr

    # calculations for Ad(p)
    yd = 0.00005 * ae * pow(f, 1.0 / 3.0)
    theta_pt = min(thetat, 0.1 * dlt)
    theta_pr = min(thetar, 0.1 * dlr)
    theta_p = 1000.0 * dn / ae + theta_pt + theta_pr
    tau = 1 - exp(-0.000412 * pow(dlm, 2.41))
    alpha = -0.6 - tau * pow(dn, 3.1) * 3.5E-9
    alpha = max(alpha, -3.4)
    u2 = pow(500.0 / ae * dn * dn / pow(sqrt(hte) + sqrt(hre), 2), alpha)
    u2 = min(u2, 1.0)
    u3 = 1.0
    if hm > 10.0:
        di = min(dn - dlt - dlr, 40.0)
        u3 = exp(-4.6E-5 * (hm - 10.0) * (43.0 + 6.0 * di))
    b = b0 * u2 * u3
    log_b = log10(b)
    gamma = 1.076 / pow(2.0058 - log_b, 1.012) \
            * exp(-(9.51 - 4.8 * log_b + 0.198 * log_b * log_b) * 1.0E-6 * pow(dn, 1.13))
    ap = -12.0 + (1.2 + 0.0037 * dn) * log10(p / b) + 12.0 * pow(p / b, gamma)
    adp = yd * theta_p + ap

    lba = af + adp

    return lba


def _50p_loc_basic_transmission_loss(p: float, b0: float, dn: float, theta: float, omega: float,
                                     lb0p: float, lb0b: float, ldp: float, lbd50: float,
                                     lba: float, lbd: float, lbs: float) -> float:
    """
    ITU-R P.1812-8, Annex 1, Section 4.6.

    Args:
        p (float): Percentage of average year for which the calculated basic transmission loss is
            not exceeded (%), with 1.0 <= p <= 50.0.
        b0 (float): Time percentage for which refractivity lapse-rates exceeding 100 N-units/km
            can be expected in the first 100 m of the lower atmosphere (%).
        dn (float): Great-circle path distance between transmit and receive antennas (km).
        theta (float): Path angular distance (mrad).
        omega (float): Fraction of the total path over water.
        lb0p (float): Notional LoS basic transmission loss not exceeded for p% time (dB).
        lb0b (float): Notional LoS basic transmission loss not exceeded for B0% time (dB).
        ldp (float): Diffraction loss not exceeded for p% time (dB).
        lbd50 (float): Median basic transmission loss associated with diffraction (dB).
        lba (float): Ducting/layer-reflection basic transmission loss not exceeded for p%
            time (dB).
        lbd (float): Basic transmission loss for diffraction not exceeded for p% time (dB).
        lbs (float): Basic transmission loss due to troposcatter (dB).

    Returns:
        lbc (float): Basic transmission loss not exceeded for p% time and 50% locations (dB).
    """
    if p < b0:
        lminb0p = lb0p + (1.0 - omega) * ldp
    else:
        if p > b0:
            fi = _I(p / 100.0) / _I(b0 / 100.0)
        else:
            fi = 1
        lminb0p = lbd50 + (lb0b + (1.0 - omega) * ldp - lbd50) * fi

    lminbap = 2.5 * ln(exp(lba / 2.5) + exp(lb0p / 2.5))

    if lminbap > lbd:
        lbda = lbd
    else:
        fk = 1.0 - 0.5 * (1.0 + tanh(3.0 * 0.5 * (dn - 20.0) / 20.0))
        lbda = lminbap + (lbd - lminbap) * fk

    fj = 1.0 - 0.5 * (1.0 + tanh(3.0 * 0.8 * (theta - 0.3) / 0.3))
    lbam = lbda + (lminb0p - lbda) * fj

    lbc = -5.0 * log10(pow(10.0, -0.2 * lbs) + pow(10.0, -0.2 * lbam))

    return lbc


def _basic_transmission_loss(f: float, wa: float, pl: float, hrg: float, r: float, lb0p: float,
                             lbc: float) -> float:
    """
    ITU-R P.1812-8, Annex 1, Sections 4.7 & 4.9.

    Args:
        f (float): Frequency (GHz).
        wa (float): Prediction resolution (m), the width of the square area over which the
            location variability applies.
        pl (float): Percentage of locations for which the calculated signal level is exceeded (%),
            with 1.0 <= pl <= 99.0.
        hrg (float): Receive antenna centre height above ground level (m).
        r (float): Height of representative clutter at the receiver/mobile location (m).
        lb0p (float): Basic transmission loss not exceeded for p% time and 50% locations
            associated with LoS with short term enhancements (dB).
        lbc (float): Basic transmission loss not exceeded for p% of time and 50% locations,
            including the effects of terminal clutter losses (dB).

    Returns:
        lb (float): Basic transmission loss not exceeded for p% time and pL% locations (dB).
    """
    sigma_l = (0.024 * f + 0.52) * pow(wa, 0.28)

    if hrg < r:
        uh = 1.0
    elif hrg < r + 10.0:
        uh = 1.0 - (hrg - r) / 10.0
    else:
        uh = 0.0

    # assumes outdoors
    lloc = 0.0
    sigma_loc = uh * sigma_l

    lb = max(lb0p, lbc + lloc - _I(pl / 100.0) * sigma_loc)

    return lb


def _path_profile_parameters(f: float, htg: float, hrg: float, d: types.FloatArray,
                             h: types.FloatArray, ae: float
                             ) -> tuple[float, float, float, float, float, float, float, float,
                                        float, float]:
    """
    ITU-R P.1812-8, Attachment 1 to Annex 1, Section 4 & 5.

    Args:
        f (float): Frequency (GHz).
        htg (float): Transmit antenna centre height above ground level (m).
        hrg (float): Receive antenna centre height above ground level (m).
        d (types.FloatArray): Distance from transmitter profile of n elements (km).
        h (types.FloatArray): Terrain height profile of n elements (m above mean sea level).
        ae (float): Median effective Earth radius (km).

    Returns:
        dlt (float): Transmitting antenna horizon distance (km).
        dlr (float): Receiving antenna horizon distance (km).
        thetat (float): Transmit horizon elevation angle (mrad).
        thetar (float): Receive horizon elevation angle (mrad).
        theta (float): Path angular distance (mrad).
        hstd (float): Modified hst for the diffraction model (m amsl).
        hsrd (float): Modified hsr for the diffraction model (m amsl).
        hte (float): Effective height of the transmitting antenna for the ducting/layer-reflection
            model (m).
        hre (float): Effective height of the receiving antenna for the ducting/layer-reflection
            model (m).
        hm (float): Terrain roughness (m).
    """
    n = len(d)
    hts = h[0] + htg
    hrs = h[n - 1] + hrg
    dn = d[n - 1]

    theta_max, theta_max_dist_index = _max_tx_to_terrain_elevation_angle(hts, d, h, ae)
    theta_td = _elevation_angle(hts, hrs, dn, ae) # elevation angle from tx to rx antennas (mrad)
    is_los = not (theta_max > theta_td)
    thetat = max(theta_max, theta_td)

    if not is_los:
        ilt = theta_max_dist_index
    else:
        ce = 1.0 / ae  # section 3.8 of Annex 1 mentions to use ae for the path profile analysis
        ilt = _los_max_diffraction_dist(f, hts, hrs, d, h, ce)
    dlt = d[ilt]

    if is_los:
        thetar = _elevation_angle(hrs, hts, dn, ae) # elevation angle from rx to tx antennas (mrad)
        dlr = dn - dlt
        ilr = ilt
    else:
        thetar, ilr = _max_rx_to_terrain_elevation_angle(hrs, d, h, ae)
        dlr = dn - d[ilr]

    theta = (1000 * dn / ae) + thetat + thetar

    hst, hsr = _smooth_earth_heights(d, h)
    hstd, hsrd = _smooth_earth_heights_for_diffraction_model(hts, hrs, d, h, hst, hsr)
    hte, hre, hm = _effective_heights_and_terrain_roughness(htg, hrg, d, h, hst, hsr, ilt, ilr)

    return dlt, dlr, thetat, thetar, theta, hstd, hsrd, hte, hre, hm


def _elevation_angle(hamsl_from: float, hamsl_to: float, dist_km: float, ae: float) -> float:
    """
    ITU-R P.1812-8, Attachment 1 to Annex 1, Section 4 & 5.3.

    Args:
        hamsl_from (float): Height of location from which the elevation angle is to be
            calculated (m above mean sea level).
        hamsl_to (float): Height of location to which the elevation angle is to be
            calculated (m above mean sea level).
        dist_km (float): Great-circle path distance between the two aforementioned locations (km).
        ae (float): Median effective Earth radius (km).

    Returns:
        theta (float): Elevation angle above local horizontal (mrad).
    """
    return 1000.0 * atan(((hamsl_to - hamsl_from) / (1000.0 * dist_km)) - (dist_km / (2.0 * ae)))


def _max_tx_to_terrain_elevation_angle(hts: float, d: types.FloatArray, h: types.FloatArray,
                                       ae: float) -> tuple[float, int]:
    """
    ITU-R P.1812-8, Attachment 1 to Annex 1, Section 4.

    Args:
        hts (float): Transmit antenna height above mean sea level (m).
        d (types.FloatArray): Distance from transmitter profile of n elements (km).
        h (types.FloatArray): Terrain height profile of n elements (m above mean sea level).
        ae (float): Median effective Earth radius (km).

    Returns:
        theta_max (float): Physical horizon elevation angle as seen by the transmitting antenna
            (relative to the local horizontal) (mrad), i.e. maximum elevation angle from
            transmitting antenna to terrain elements.
        dindex (int): Index of distance to transmitter profile d for which theta_max was found.
    """
    n = len(d)
    theta_max = -inf
    dindex = 0

    for i in range(1, n - 1):  # excludes transmit and receive locations
        theta_i = _elevation_angle(hts, h[i], d[i], ae)
        if theta_i > theta_max:
            theta_max = theta_i
            dindex = i

    return theta_max, dindex


def _los_max_diffraction_dist(f: float, hts: float, hrs: float, d: types.FloatArray,
                              h: types.FloatArray, ce: float) -> int:
    """
    ITU-R P.1812-8, Attachment 1 to Annex 1, Section 5.2.

    Args:
        f (float): Frequency (GHz).
        hts (float): Transmit antenna height above mean sea level (m).
        hrs (float): Receive antenna height above mean sea level (m).
        d (types.FloatArray): Distance from transmitter profile of n elements (km).
        h (types.FloatArray): Terrain height profile of n elements (m above mean sea level).
        ce (float): Effective Earth curvature (1/km).

    Returns:
        dindex (int): Index of distance to transmitter profile d for which the maximum diffraction
            parameter was calculated.
    """
    n = len(d)
    dn = d[n - 1]
    vmax = -inf
    dindex = 0

    for i in range(1, n - 1):  # excludes transmit and receive locations
        di = d[i]
        vi = (h[i] + 500.0 * ce * di * (dn - di) - (hts * (dn - di) + hrs * di) / dn) \
             * sqrt(0.002 * dn / (_wavelength(f) * di * (dn - di)))
        if vi > vmax:
            vmax = vi
            dindex = i

    return dindex


def _max_rx_to_terrain_elevation_angle(hrs: float, d: types.FloatArray, h: types.FloatArray,
                                       ae: float) -> tuple[float, int]:
    """
    ITU-R P.1812-8, Attachment 1 to Annex 1, Section 5.3.

    Args:
        hrs (float): Receive antenna height above mean sea level (m).
        d (types.FloatArray): Distance from transmitter profile of n elements (km).
        h (types.FloatArray): Terrain height profile of n elements (m above mean sea level).
        ae (float): Median effective Earth radius (km).

    Returns:
        theta_max (float): Physical horizon elevation angle as seen by the receiving antenna
            (relative to the local horizontal) (mrad), i.e. maximum elevation angle from
            receiving antenna to terrain elements.
        dindex (int): Index of distance to transmitter profile d for which theta_max was found.
    """
    n = len(d)
    dn = d[n - 1]
    theta_max = -inf
    dindex = 0

    for j in range(1, n - 1):  # excludes transmit and receive locations
        theta_j = _elevation_angle(hrs, h[j], dn - d[j], ae)
        if theta_j > theta_max:
            theta_max = theta_j
            dindex = j

    return theta_max, dindex


def _smooth_earth_heights(d: types.FloatArray, h: types.FloatArray) -> tuple[float, float]:
    """
    ITU-R P.1812-8, Attachment 1 to Annex 1, Section 5.6.1.

    Args:
        d (types.FloatArray): Distance from transmitter profile of n elements (km).
        h (types.FloatArray): Terrain height profile of n elements (m above mean sea level).

    Returns:
        hst (float): Height of the smooth-Earth surface at the transmitting station location
            (m amsl).
        hsr (float): Height of the smooth-Earth surface at the receiving station location
            (m amsl).
    """
    n = len(d)
    v1 = 0.0
    v2 = 0.0
    dn = d[n - 1]

    for i in range(1, n):
        v1 += (d[i] - d[i - 1]) * (h[i] + h[i - 1])
        v2 += (d[i] - d[i-1]) * (h[i] * (2.0 * d[i] + d[i-1]) + h[i-1] * (d[i] + 2.0 * d[i-1]))

    hst = (2.0 * v1 * dn - v2) / (dn * dn)
    hsr = (v2 - v1 * dn) / (dn * dn)

    return hst, hsr


def _smooth_earth_heights_for_diffraction_model(hts: float, hrs: float, d: types.FloatArray,
                                                h: types.FloatArray, hst: float,
                                                hsr: float) -> tuple[float, float]:
    """
    ITU-R P.1812-8, Attachment 1 to Annex 1, Section 5.6.2.

    Args:
        hts (float): Transmit antenna height above mean sea level (m).
        hrs (float): Receive antenna height above mean sea level (m).
        d (types.FloatArray): Distance from transmitter profile of n elements (km).
        h (types.FloatArray): Terrain height profile of n elements (m above mean sea level).
        hst (float): Height of the smooth-Earth surface at the transmitting station location
            (m amsl).
        hsr (float): Height of the smooth-Earth surface at the receiving station location (m amsl).

    Returns:
        hstd (float): Modified hst for the diffraction model (m amsl).
        hsrd (float): Modified hsr for the diffraction model (m amsl).
    """
    n = len(d)
    htc = hts
    hrc = hrs
    hobs = -inf
    aobt = -inf
    aobr = -inf
    dn = d[n - 1]
    h1 = h[0]
    hn = h[n - 1]

    for i in range(1, n - 1):
        hi = h[i] - (htc * (dn - d[i]) + hrc * d[i]) / dn
        aobti = hi / d[i]
        aobri = hi / (dn - d[i])
        hobs = max(hobs, hi)
        aobt = max(aobt, aobti)
        aobr = max(aobr, aobri)

    if hobs <= 0:
        hstp = hst
        hsrp = hsr
    else:
        gt = aobt / (aobt + aobr)
        gr = aobr / (aobt + aobr)
        hstp = hst - hobs * gt
        hsrp = hsr - hobs * gr

    hstd = h1 if hstp > h1 else hstp
    hsrd = hn if hsrp > hn else hsrp

    return hstd, hsrd


def _effective_heights_and_terrain_roughness(htg: float, hrg: float, d: types.FloatArray,
                                             h: types.FloatArray, hst: float, hsr: float,
                                             ilt: int, ilr: int) -> tuple[float, float, float]:
    """
    ITU-R P.1812-8, Attachment 1 to Annex 1, Section 5.6.3.

    Args:
        htg (float): Transmit antenna centre height above ground level (m).
        hrg (float): Receive antenna centre height above ground level (m).
        d (types.FloatArray): Distance from transmitter profile of n elements (km).
        h (types.FloatArray): Terrain height profile of n elements (m above mean sea level).
        hst (float): Height of the smooth-Earth surface at the transmitting station location
            (m amsl).
        hsr (float): Height of the smooth-Earth surface at the receiving station location (m amsl).
        ilt (int): Index of the profile point at distance dlt from the transmitter.
        ilr (int): Index of the profile point at distance dlr from the receiver.

    Returns:
        hte (float): Effective height of the transmitting antenna for the ducting/layer-reflection
            model (m).
        hre (float): Effective height of the receiving antenna for the ducting/layer-reflection
            model (m).
        hm (float): Terrain roughness (i.e. maximum height of the terrain above the smooth-Earth
            surface in the section of the path between, and including, the horizon points) (m).
    """
    n = len(d)
    h1 = h[0]
    hn = h[n - 1]
    dn = d[n - 1]

    hst = min(hst, h1)
    hsr = min(hsr, hn)
    m = (hsr - hst) / dn
    hte = htg + h1 - hst
    hre = hrg + hn - hsr
    hm = -inf

    for i in range(ilt, ilr + 1):
        hmi = h[i] - (hst + m * d[i])
        hm = max(hm, hmi)

    return hte, hre, hm


def _I(x: float) -> float:
    """
    ITU-R P.1812-8, Attachment 2 to Annex 1.

    Args:
        x (float): Input value, clamped to [0.000001, 0.999999].

    Returns:
        float: Approximation to the inverse complementary cumulative normal distribution function.
    """
    C0 = 2.515516698
    C1 = 0.802853
    C2 = 0.010328
    D1 = 1.432788
    D2 = 0.189269
    D3 = 0.001308

    x = max(x, 0.000001)
    x = min(x, 0.999999)

    def _T(a: float) -> float:
        return sqrt(-2.0 * ln(a))

    def _Xi(b: float) -> float:
        tx = _T(b)
        return (((C2 * tx + C1) * tx) + C0) / (((D3 * tx + D2) * tx + D1) * tx + 1)

    if x <= 0.5:
        return _T(x) - _Xi(x)
    else:
        return _Xi(1.0 - x) - _T(1.0 - x)


def _wavelength(f_ghz: float) -> float:
    """
    Returns wavelength in meters.
    """
    c = 2.998E8 # Speed of propagation (m/s)
    return 1.0E-9*c/f_ghz


def _thread_safe_get_dn50_array() -> array:
    return _thread_safe_get_digital_map_array('dn50_lock', 'dn50_array', 'DN50.TXT')


def _thread_safe_get_n050_array() -> array:
    return _thread_safe_get_digital_map_array('n050_lock', 'n050_array', 'N050.TXT')


def _thread_safe_get_digital_map_array(lock_key: str, array_key: str, filename: str) -> array:
    arr = _p1812_8_shared[array_key]
    if arr is not None:
        return arr
    with _p1812_8_shared[lock_key]:
        arr = _p1812_8_shared[array_key] # re-read under lock
        if arr is None:
            try:
                arr = _load_digital_map(filename)
            except FileNotFoundError:
                _download_rec_data()
                arr = _load_digital_map(filename)
            _p1812_8_shared[array_key] = arr # only assign when load completed successfully
    return arr


def _load_digital_map(filename: str) -> array:
    return p1144_13.load_digital_map(join(_du.install_dir(),_p1812_8_shared['DATA_DIR'],
                                          filename))


def _download_rec_data() -> None:
    data_dir = _p1812_8_shared['DATA_DIR']
    full_path_data_dir = join(_du.install_dir(), data_dir)
    filenames = ['DN50.TXT', 'N050.TXT']
    lock = FileLock(_du.get_lockfile_pathname(data_dir))
    with lock:
        if _du.files_all_exist(full_path_data_dir, filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.1812-8-202509-I!!ZIP-E.zip'
            zip_pathname = _du.download(url, full_path_data_dir)
            _du.extract_files(zip_pathname, filenames, create_dirs=True, delete_zip_archive=True)
            _du.print_notice()


_p1812_8_shared = {
    'DATA_DIR': 'p1812_8',
    'dn50_lock': Lock(),
    'dn50_array': None,
    'n050_lock': Lock(),
    'n050_array': None
}
