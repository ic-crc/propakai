# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.2148-0.

P.2148 : Digital maps related to surface wind speed statistics.

https://www.itu.int/rec/R-REC-P.2148/en
"""

from os.path import join
from math import log10
from threading import Lock
from array import array
from filelock import FileLock
from propakai import _download_utils as _du
from propakai import p1144_13


__all__ = ['wind_speed']


def wind_speed(p_percent: float, lat: float, lon: float) -> float:
    """
    ITU-R P.2148-0, Annex 1.

    Gets the annual value of wind speed at a height of 10 m above the surface of the Earth,
    exceeded for p_percent of an average year, in m/s.

    Args:
        p_percent (float): Exceedance probability for an average year, in %, with 0.01 <= p_percent
            <= 99.
        lat (float): Latitude of the desired location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (degrees), with -180 <= lon <= 180.

    Returns:
        W (float): The annual value of wind speed at a height of 10 m above the surface of the
            Earth, exceeded for p_percent of an average year (m/s).
    """
    nominal_percentages = _p2148_0_shared['ANNUAL_P']
    filenames = _p2148_0_shared['ANNUAL_FILENAMES']
    for i in range(0, len(nominal_percentages)-1):
        if p_percent >= nominal_percentages[i] and p_percent <= nominal_percentages[i+1]:
            W0 = _get_digital_map_value(filenames[i], lat, lon)
            W1 = _get_digital_map_value(filenames[i+1], lat, lon)
            p0 = nominal_percentages[i] # p below
            p1 = nominal_percentages[i+1] # p above
            W = (W0*log10(p1/p_percent) + W1*log10(p_percent/p0)) / log10(p1/p0)
            return W
    raise ValueError('p_percent is out of range.')


def _get_digital_map_value(filename: str, lat: float, lon: float) -> float:
    # lat from +90 to -90, lon from 0 to 360
    lat_interval = 0.25
    lon_interval = 0.25
    num_rows = 721  # from the recommendation's TABLE 1
    row_size = 1440 # from the recommendation's TABLE 1
    if lon < 0:
        lon += 360
    r = (90.0 - lat) / lat_interval
    c = lon / lon_interval
    grid = _thread_safe_get_digital_map_array(filename)
    return p1144_13.square_grid_bilinear_interpolation(grid, num_rows, row_size, r, c)


def _thread_safe_get_digital_map_array(filename: str) -> array:
    # NOTE: It is not safe to concurrently access a Python dictionary from one thread while it is
    # being modified by another thread, even if you are only reading a specific key/value that is
    # not being directly modified. This is why we always use the lock here.
    with _p2148_0_shared['digital_maps_lock']:
        dmaps = _p2148_0_shared['digital_maps']
        if filename not in dmaps:
            pathname = join(_du.install_dir(), _p2148_0_shared['DATA_DIR'], f'{filename}.txt')
            try:
                arr = p1144_13.load_digital_map(pathname)
            except FileNotFoundError:
                _download_rec_data()
                arr = p1144_13.load_digital_map(pathname)
            dmaps[filename] = arr
        map_array = dmaps[filename]
    return map_array


def _download_rec_data() -> None:
    data_dir = _p2148_0_shared['DATA_DIR']
    full_path_data_dir = join(_du.install_dir(), data_dir)
    filenames = [fn+'.txt' for fn in _p2148_0_shared['ANNUAL_FILENAMES']]
    filenames += ['Attribution and disclaimer.docx']
    lock = FileLock(_du.get_lockfile_pathname(data_dir))
    with lock:
        if _du.files_all_exist(full_path_data_dir, filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.2148-0-202208-I!!ZIP-E.zip'
            zip_pathname = _du.download(url, full_path_data_dir)
            _du.extract_files(zip_pathname, filenames, create_dirs=False, delete_zip_archive=True)
            _du.print_notice()
        else:
            _du.print_already_installed(full_path_data_dir, filenames)


_p2148_0_shared = {
    'DATA_DIR': 'p2148_0',
    'ANNUAL_P': [0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70,
                 80, 90, 95, 99],
    'ANNUAL_FILENAMES': ['W_001', 'W_002', 'W_003', 'W_005', 'W_01', 'W_02', 'W_03', 'W_05', 'W_1',
                         'W_2', 'W_3', 'W_5', 'W_10', 'W_20', 'W_30', 'W_50', 'W_60', 'W_70',
                         'W_80', 'W_90', 'W_95', 'W_99'],
    'digital_maps_lock': Lock(),
    'digital_maps': {}
}
