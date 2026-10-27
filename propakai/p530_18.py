# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.530-18.

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite this software
    package along with the underlying ITU-R standard:

    * **ITU-R Standard:** International Telecommunication Union (2021).
      *Recommendation ITU-R P.530-18: Propagation data and prediction methods required for the
      design of terrestrial line-of-sight systems*. Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.530/en
"""

from os.path import join
from math import exp, log10, sqrt, tanh, radians, cos, log as ln
from enum import Enum
from typing import Callable, Any
from threading import Lock
from array import array
from filelock import FileLock
from propakai import _download_utils as _du
from propakai import p676_13
from propakai import p837_8
from propakai import p838_3
from propakai import p1144_13


__all__ = ['TimePeriod',
           'PathType',
           'atmospheric_gases_attenuation',
           'rain_attenuation_long_term_stats',
           'diffraction_loss_over_avg_terrain',
           'single_frequency_fading_distribution',
           'fading_distribution',
           'enhancement_distribution',
           'inverse_distribution',
           'avg_worst_month_to_shorter_worst_period']


class TimePeriod(Enum):
    """
    Enumerates possible time periods for fading/enhancement distributions.
    """
    AVG_WORST_MONTH = 1
    AVG_YEAR        = 2


class PathType(Enum):
    """
    ITU-R P.530-18, Annex 1, Section 2.3.5. Enumerates path types.
    """
    RELATIVELY_FLAT = 1
    HILLY           = 2
    HILLY_LAND      = 3


def atmospheric_gases_attenuation(d_km: float, f_ghz: float, p_hpa: float=1013.25,
                                  t_k: float=288.15, rho_gm3: float=7.5) -> float:
    """
    ITU-R P.530-18, Annex 1, Section 2.1.

    Terrestrial path attenuation due to absorption by oxygen and water vapour (dB).

    Args:
        d_km (float): Path length (km), with 0 <= d_km.
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000.
        p_hpa (float, optional): Atmospheric pressure (hPa). Defaults to 1013.25.
        t_k (float, optional): Temperature (K). Defaults to 288.15.
        rho_gm3 (float, optional): Water vapour density (g/m3). Defaults to 7.5.

    Returns:
        Aa (float): Terrestrial path attenuation due to absorption by oxygen and water vapour (dB).
    """
    return p676_13.terrestrial_path_gaseous_attenuation(d_km, f_ghz, p_hpa, t_k, rho_gm3)


def rain_attenuation_long_term_stats(f_ghz: float, d_km: float, p_percent: float,
                                     theta_deg: float, tau_deg: float,
                                     lat: float, lon: float) -> float:
    """
    ITU-R P.530-18, Annex 1, Sections 2.4.1.

    Calculates the rain attenuation over the specified path length, exceeded for p percent of
    time, based on yearly statistics (dB).

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 100.
        d_km (float): Path length (km), with 0 < d_km <= 60.
        p_percent (float): Annual time percentage (%), with 0.001 <= p_percent <= 1.
        theta_deg (float): Path elevation angle (degrees).
        tau_deg (float): Polarization tilt angle relative to the horizontal (degrees). Use 45° for
            circular polarization.
        lat (float): Latitude of the path location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the path location (degrees), with -180 <= lon <= 180.
    
    Returns:
        Ap (float): Rain attenuation over the specified path length, exceeded for p percent of
            time, based on yearly statistics (dB).
    """
    # Step 1
    R001 = p837_8.annual_rainfall_rate_001(lat, lon)

    # Step 2
    k, alpha = p838_3.coefficients(f_ghz, theta_deg, tau_deg)
    gamma_R = k*pow(R001, alpha)

    # Step 3
    r_inv = 0.477*pow(d_km, 0.633)*pow(R001, 0.073*alpha)*pow(f_ghz, 0.123) - \
            10.579*(1.0-exp(-0.024*d_km))
    r = 1.0/r_inv
    d_eff = d_km*r

    # Step 4
    A001 = gamma_R*d_eff

    # Step 5
    if f_ghz >= 10:
        C0 = 0.12 + 0.4*log10(pow(f_ghz/10.0, 0.8))
    else:
        C0 = 0.12
    C1 = pow(0.07, C0)*pow(0.12, 1.0-C0)
    C2 = 0.855*C0 + 0.546*(1.0-C0)
    C3 = 0.139*C0 + 0.043*(1.0-C0)
    Ap = A001*C1*pow(p_percent, -(C2+C3*log10(p_percent)))

    return Ap


def diffraction_loss_over_avg_terrain(d_km: float, f_ghz: float, d1_km: float, d2_km: float,
                                      h_m: float) -> float:
    """
    ITU-R P.530-18, Annex 1, Section 2.2.1.

    Approximation of the diffraction loss (dB) over average terrain (strictly valid for losses
    greater than about 15 dB).

    Args:
        d_km (float): Path length (km), with 0 < d_km.
        f_ghz (float): Frequency (GHz).
        d1_km (float): Distance from the first terminal to the path obstruction (km).
        d2_km (float): Distance from the second terminal to the path obstruction (km).
        h_m (float): Height difference (m) between most significant path blockage and the path
            trajectory (h_m is negative if the top of the obstruction of interest is above the
            virtual line-of-sight).

    Returns:
        Ad (float): Approximation of the diffraction loss (dB) over average terrain (strictly valid
            for losses greater than about 15 dB).
    """
    F1 = 17.3*sqrt((d1_km*d2_km)/(f_ghz*d_km))
    Ad = -20.0*h_m/F1 + 10
    return Ad


def single_frequency_fading_distribution(a_db: float, d_km: float, f_ghz: float, he_masl: float,
                                         hr_masl: float, ht_masl: float, lat: float, lon: float,
                                         time_period: TimePeriod) -> float:
    """
    ITU-R P.530-18, Annex 1, Sections 2.3.1 and 2.3.4.

    Calculates the percentage of time that fade depth a_db is exceeded in the specified time
    period (%).
    
    This implements a method for predicting the single-frequency (or narrow-band) fading
    distribution at large fade depths in the average worst month or average year in any part of the
    world. This method does not make use of the path profile and can be used for initial planning,
    licensing, or design purposes.

    Multipath fading and enhancement only need to be calculated for path lengths longer than 5 km,
    and can be set to zero for shorter paths.

    Args:
        a_db (float): Fade depth (dB), with 0 <= a_db.
        d_km (float): Path length (km), with 0 < d_km.
        f_ghz (float): Frequency (GHz), with 15/d_km <= f_ghz <= 45.
        he_masl (float): Emitter antenna height (meters above sea level).
        hr_masl (float): Receiver antenna height (meters above sea level).
        ht_masl (float): Mean terrain elevation along the path, excluding trees (meters above sea
            level).
        lat (float): Latitude of the path location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the path location(degrees), with -180 <= lon <= 180.
        time_period (TimePeriod): Time period (AVG_WORST_MONTH or AVG_YEAR).

    Returns:
        p (float): The percentage of time that fade depth a_db is exceeded in the specified time
            period (%).
    """
    f = f_ghz
    d = d_km
    he = he_masl
    hr = hr_masl
    ht = ht_masl
    epsp = abs(hr-he)/d
    hc = ((hr+he)/2.0) - (d*d/102.0) - ht
    K = _geoclimatic_factor_k(lat, lon)
    dN75 = _dn75(lat, lon)
    vsrlimit = dN75*pow(d, 1.5)*sqrt(f)/24730.0
    vsr = pow(dN75/50.0, 1.8)*exp(-hc/(2.5*sqrt(d)))
    vsr = min(vsr, vsrlimit)
    hL = min(he, hr)
    xponent = -0.376*tanh((hc-147.0)/125.0) - 0.334*pow(epsp, 0.39) - 0.00027*hL + 17.85*vsr - \
              a_db/10.0
    pw = K*pow(d, 3.51)*pow((f*f)+13.0, 0.447)*pow(10.0, xponent)
    if time_period == TimePeriod.AVG_WORST_MONTH:
        return pw
    else: # AVG_YEAR
        delta_G = _delta_g(d_km, he_masl, hr_masl, lat)
        p = pow(10.0, -delta_G/10.0)*pw
        return p


def _geoclimatic_factor_k(lat: float, lon: float) -> float:
    """
    ITU-R P.530-18, Annex 1, Sections 1.1 and 2.3.1.

    Gets the geoclimatic factor K.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        K (float): The geoclimatic factor K.
    """
    # lat from +90 to -90, lon from -180 to +180 in LogK.csv
    lat_interval = 0.25
    lon_interval = 0.25
    num_rows = 721 # number of points from [-90, 90] latitude deg range,
                   # at 0.25 deg intervals: (180/0.25)+1
    row_size = 1441 # number of points from [-180, 180] longitude deg range,
                    # at 0.25 deg intervals: (360/0.25)+1
    r = (90.0 - lat) / lat_interval
    c = (180.0 + lon) / lon_interval
    arr = _thread_safe_get_logk_array()
    log10_K = p1144_13.square_grid_bilinear_interpolation(arr, num_rows, row_size, r, c)
    return pow(10, log10_K)


def _dn75(lat: float, lon: float) -> float:
    """
    ITU-R P.530-18, Annex 1, Sections 1.1 and 2.3.1.

    Gets parameter dN75, an empirical prediction of 0.1% of the average worst month refractivity
    increase with height over the lowest 75 m of the atmosphere from surface dewpoint data
    (N-units).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        dN75 (float): dN75, an empirical prediction of 0.1% of the average worst month refractivity
            increase with height over the lowest 75 m of the atmosphere from surface dewpoint data
            (N-units).
    """
    # lat from +90 to -90, lon from -180 to +180 in dN75.csv
    lat_interval = 0.25
    lon_interval = 0.25
    num_rows = 721 # number of points from [-90, 90] latitude deg range,
                   # at 0.25 deg intervals: (180/0.25)+1
    row_size = 1441 # number of points from [-180, 180] longitude deg range,
                    # at 0.25 deg intervals: (360/0.25)+1
    r = (90.0 - lat) / lat_interval
    c = (180.0 + lon) / lon_interval
    arr = _thread_safe_get_dn75_array()
    return p1144_13.square_grid_bilinear_interpolation(arr, num_rows, row_size, r, c)


def fading_distribution(a_db: float, d_km: float, f_ghz: float, he_masl: float, hr_masl: float,
                        ht_masl: float, lat: float, lon: float, time_period: TimePeriod) -> float:
    """
    ITU-R P.530-18, Annex 1, Sections 2.3.2 and 2.3.4.

    Calculates the percentage of time that fade depth a_db is exceeded in the specified time
    period (%).

    This implementation is suitable for all fade depths and employs the method for large fade depths
    and an interpolation procedure for small fade depths. It combines the deep fading distribution
    given in section 2.3.1 and an empirical interpolation procedure for shallow fading down to 0 dB.

    Multipath fading and enhancement only need to be calculated for path lengths longer than 5 km,
    and can be set to zero for shorter paths.

    Args:
        a_db (float): Fade depth (dB), with 0 <= a_db.
        d_km (float): Path length (km), with 0 < d_km.
        f_ghz (float): Frequency (GHz), with 15/d_km <= f_ghz <= 45.
        he_masl (float): Emitter antenna height (meters above sea level).
        hr_masl (float): Receiver antenna height (meters above sea level).
        ht_masl (float): Mean terrain elevation along the path, excluding trees (meters above sea
            level).
        lat (float): Latitude of the path location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the path location(degrees), with -180 <= lon <= 180.
        time_period (TimePeriod): Time period (AVG_WORST_MONTH or AVG_YEAR).
        
    Returns:
        p (float): The percentage of time that fade depth a_db is exceeded in the specified time
            period (%).
    """
    p0 = single_frequency_fading_distribution(0.0, d_km, f_ghz, he_masl, hr_masl, ht_masl, lat, lon,
             TimePeriod.AVG_WORST_MONTH) # always use worst month here, as of step 1 of 2.3.4
    return _fade_depth_distribution(a_db, p0, d_km, he_masl, hr_masl, lat, time_period)


def _fade_depth_distribution(a_db: float, p0: float, d_km: float, he_masl: float, hr_masl: float,
                             lat: float, time_period: TimePeriod) -> float:
    """
    ITU-R P.530-18, Annex 1, Sections 2.3.2 and 2.3.4.

    See fading_distribution() for details.
    """
    At = 25.0 + 1.2*log10(p0)
    if a_db >= At and time_period == TimePeriod.AVG_WORST_MONTH:
        p = p0*pow(10.0, -a_db/10.0)
    else:
        pt = p0*pow(10.0, -At/10.0)
        if time_period == TimePeriod.AVG_YEAR:
            delta_G = _delta_g(d_km, he_masl, hr_masl, lat)
            pt = pow(10.0, -delta_G/10.0)*pt
        qpa = -20.0*log10(-ln((100.0-pt)/100.0))/At
        qt = (qpa-2.0)/((1.0+0.3*pow(10.0, -At/20.0))*pow(10.0, -0.016*At)) - \
             4.3*(pow(10.0, -At/20.0)+At/800.0)
        qa = 2.0 + (1.0+0.3*pow(10.0, -a_db/20.0))*pow(10.0, -0.016*a_db)* \
             (qt+4.3*(pow(10.0, -a_db/20.0)+a_db/800.0))
        p = 100.0*(1.0-exp(-pow(10.0, -qa*a_db/20.0)))
    return p


def enhancement_distribution(e_db: float, d_km: float, f_ghz: float, he_masl: float, hr_masl: float,
                             ht_masl: float, lat: float, lon: float, time_period: TimePeriod
                             ) -> float:
    """
    ITU-R P.530-18, Annex 1, Sections 2.3.3 and 2.3.4.

    Calculates the percentage of time that enhancement e_db is not exceeded in the specified time
    period (%).

    Multipath fading and enhancement only need to be calculated for path lengths longer than 5 km,
    and can be set to zero for shorter paths.

    Args:
        e_db (float): Enhancement (dB), with 0 <= e_db.
        d_km (float): Path length (km), with 0 < d_km.
        f_ghz (float): Frequency (GHz), with 15/d_km <= f_ghz <= 45.
        he_masl (float): Emitter antenna height (meters above sea level).
        hr_masl (float): Receiver antenna height (meters above sea level).
        ht_masl (float): Mean terrain elevation along the path, excluding trees (meters above sea
            level).
        lat (float): Latitude of the path location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the path location(degrees), with -180 <= lon <= 180.
        time_period (TimePeriod): Time period (AVG_WORST_MONTH or AVG_YEAR).

    Returns:
        p (float): The percentage of time that enhancement e_db is not exceeded in the specified
            time period (%).
    """
    p0 = single_frequency_fading_distribution(0.0, d_km, f_ghz, he_masl, hr_masl, ht_masl, lat,
            lon, TimePeriod.AVG_WORST_MONTH) # always use worst month here, as of step 1 of 2.3.4
    return _enhancement_distribution(e_db, p0, d_km, he_masl, hr_masl, lat, time_period)


def _enhancement_distribution(e_db: float, p0: float, d_km: float, he_masl: float, hr_masl: float,
                              lat: float, time_period: TimePeriod) -> float:
    """
    ITU-R P.530-18, Annex 1, Sections 2.3.3 and 2.3.4.

    See enhancement_distribution() for details.
    """
    if time_period == TimePeriod.AVG_WORST_MONTH:
        A001 = 10.0*log10(p0/0.01) # <-- This is what the matlab code from
                                   #     https://github.com/eeveetza/p530 does.
        # Alternately...
        #A001 = inverse_distribution(_fade_depth_distribution, 0.01, p0, d_km, he_masl, hr_masl,
        #                            lat, time_period)
    else: # AVG_YEAR
        delta_G = _delta_g(d_km, he_masl, hr_masl, lat)
        pw = 0.01/(pow(10.0, -delta_G/10.0))
        A001 = 10.0*log10(p0/pw)
        #A001 = inverse_distribution(_fade_depth_distribution, pw, p0, d_km, he_masl, hr_masl,
        #                            lat, time_period)

    if e_db > 10.0:
        p = 100.0-pow(10.0, (-1.7+0.2*A001-e_db)/3.5)
    else:
        Ep = 10.0
        pwp = 100.0-pow(10.0, (-1.7+0.2*A001-Ep)/3.5)
        qep = -(20.0/Ep)*(log10(-ln(1.0-(100.0-pwp)/58.21)))
        qs = 2.05*qep - 20.3
        qe = 8.0 + (1.0+0.3*pow(10.0, -e_db/20.0)) * pow(10.0, -0.7*e_db/20.0) * \
             (qs+12.0*(pow(10.0, -e_db/20.0)+e_db/800.0))
        p = 100.0-58.21*(1.0-exp(-pow(10.0, -qe*e_db/20.0)))
    return p


def inverse_distribution(distrib_func: Callable[..., float], p_percent: float,
                         *distrib_func_args: tuple[Any, ...]) -> float:
    """
    Related to ITU-R P.530-18, Annex 1, Sections 2.3.1, 2.3.2, 2.3.3 and 2.3.4.

    Calculates the fading (dB) exceeded for the specified time percentage, or the enhancement (dB)
    not exceeded for the specified time percentage.
    
    Warning:
        This function is provided for convenience. It is not directly part of the ITU
        recommendation, so please use it with caution

    Args:
        distrib_func (Callable[..., float]): Function, one of single_frequency_fading_distribution,
            fading_distribution or enhancement_distribution.
        p_percent (float): Percentage of time (%).
        distrib_func_args (tuple[Any, ...]): Arguments for distrib_func, with the exception of a_db
            or e_db that must not be specified. 

    Returns:
        float: The fading (dB) exceeded for the specified time percentage, or the enhancement (dB)
            not exceeded for the specified time percentage.

    Examples:
        ```python
        from propakai import p530_18

        attenuation_db = 1
        params = (d_km:=3, f_ghz:=30, he_masl:=112, hr_masl:=101.5, ht_masl:=100, lat:=45, lon:=-75,
                  time_period:=p530_18.TimePeriod.AVG_YEAR) # params must be in the right order
        percent_time_att_is_exceeded = p530_18.fading_distribution(attenuation_db, *params)
        print(percent_time_att_is_exceeded) # Output: 9.45680513994811

        attenuation_db = p530_18.inverse_distribution(p530_18.fading_distribution,
                                                      percent_time_att_is_exceeded, *params)
        print(attenuation_db) # Output: 1.000070571899414
        ```
    """
    if distrib_func.__name__ == 'enhancement_distribution':
        # the time percentage is for the dB value **not** being exceeded
        return _inverse_distribution(distrib_func, p_percent, True, *distrib_func_args)
    else:
        # the time percentage is for the dB value being exceeded
        return _inverse_distribution(distrib_func, p_percent, False, *distrib_func_args)


def _inverse_distribution(distrib_func, p_percent: float, not_exceeded: bool, *distrib_func_args
                          ) -> float:
    """
    See inverse_distribution() for details.
    """
    p = p_percent
    min_dB = 0
    max_dB = 300
    mid_dB = (max_dB + min_dB) / 2.0
    while True:
        temp_p = distrib_func(mid_dB, *distrib_func_args)
        if (temp_p < p and not_exceeded is False) or (temp_p > p and not_exceeded is True):
            max_dB = mid_dB
        else:
            min_dB = mid_dB
        temp_mid_dB = (max_dB + min_dB) / 2.0
        if abs(mid_dB-temp_mid_dB) < 1E-4: # arbitrary value
            break
        mid_dB = temp_mid_dB
    return mid_dB


def _delta_g(d_km: float, he_masl: float, hr_masl: float, lat: float) -> float:
    """
    ITU-R P.530-18, Annex 1, Section 2.3.4 (Step 2).

    Calculates the logarithmic geoclimatic conversion factor (dB).

    Args:
        d_km (float): Path length (km), with 0 < d_km.
        he_masl (float): Emitter antenna height (meters above sea level).
        hr_masl (float): Receiver antenna height (meters above sea level).
        lat (float): Latitude of the path location (degrees), with -90 <= lat <= 90.

    Returns:
        delta_G (float): The logarithmic geoclimatic conversion factor (dB)
    """
    lat = abs(lat)
    if lat > 45:
        sign = -1
    else:
        sign = 1
    lat_rad = radians(lat)
    epsp = (hr_masl-he_masl)/d_km
    delta_G = 10.5 - 5.6*log10(1.1+(sign*pow(abs(cos(2*lat_rad)), 0.7))) - 2.7*log10(d_km) + \
              1.7*log10(1.0+abs(epsp))
    delta_G = max(10.8, delta_G)
    return delta_G


def avg_worst_month_to_shorter_worst_period(pw_percent: float, t_hours: float, path_type: PathType
                                            ) -> float:
    """
    ITU-R P.530-18, Annex 1, Sections 2.3.5.

    Converts the percentage of time pw of exceeding a deep fade A in the average worst month to a
    percentage of time pws of exceeding the same deep fade during a shorter worst period of time T.

    Args:
        pw_percent (float): The percentage of time (%) of exceeding a deep fade A in the average
            worst month.
        t_hours (float): Shorter than a month worst period of time (hours), with 1 <= t_hours < 720.
        path_type (PathType): Type of path.

    Returns:
        psw (float): Percentage of time of exceeding the deep fade A during the worst T hours.
    """
    psw = pw_percent
    if path_type == PathType.RELATIVELY_FLAT:
        psw = pw_percent*(89.34*pow(t_hours, -0.854)+0.676)
    elif path_type == PathType.HILLY:
        psw = pw_percent*(119.0*pow(t_hours, -0.78)+0.295)
    elif path_type == PathType.HILLY_LAND:
        psw = pw_percent*(199.85*pow(t_hours, -0.834)+0.175)
    return psw


def _load_logk() -> array:
    return p1144_13.load_digital_map(join(_du.install_dir(), _p530_18_shared['DATA_DIR'],
                                          'LogK.csv'), delimiter=',')


def _thread_safe_get_logk_array() -> array:
    arr = _p530_18_shared['logk_array']
    if arr is not None:
        return arr
    with _p530_18_shared['logk_lock']:
        arr = _p530_18_shared['logk_array']
        if arr is None:
            try:
                arr = _load_logk()
            except FileNotFoundError:
                _download_rec_data()
                arr = _load_logk()
            _p530_18_shared['logk_array'] = arr
    return arr


def _load_dn75() -> array:
    return p1144_13.load_digital_map(join(_du.install_dir(), _p530_18_shared['DATA_DIR'],
                                          'dN75.csv'), delimiter=',')


def _thread_safe_get_dn75_array() -> array:
    arr = _p530_18_shared['dn75_array']
    if arr is not None:
        return arr
    with _p530_18_shared['dn75_lock']:
        arr = _p530_18_shared['dn75_array']
        if arr is None:
            try:
                arr = _load_dn75()
            except FileNotFoundError:
                _download_rec_data()
                arr = _load_dn75()
            _p530_18_shared['dn75_array'] = arr
    return arr


def _download_rec_data() -> None:
    data_dir = _p530_18_shared['DATA_DIR']
    full_path_data_dir = join(_du.install_dir(), data_dir)
    filenames = ['dN75.csv', 'LogK.csv']
    lock = FileLock(_du.get_lockfile_pathname(data_dir))
    with lock:
        if _du.files_all_exist(full_path_data_dir, filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.530-18-202109-S!!ZIP-E.zip'
            zip_pathname = _du.download(url, full_path_data_dir)
            _du.extract_files(zip_pathname, filenames, create_dirs=True, delete_zip_archive=True)
            _du.print_notice()
        else:
            _du.print_already_installed(full_path_data_dir, filenames)


_p530_18_shared = {
    'DATA_DIR': 'p530_18',
    'logk_lock': Lock(),
    'logk_array': None,
    'dn75_lock': Lock(),
    'dn75_array': None
}
