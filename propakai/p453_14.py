# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.453-14.

P.453 : The radio refractive index: its formula and refractivity data.

https://www.itu.int/rec/R-REC-P.453/en
"""

from os.path import join
from threading import Lock
from array import array
from filelock import FileLock
from propakai import _download_utils as _du
from propakai import p1144_13


__all__ = ['median_annual_nwet']


def median_annual_nwet(lat: float, lon: float) -> float:
    """
    ITU-R P.453-14, Annex 1, Section 2.2.

    Gets the median value of the wet term of the surface refractivity exceeded for the average
    year (ppm).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        float: The median value of the wet term of the surface refractivity exceeded for the
            average year (ppm).
    """
    # lat from -90 to +90, lon from -180 to +180 in NWET_Annual_50.TXT
    lat_interval = 0.75
    lon_interval = 0.75
    num_rows = 241 # number of points from [-90, 90] latitude deg range,
                   # at 0.75 deg intervals: (180/0.75)+1
    row_size = 481 # number of points from [-180, 180] longitude deg range,
                   # at 0.75 deg intervals: (360/0.75)+1

    r = (90.0 + lat) / lat_interval
    c = (180.0 + lon) / lon_interval
    arr = _thread_safe_get_nwet_annual_50_array()
    return p1144_13.square_grid_bilinear_interpolation(arr, num_rows, row_size, r, c)


def _load_nwet_annual_50() -> array:
    return p1144_13.load_digital_map(join(_du.install_dir(), _p453_14_shared['DATA_DIR'],
                                          'NWET_Annual_50.TXT'))


def _thread_safe_get_nwet_annual_50_array() -> array:
    arr = _p453_14_shared['nwet_annual_50_array']
    if arr is not None:
        return arr
    with _p453_14_shared['nwet_annual_50_lock']:
        arr = _p453_14_shared['nwet_annual_50_array']
        if arr is None:
            try:
                arr = _load_nwet_annual_50()
            except FileNotFoundError:
                _download_rec_data()
                arr = _load_nwet_annual_50()
            _p453_14_shared['nwet_annual_50_array'] = arr
    return arr


def _download_rec_data() -> None:
    data_dir = _p453_14_shared['DATA_DIR']
    full_path_data_dir = join(_du.install_dir(), data_dir)
    filenames = ['NWET_Annual_50.TXT']
    lock = FileLock(_du.get_lockfile_pathname(data_dir))
    with lock:
        if _du.files_all_exist(full_path_data_dir, filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.453-14-201908-I!!ZIP-E.zip'
            zip_pathname1 = _du.download(url, full_path_data_dir)
            zip_pathname2 = _du.extract_files(zip_pathname1, ['P.453_NWET_Maps.zip'],
                                              create_dirs=True, delete_zip_archive=True)[0]
            zip_pathname3 = _du.extract_files(zip_pathname2, ['P.453_NWET_Maps_Annual.zip'],
                                              create_dirs=True, delete_zip_archive=True)[0]
            _du.extract_files(zip_pathname3, filenames, create_dirs=True, delete_zip_archive=True)
            _du.print_notice()
        else:
            _du.print_already_installed(full_path_data_dir, filenames)


_p453_14_shared = {
    'DATA_DIR': 'p453_14',
    'nwet_annual_50_lock': Lock(),
    'nwet_annual_50_array': None
}
