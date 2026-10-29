# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.837-8.

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite this software
    package along with the underlying ITU-R standard:

    * **ITU-R Standard:** International Telecommunication Union (2025).
      *Recommendation ITU-R P.837-8: Characteristics of precipitation for propagation modelling*.
      Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.837/en
"""

from os.path import join
from math import exp, fabs, log as ln, erfc, sqrt
from types import SimpleNamespace
from threading import Lock
from array import array
from filelock import FileLock
from propakai import _download_utils as _du
from propakai import p1144_13
from propakai import p1510_1


__all__ = ['annual_rainfall_rate_001',
           'total_monthly_mean_rainfall',
           'annual_rainfall_rate',
           'monthly_rainfall_rate']


def annual_rainfall_rate_001(lat: float, lon: float) -> float:
    """
    ITU-R P.837-8.
    
    Gets the annual rainfall rate exceeded for 0.01% of an average year (mm/hr).
    This function uses bilinear interpolation on the precalculated R001.txt file.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        R001 (float): The annual rainfall rate exceeded for 0.01% of an average year (mm/hr).
    """
    # lat from -90 to +90, lon from -180 to +180 in R001.txt
    lat_interval = 0.125
    lon_interval = 0.125
    num_rows = 1441 # number of points from [-90, 90] latitude deg range,
                    # at 0.125 deg intervals: (180/0.125)+1
    row_size = 2881 # number of points from [-180, 180] longitude deg range,
                    # at 0.125 deg intervals: (360/0.125)+1

    r = (90.0 + lat) / lat_interval
    c = (180.0 + lon) / lon_interval
    arr = _thread_safe_get_r001_array()
    return p1144_13.square_grid_bilinear_interpolation(arr, num_rows, row_size, r, c)


def total_monthly_mean_rainfall(lat: float, lon: float, month: int) -> float:
    """
    ITU-R P.837-8, Annex 1.

    Gets the total monthly mean rainfall (mm).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        MT (float): Total monthly mean rainfall (mm).
    """
    # lat from -90.125 to +90.125, lon from -180.125 to +180.125 in R001.txt
    lat_interval = 0.25
    lon_interval = 0.25
    num_rows =  722 # number of points from [-90.125, 90.125] latitude deg range,
                    # at 0.25 deg intervals: (180.25/0.25)+1
    row_size = 1442 # number of points from [-180.125, 180.125] longitude deg range,
                    # at 0.25 deg intervals: (360.25/0.25)+1

    r = (90.125 + lat) / lat_interval
    c = (180.125 + lon) / lon_interval
    arr = _thread_safe_get_mt_array(month)
    return p1144_13.square_grid_bilinear_interpolation(arr, num_rows, row_size, r, c)


def annual_rainfall_rate(p_percent: float, lat: float, lon: float) -> tuple[float, float]:
    """
    ITU-R P.837-8, Annex 1.
    
    Gets the rainfall rate at the desired annual rainfall rate probability of exceedance (mm/hr),
    along with the annual probability of rain (%).

    Args:
        p_percent (float): Annual rainfall rate probability of exceedance (%).
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        Rp (float): Rainfall rate exceeded for the desired annual probability of exceedance,
            p_percent, at the specified location on the surface of the Earth, and for an integration
            time of 1 minute (mm/hr).
        P0_annual (float): Annual probability of rain (%).
    """
    # step 1
    N_list = (31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

    # steps 2 to 7 incl.
    r_list = []
    P0_list = []
    P0_annual = 0
    for month in range(1, 12+1):
        Tii_K = p1510_1.mean_surface_temperature(lat, lon, month)
        tii = Tii_K-273.15
        MTii = total_monthly_mean_rainfall(lat, lon, month)
        if tii >= 0.0:
            rii = 0.5874*exp(0.0883*tii)
        else:
            rii = 0.5874
        Nii = N_list[month-1]
        P0ii = 100.0*MTii/(24.0*Nii*rii)
        if P0ii > 70.0:
            P0ii = 70.0
            rii = (100.0/70.0)*(MTii/(24.0*Nii))
        r_list.append(rii)
        P0_list.append(P0ii)
        P0_annual += Nii*P0ii
    P0_annual /= 365.25

    # step 8
    p = p_percent
    if p > P0_annual:
        Rp = 0.0
        return Rp, P0_annual

    Rref_a = 0.0
    Rref_b = 10000.0
    while True:
        Rref = (Rref_a + Rref_b) / 2.0
        P = 0.0
        for ii in range(0, 12):
            Pii = P0_list[ii]*_Q((ln(Rref)+0.7938-ln(r_list[ii]))/1.26)
            P += N_list[ii]*Pii
        P /= 365.25

        rel_error = 100.0*fabs((P/p)-1.0)
        if rel_error < 0.001:
            break

        if P > p:
            Rref_a = Rref
        else:
            Rref_b = Rref

    Rp = Rref
    return Rp, P0_annual


def monthly_rainfall_rate(p_percent: float, lat: float, lon: float, month: int
                          ) -> tuple[float, float]:
    """
    ITU-R P.837-8, Annex 1.
    
    Gets the rainfall rate at the desired monthly rainfall rate probability of exceedance (mm/hr),
    along with the monthly probability of rain (%).

    Args:
        p_percent (float): Monthly rainfall rate probability of exceedance (%).
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        Rp_ii (float): Rainfall rate exceeded for the desired monthly probability of exceedance,
            p_percent, at the specified location on the surface of the Earth, and for an
            integration time of 1 minute (mm/hr).
        P0_ii (float): Monthly probability of rain (%).
    """
    if month < 1 or month > 12:
        raise ValueError('month must be between 1 and 12 inclusively.')

    # step 1
    N_list = (31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

    # steps 2 to 7 incl.
    Tii_K = p1510_1.mean_surface_temperature(lat, lon, month)
    tii = Tii_K-273.15
    MTii = total_monthly_mean_rainfall(lat, lon, month)
    if tii >= 0.0:
        rii = 0.5874*exp(0.0883*tii)
    else:
        rii = 0.5874
    Nii = N_list[month-1]
    P0ii = 100.0*MTii/(24.0*Nii*rii)
    if P0ii > 70.0:
        P0ii = 70.0
        rii = (100.0/70.0)*(MTii/(24.0*Nii))

    # step 8
    p = p_percent
    if p > P0ii:
        Rp_ii = 0.0
        return Rp_ii, P0ii
    Rref_a = 0.0
    Rref_b = 10000.0
    while True:
        Rref = (Rref_a + Rref_b) / 2.0
        Pii = P0ii*_Q((ln(Rref)+0.7938-ln(rii))/1.26)
        rel_error = 100.0*fabs((Pii/p)-1.0)
        if rel_error < 0.001:
            break
        if Pii > p:
            Rref_a = Rref
        else:
            Rref_b = Rref
    Rp = Rref

    return Rp, P0ii


def _Q(x):
    return 0.5*erfc(x/sqrt(2))


def _load_r001_digital_map() -> array:
    return p1144_13.load_digital_map(join(_du.install_dir(), _p837_8_shared.DATA_DIR,
                                          'R001.TXT'))


def _thread_safe_get_r001_array() -> array:
    arr = _p837_8_shared.r001_digital_map
    if arr is not None:
        return arr
    with _p837_8_shared.r001_digital_map_lock:
        arr = _p837_8_shared.r001_digital_map
        if arr is None:
            try:
                arr = _load_r001_digital_map()
            except FileNotFoundError:
                _download_rec_data()
                arr = _load_r001_digital_map()
            _p837_8_shared.r001_digital_map = arr
    return arr


def _load_mt_digital_map(month: int) -> array:
    return p1144_13.load_digital_map(join(_du.install_dir(), _p837_8_shared.DATA_DIR,
                                          f'MT_Month{month:02d}.TXT'))


def _thread_safe_get_mt_array(month: int) -> array:
    if month > 0 and month < 13:
        array_index = month-1
    else:
        raise ValueError('month must be between 1 and 12 inclusively.')
    arr = _p837_8_shared.mt_digital_maps[array_index]
    if arr is not None:
        return arr
    with _p837_8_shared.mt_digital_maps_lock:
        arr = _p837_8_shared.mt_digital_maps[array_index]
        if arr is None:
            try:
                arr = _load_mt_digital_map(month)
            except FileNotFoundError:
                _download_rec_data()
                arr = _load_mt_digital_map(month)
            _p837_8_shared.mt_digital_maps[array_index] = arr
    return arr


def _download_rec_data() -> None:
    data_dir = _p837_8_shared.DATA_DIR
    directory = join(_du.install_dir(), data_dir)
    filenames = ['R001.TXT', 'MT_Month01.TXT', 'MT_Month02.TXT', 'MT_Month03.TXT', 'MT_Month04.TXT',
                 'MT_Month05.TXT', 'MT_Month06.TXT', 'MT_Month07.TXT', 'MT_Month08.TXT',
                 'MT_Month09.TXT', 'MT_Month10.TXT', 'MT_Month11.TXT', 'MT_Month12.TXT']
    lock = FileLock(_du.get_lockfile_pathname(data_dir))
    with lock:
        if _du.files_all_exist(directory, filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.837-8-202509-I!!ZIP-E.zip'
            zip_pathname1 = _du.download(url, directory)
            zip_pathname2 = _du.extract_files(zip_pathname1, ['R-REC-P.837-8-Maps.zip'],
                                              create_dirs=True, delete_zip_archive=True)[0]
            zip_pathname3 = _du.extract_files(zip_pathname2, ['P.837_R001_Maps.zip'],
                                              create_dirs=True, delete_zip_archive=False)[0]
            _du.extract_files(zip_pathname3, filenames, create_dirs=True, delete_zip_archive=True)
            zip_pathname4 = _du.extract_files(zip_pathname2, ['P.837_MT_Maps.zip'],
                                              create_dirs=True, delete_zip_archive=True)[0]
            _du.extract_files(zip_pathname4, filenames, create_dirs=True, delete_zip_archive=True)
            _du.print_notice()
        else:
            _du.print_already_installed(directory, filenames)


_p837_8_shared = SimpleNamespace(
    DATA_DIR = "p837_8",
    r001_digital_map_lock = Lock(),
    r001_digital_map = None,
    mt_digital_maps_lock = Lock(),
    mt_digital_maps = [None] * 12,
)
