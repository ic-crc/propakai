# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.837-8.

P.837 : Characteristics of precipitation for propagation modelling.

https://www.itu.int/rec/R-REC-P.837/en
"""

from os.path import join
from threading import Lock
from array import array
from filelock import FileLock
from propakai import _download_utils as _du
from propakai import p1144_13


__all__ = ['annual_rainfall_rate_001']


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


def _load_r001() -> array:
    return p1144_13.load_digital_map(join(_du.install_dir(), _p837_8_shared['DATA_DIR'],
                                          'R001.TXT'))


def _thread_safe_get_r001_array() -> array:
    arr = _p837_8_shared['r001_array']
    if arr is not None:
        return arr
    with _p837_8_shared['r001_lock']:
        arr = _p837_8_shared['r001_array']
        if arr is None:
            try:
                arr = _load_r001()
            except FileNotFoundError:
                _download_rec_data()
                arr = _load_r001()
            _p837_8_shared['r001_array'] = arr
    return arr


def _download_rec_data() -> None:
    data_dir = _p837_8_shared['DATA_DIR']
    directory = join(_du.install_dir(), data_dir)
    filenames = ['R001.TXT']
    lock = FileLock(_du.get_lockfile_pathname(data_dir))
    with lock:
        if _du.files_all_exist(directory, filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.837-8-202509-I!!ZIP-E.zip'
            zip_pathname1 = _du.download(url, directory)
            zip_pathname2 = _du.extract_files(zip_pathname1, ['R-REC-P.837-8-Maps.zip'],
                                              create_dirs=True, delete_zip_archive=True)[0]
            zip_pathname3 = _du.extract_files(zip_pathname2, ['P.837_R001_Maps.zip'],
                                              create_dirs=True, delete_zip_archive=True)[0]
            _du.extract_files(zip_pathname3, filenames, create_dirs=True, delete_zip_archive=True)
            _du.print_notice()
        else:
            _du.print_already_installed(directory, filenames)


_p837_8_shared = {
    'DATA_DIR': 'p837_8',
    'r001_lock': Lock(),
    'r001_array': None
}
