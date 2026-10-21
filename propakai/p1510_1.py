# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.1510-1.

P.1510 : Mean surface temperature.

https://www.itu.int/rec/R-REC-P.1510/en
"""

from os.path import join
from threading import Lock
from array import array
from filelock import FileLock
from propakai import _download_utils as _du
from propakai import p1144_13


__all__ = ['mean_surface_temperature']


def mean_surface_temperature(lat: float, lon: float, month: int|None=None) -> float:
    """
    ITU-R P.1510-1, Annex 1.

    Gets the annual or monthly mean surface temperature (K).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the monthly mean surface temperature for
            (1=Jan, ..., 12=Dec). Use None for annual mean surface temperature. Default value is
            None.
    
    Returns:
        float: Annual or monthly mean surface temperature (K).
    """
    # lat from -90 to +90, lon from -180 to +180
    lat_interval = 0.75
    lon_interval = 0.75
    num_rows = 241 # number of points from [-90, 90] latitude deg range,
                   # at 0.75 deg intervals: (180/0.75)+1
    row_size = 481 # number of points from [-180, 180] longitude deg range,
                   # at 0.75 deg intervals: (360/0.75)+1
    r = (90.0 + lat) / lat_interval
    c = (180.0 + lon) / lon_interval
    arr = _thread_safe_get_temperature_array(month)
    return p1144_13.square_grid_bilinear_interpolation(arr, num_rows, row_size, r, c)


def _thread_safe_get_temperature_array(month: int|None=None) -> array:
    if month is None:
        array_index = 0
    elif month > 0 and month < 13:
        array_index = month
    else:
        raise ValueError('month must be None or between 1 and 12 inclusively.')
    arr = _p1510_1_shared['digital_maps'][array_index]
    if arr is not None:
        return arr
    with _p1510_1_shared['digital_maps_lock']:
        arr = _p1510_1_shared['digital_maps'][array_index]
        if arr is None:
            try:
                arr = _load_temperature(month)
            except FileNotFoundError:
                _download_rec_data()
                arr = _load_temperature(month)
            _p1510_1_shared['digital_maps'][array_index] = arr
    return arr


def _load_temperature(month: int|None=None) -> array:
    if month is None:
        filename = 'T_Annual.TXT'
    else:
        filename = f'T_Month{month:02d}.TXT'
    return p1144_13.load_digital_map(join(_du.install_dir(), _p1510_1_shared['DATA_DIR'], filename))


def _download_rec_data() -> None:
    data_dir = _p1510_1_shared['DATA_DIR']
    full_path_data_dir = join(_du.install_dir(), data_dir)
    filenames = [f'T_Month{i:02d}.TXT' for i in range(1, 12+1)]
    filenames += ['T_Annual.TXT']
    lock = FileLock(_du.get_lockfile_pathname(data_dir))
    with lock:
        if _du.files_all_exist(full_path_data_dir, filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.1510-1-201706-I!!ZIP-E.zip'
            zip_pathname = _du.download(url, full_path_data_dir)
            _du.extract_files(zip_pathname, filenames, create_dirs=True, delete_zip_archive=True)
            _du.print_notice()
        else:
            _du.print_already_installed(full_path_data_dir, filenames)


_p1510_1_shared = {
    'DATA_DIR': 'p1510_1',
    'digital_maps_lock': Lock(),
    'digital_maps': [None] * 13
}
