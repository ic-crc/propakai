# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.840-9.

P.840 : Attenuation due to clouds and fog.

https://www.itu.int/rec/R-REC-P.840/en
"""

from os.path import join
from math import log10, exp, sin, radians
from threading import Lock
from array import array
from filelock import FileLock
from propakai import _download_utils as _du
from propakai import p1144_13
from propakai import p1057_7


__all__ = ['cloud_or_fog_attenuation',
           'cloud_liquid_water_attenuation_coefficient',
           'slant_path_instantaneous_cloud_attenuation',
           'slant_path_statistical_cloud_attenuation',
           'log_normal_approx_to_stat_cloud_attenuation',
           'integrated_cloud_liquid_water_content',
           'mean_integrated_cloud_liquid_water_content',
           'std_dev_integrated_cloud_liquid_water_content']


def cloud_or_fog_attenuation(f_ghz, t_k, rhol_gm3) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 1.

    Gets the specific attenuation within a cloud or fog (dB/km).
    
    "At frequencies of the order of 100 GHz and above, attenuation due to fog may be significant".

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 200.
        t_k (float): Liquid water temperature (K).
        rhol_gm3 (float): Liquid water density in the cloud or fog (g/m3). "Typically about 0.05
            g/m3 for medium fog (visibility of the order of 300 m) and 0.5 g/m3 for thick fog
            (visibility of the order of 50 m)."

    Returns:
        gamma_c (float): Specific attenuation (dB/km) within cloud or fog.
    """
    gamma_c = cloud_liquid_water_attenuation_coefficient(f_ghz, t_k)*rhol_gm3
    return gamma_c


def cloud_liquid_water_attenuation_coefficient(f_ghz, t_k) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 2.

    Gets the cloud liquid water specific attenuation coefficient (dB/km)/(g/m3).

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 200.
        t_k (float): Liquid water temperature (K).
    
    Returns:
        Kl (float): The cloud liquid water specific attenuation coefficient (dB/km)/(g/m3).
    """
    a = (300/t_k)-1
    fp = 20.20 - 146*a + 316*a*a
    fs = 39.8*fp
    eps0 = 77.66 + 103.3*a
    eps1 = 0.0671*eps0
    eps2 = 3.52
    xp = 1 + (f_ghz*f_ghz)/(fp*fp)
    xs = 1 + (f_ghz*f_ghz)/(fs*fs)
    eps_pp = f_ghz*(eps0-eps1)/(fp*xp) + f_ghz*(eps1-eps2)/(fs*xs)
    eps_p = (eps0-eps1)/xp + (eps1-eps2)/xs + eps2
    n = (2+eps_p)/eps_pp
    Kl = 0.819*f_ghz/(eps_pp*(1+(n*n)))
    return Kl


def slant_path_instantaneous_cloud_attenuation(f_ghz: float, theta_deg: float, l_kgm2: float
                                               ) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 3.1.

    Gets the predicted slant path instantaneous cloud attenuation (dB).

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 200.
        theta_deg (float): Elevation angle (degrees).
        l_kgm2 (float): Integrated cloud liquid water content, in kg/m2 or mm, from the surface
            of the Earth at the desired location.

    Returns:
        Ac (float): The predicted slant path instantaneous cloud attenuation (dB).
    """
    Ac = _KL(f_ghz)*l_kgm2/sin(radians(theta_deg))
    return Ac


def _KL(f_ghz) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 3.1.

    Gets the cloud liquid mass absorption coefficient in dB/(kg/m2) or dB/mm.

    Args:
        f_ghz (float): Frequency (GHz).
    
    Returns:
        KL (float): The cloud liquid mass absorption coefficient in dB/(kg/m2) or dB/mm.
    """
    A1 = 0.1522
    A2 = 11.51
    A3 = -10.4912
    f1 = -23.9589
    f2 = 219.2096
    s1 = 3.2991E3
    s2 = 2.7595E6
    e1 = exp(-((f_ghz-f1)**2)/s1)
    e2 = exp(-((f_ghz-f2)**2)/s2)
    KL = cloud_liquid_water_attenuation_coefficient(f_ghz, 273.75)* ((A1*e1) + (A2*e2) + A3)
    return KL


def slant_path_statistical_cloud_attenuation(f_ghz: float, theta_deg: float, p_percent: float,
                                             lat: float, lon: float, month: int|None=None
                                             ) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 3.2.

    Gets the predicted slant path statistical cloud attenuation (dB).

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 200.
        theta_deg (float): Elevation angle (degrees).
        p_percent (float): Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent
            <= 100 for annual statistics and with 0.1 <= p_percent <= 100 for monthly statistics.
        lat (float): Latitude of the desired location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (degrees), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.

    Returns:
        Ac (float): The predicted slant path statistical cloud attenuation (dB).
    """
    L = integrated_cloud_liquid_water_content(p_percent, lat, lon, month)
    Ac = slant_path_instantaneous_cloud_attenuation(f_ghz, theta_deg, L)
    return Ac


def log_normal_approx_to_stat_cloud_attenuation(f_ghz: float, theta_deg: float, p_percent: float,
                                                lat: float, lon: float) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 3.3.

    Gets the log-normal approximation to the predicted slant path statistical cloud
    attenuation (dB). Uses annual statistics.
    
    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 200.
        theta_deg (float): Elevation angle (degrees).
        p_percent (float): Exceedance probability (CCDF) of interest, in %, with 0.01 <= p <= 100.
        lat (float): Latitude of the desired location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (degrees), with -180 <= lon <= 180.

    Returns:
        Ac (float): The log-normal approximation to the predicted slant path statistical cloud
            attenuation (dB).
    """
    PL = _get_digital_map_value(None, 'PL', lat, lon)
    if PL <= 0.02:
        return 0
    if p_percent >= PL:
        return 0
    mL = _get_digital_map_value(None, 'mL', lat, lon)
    sL = _get_digital_map_value(None, 'sL', lat, lon)
    KL = _KL(f_ghz)
    Ac = KL*exp(mL+(sL*p1057_7.q_inv(p_percent/PL)))/sin(radians(theta_deg))
    return Ac


def integrated_cloud_liquid_water_content(p_percent: float, lat: float, lon: float,
                                          month: int|None=None) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 4.

    Gets the integrated cloud liquid water content for the provided exceedance probability, in
    kg/m2, or, equivalently, mm.

    Args:
        p_percent (float): Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent
            <= 100 for annual statistics and with 0.1 <= p_percent <= 100 for monthly statistics.
        lat (float): Latitude of the desired location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (degrees), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.

    Returns:
        L (float): The integrated cloud liquid water content in kg/m2, or, equivalently, mm.
    """
    if month is None:
        nominal_percentages = _p840_9_shared['ANNUAL_P']
        filenames = _p840_9_shared['ANNUAL_FILENAMES']
    else:
        nominal_percentages = _p840_9_shared['MONTHLY_P']
        filenames = _p840_9_shared['MONTHLY_FILENAMES']
    for i in range(0, len(nominal_percentages)-1):
        if p_percent >= nominal_percentages[i] and p_percent <= nominal_percentages[i+1]:
            L0 = _get_digital_map_value(month, filenames[i], lat, lon)
            L1 = _get_digital_map_value(month, filenames[i+1], lat, lon)
            p0 = nominal_percentages[i] # p below
            p1 = nominal_percentages[i+1] # p above
            L = (L0*log10(p1/p_percent) + L1*log10(p_percent/p0)) / log10(p1/p0)
            return L
    raise ValueError('p_percent is out of range.')


def mean_integrated_cloud_liquid_water_content(lat: float, lon: float, month:int|None=None
                                               ) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 4.

    Gets the mean of the integrated cloud liquid water content.

    Args:
        lat (float): Latitude of the desired location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (degrees), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.

    Returns:
        L_mean (float): The mean of the integrated cloud liquid water content.
    """
    return _get_digital_map_value(month, 'L_mean', lat, lon)


def std_dev_integrated_cloud_liquid_water_content(lat: float, lon: float, month:int|None=None
                                                  ) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 4.

    Gets the standard deviation of the integrated cloud liquid water content.

    Args:
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.

    Returns:
        L_std (float): The standard deviation of the integrated cloud liquid water content.
    """
    return _get_digital_map_value(month, 'L_std', lat, lon)


def _get_digital_map_value(month: int|None, filename: str, lat: float, lon: float) -> float:
    # lat from -90 to +90, lon from -180 to +180
    lat_interval = 0.25
    lon_interval = 0.25
    num_rows = 721 # number of points from [-90, 90] latitude deg range,
                   # at 0.25 deg intervals: (180/0.25)+1
    row_size = 1441 # number of points from [-180, 180] longitude deg range,
                    # at 0.25 deg intervals: (360/0.25)+1
    r = (90.0 + lat) / lat_interval
    c = (180.0 + lon) / lon_interval
    grid = _thread_safe_get_digital_map_array(month, filename)
    return p1144_13.square_grid_bilinear_interpolation(grid, num_rows, row_size, r, c)


def _thread_safe_get_digital_map_array(month: int|None, filename: str) -> array:
    # NOTE: It is not safe to concurrently access a Python dictionary from one thread while it is
    # being modified by another thread, even if you are only reading a specific key/value that is
    # not being directly modified. This is why we always use the lock here.
    with _p840_9_shared['digital_maps_lock']:
        dmaps = _p840_9_shared['digital_maps']
        if (month, filename) not in dmaps:
            if month is None:
                pathname = join(_du.install_dir(), _p840_9_shared['DATA_DIR'], 'annual',
                                f'{filename}.TXT')
            else:
                pathname = join(_du.install_dir(), _p840_9_shared['DATA_DIR'], 'monthly',
                                f'{month:02d}', f'{filename}.TXT')
            try:
                arr = p1144_13.load_digital_map(pathname)
            except FileNotFoundError:
                if month is None:
                    _download_annual_rec_data()
                else:
                    _download_monthly_rec_data(month)
                arr = p1144_13.load_digital_map(pathname)
            dmaps[(month, filename)] = arr
        map_array = dmaps[(month, filename)]
    return map_array


def _download_annual_rec_data() -> None:
    data_dir = _p840_9_shared['DATA_DIR']
    annual_data_dir = join(data_dir, 'annual')
    full_path_annual_data_dir = join(_du.install_dir(), annual_data_dir)
    filenames = [fn+'.TXT' for fn in _p840_9_shared['ANNUAL_FILENAMES']]
    filenames += ['L_mean.TXT', 'L_std.TXT']
    lock = FileLock(_du.get_lockfile_pathname(f'{data_dir}_annual'))
    with lock:
        if _du.files_all_exist(full_path_annual_data_dir, filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/' \
                'R-REC-P.840Part01-0-202308-I!!ZIP-E.zip'
            zip_pathname = _du.download(url, full_path_annual_data_dir)
            _du.extract_all(zip_pathname, delete_zip_archive=True)
            _du.print_notice()
        else:
            _du.print_already_installed(full_path_annual_data_dir, filenames)

    filenames = ['mL.TXT', 'PL.TXT', 'sL.TXT']
    with lock:
        if _du.files_all_exist(full_path_annual_data_dir, filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/' \
                'R-REC-P.840Part14-0-202308-I!!ZIP-E.zip'
            zip_pathname = _du.download(url, full_path_annual_data_dir)
            _du.extract_all(zip_pathname, delete_zip_archive=True)
            _du.print_notice()
        else:
            _du.print_already_installed(full_path_annual_data_dir, filenames)


def _download_monthly_rec_data(month: int) -> None:
    """
    Downloads monthly data files.

    Args:
        month (int): 1 <= month <= 12.
    """
    month_num_str = f'{month:02d}'
    part_num_str = f'{month+1:02d}'
    data_dir = _p840_9_shared['DATA_DIR']
    monthly_data_dir = join(data_dir, 'monthly', month_num_str)
    full_path_monthly_data_dir = join(_du.install_dir(), monthly_data_dir)
    filenames = [fn+'.TXT' for fn in _p840_9_shared['MONTHLY_FILENAMES']]
    filenames += ['L_mean.TXT', 'L_std.TXT']
    lock = FileLock(_du.get_lockfile_pathname(f'{data_dir}_month{month}'))
    with lock:
        if _du.files_all_exist(full_path_monthly_data_dir, filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/' \
                f'R-REC-P.840Part{part_num_str}-0-202308-I!!ZIP-E.zip'
            zip_pathname = _du.download(url, full_path_monthly_data_dir)
            _du.extract_all(zip_pathname, delete_zip_archive=True)
            _du.print_notice()
        else:
            _du.print_already_installed(full_path_monthly_data_dir, filenames)


_p840_9_shared = {
    'DATA_DIR': 'p840_9',
    'ANNUAL_P': (0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70,
                 80, 90, 95, 99, 100),
    'ANNUAL_FILENAMES': ('L_001', 'L_002', 'L_003', 'L_005', 'L_01', 'L_02', 'L_03', 'L_05', 'L_1',
                         'L_2', 'L_3', 'L_5', 'L_10', 'L_20', 'L_30', 'L_50', 'L_60', 'L_70',
                         'L_80', 'L_90', 'L_95', 'L_99', 'L_100'),
    'MONTHLY_P': (0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99, 100),
    'MONTHLY_FILENAMES': ('L_01', 'L_02', 'L_03', 'L_05', 'L_1', 'L_2', 'L_3', 'L_5', 'L_10',
                          'L_20', 'L_30', 'L_50', 'L_60', 'L_70', 'L_80', 'L_90', 'L_95', 'L_99',
                          'L_100'),
    'digital_maps_lock': Lock(),
    'digital_maps': {}
}
