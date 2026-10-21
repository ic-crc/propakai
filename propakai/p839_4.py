# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.839-4.

P.839 : Rain height model for prediction methods.

https://www.itu.int/rec/R-REC-P.839/en
"""

from os.path import join
from threading import Lock
from array import array
from filelock import FileLock
from propakai import _download_utils as _du
from propakai import p1144_13


__all__ = ['mean_annual_0c_isotherm_height',
           'mean_annual_rain_height']


def mean_annual_0c_isotherm_height(lat: float, lon: float) -> float:
    """
    ITU-R P.839-4.

    Gets the mean annual 0°C isotherm height (km above mean sea level).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        h0 (float): The mean annual 0°C isotherm height (km above mean sea level).
    """
    # lat from +90 to -90, lon from 0 to 360 in h0.txt
    lat_interval = 1.5
    lon_interval = 1.5
    num_rows = 121 # number of points from [-90, 90] latitude deg range,
                   # at 1.5 deg intervals: (180/1.5)+1
    row_size = 241 # number of points from [0, 360] longitude deg range,
                   # at 1.5 deg intervals: (360/1.5)+1

    if lon < 0:
        lon += 360
    r = (90.0 - lat) / lat_interval
    c = lon / lon_interval
    arr = _thread_safe_get_h0_array()
    return p1144_13.square_grid_bilinear_interpolation(arr, num_rows, row_size, r, c)


def mean_annual_rain_height(lat: float, lon: float) -> float:
    """
    ITU-R P.839-4.

    Gets the mean annual rain height (km above mean sea level).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        hR (float): The mean annual rain height (km above mean sea level).
    """
    return mean_annual_0c_isotherm_height(lat, lon) + 0.36


def _load_h0() -> array:
    return p1144_13.load_digital_map(join(_du.install_dir(), _p839_4_shared['DATA_DIR'], 'h0.txt'))


def _thread_safe_get_h0_array() -> array:
    arr = _p839_4_shared['h0_array']
    if arr is not None:
        return arr
    with _p839_4_shared['h0_lock']:
        arr = _p839_4_shared['h0_array']
        if arr is None:
            try:
                arr = _load_h0()
            except FileNotFoundError:
                _download_rec_data()
                arr = _load_h0()
            _p839_4_shared['h0_array'] = arr
    return arr


def _download_rec_data() -> None:
    data_dir = _p839_4_shared['DATA_DIR']
    full_path_data_dir = join(_du.install_dir(), data_dir)
    filenames = ['h0.txt']
    lock = FileLock(_du.get_lockfile_pathname(data_dir))
    with lock:
        if _du.files_all_exist(full_path_data_dir, filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.839-4-201309-I!!ZIP-E.zip'
            zip_pathname = _du.download(url, full_path_data_dir)
            _du.extract_files(zip_pathname, filenames, create_dirs=True, delete_zip_archive=True)
            _du.print_notice()
        else:
            _du.print_already_installed(full_path_data_dir, filenames)


_p839_4_shared = {
    'DATA_DIR': 'p839_4',
    'h0_lock': Lock(),
    'h0_array': None
}
