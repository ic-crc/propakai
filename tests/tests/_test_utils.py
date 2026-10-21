# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Utility module for tests.
"""
import os
import enum
from propakai import _download_utils as _du

script_dir = os.path.dirname(os.path.abspath(__file__))

__all__ = ['get_pathname',
           'get_pathnames']


class ValidationFile(enum.Enum):
    """Enumerates validation files for testing purposes."""
    CG_3M3J_13_VALEX_REV830 = 1
    CLUTTER_AND_BEL_WORKBOOK_V2 = 2


class ValidationFileGroup(enum.Enum):
    """Enumerates groups of validation files for testing purposes."""
    P528_5_DATA_TABLES = 1
    P1812_8_VALIDATION_PROFILES = 2
    P452_18_VALIDATION_PROFILES = 3
    P1546_6_VALIDATION_PROFILES = 4
    P2001_6_VALIDATION_PROFILES = 5


def get_pathname(file: ValidationFile) -> str:
    """
    Returns the full path to the specified validation files. The file is downloaded first when not
    already locally present.

    Args:
        file (ValidationFile): A validation file.

    Returns:
        str: Full path to the requested file.
    """
    if file is ValidationFile.CG_3M3J_13_VALEX_REV830:
        target_dir = os.path.join(script_dir, 'validation_data', 'itu_proprietary')
        # see https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx under "Validation Examples" tab.
        pathname = _download_file(
            url='https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Validation%20Example/CG-3M3J-13-ValEx-Rev8.3.0.xlsx',
            directory=target_dir, overwrite=False, print_itu_notice=True)
        return pathname
    elif file is ValidationFile.CLUTTER_AND_BEL_WORKBOOK_V2:
        target_dir = os.path.join(script_dir, 'validation_data', 'itu_proprietary')
        # see https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Pages/digprod.aspx under "Software Products" tab.
        pathname = _download_file(
            url='https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Software%20Products/Clutter%20and%20BEL%20workbook_V2.xlsx',
            directory=target_dir, overwrite=False, print_itu_notice=True)
        return pathname
    return None


def get_pathnames(file_group: ValidationFileGroup) -> list[str]:
    """
    Returns the list of full paths to the files compositing the specified group. The files are
    downloaded first when not already locally present.

    Args:
        file_group (ValidationFileGroup): A group of related validation files.

    Returns:
        str: List of full paths to the requested files.
    """
    if file_group is ValidationFileGroup.P528_5_DATA_TABLES:
        target_dir = os.path.join(script_dir, 'validation_data', 'itu_proprietary', 'p528_5')
        pathnames = _get_pathnames(target_dir, 'csv')
        if len(pathnames) == 0:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.528-5-202109-I!!ZIP-E.zip'
            zip_pathname = _du.download(url, target_dir)
            pathnames = _du.extract_dirs(zip_pathname, ['Data Tables'], create_dirs=False,
                                         delete_zip_archive=True)
            _du.print_notice()
            return pathnames
        return pathnames

    elif file_group is ValidationFileGroup.P1812_8_VALIDATION_PROFILES:
        target_dir = os.path.join(script_dir, 'validation_data', 'itu_proprietary', 'p1812_8')
        pathnames = _get_pathnames(target_dir, 'csv')
        if len(pathnames) == 0:
            url = 'https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Software%20Products/P_1812_8.zip'
            zip_pathname = _du.download(url, target_dir)
            pathnames = _du.extract_dirs(zip_pathname, ['validation_profiles'], create_dirs=False,
                                         delete_zip_archive=True)
            _du.print_notice()
            return pathnames
        return pathnames

    elif file_group is ValidationFileGroup.P452_18_VALIDATION_PROFILES:
        target_dir = os.path.join(script_dir, 'validation_data', 'itu_proprietary', 'p452_18')
        pathnames = _get_pathnames(target_dir, 'csv')
        if len(pathnames) == 0:
            url = 'https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Validation%20Example/Validation%20examples%20for%20Recommendation%20ITU-R%20P.452-18%20-%20Ver%2018.0.zip'
            zip_pathname = _du.download(url, target_dir)
            pathnames = _du.extract_dirs(zip_pathname, ['profiles', 'results'], create_dirs=False,
                                         delete_zip_archive=True)
            _du.print_notice()
            return pathnames
        return pathnames
    
    elif file_group is ValidationFileGroup.P1546_6_VALIDATION_PROFILES:
        target_dir = os.path.join(script_dir, 'validation_data', 'itu_proprietary', 'p1546_6')
        pathnames = _get_pathnames(target_dir, 'csv')
        if len(pathnames) == 0:
            url = 'https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Validation%20Example/R19-WP3K-C-0264%21N05-P2%21ZIP-E.zip'
            zip_pathname = _du.download(url, target_dir)
            pathnames = _du.extract_dirs(zip_pathname, ['validation_profiles'], create_dirs=False,
                                         delete_zip_archive=True)
            _du.print_notice()
            return pathnames
        return pathnames

    elif file_group is ValidationFileGroup.P2001_6_VALIDATION_PROFILES:
        target_dir = os.path.join(script_dir, 'validation_data', 'itu_proprietary', 'p2001_6')
        pathnames = _get_pathnames(target_dir, 'csv')
        if len(pathnames) == 0:
            url = 'https://www.itu.int/en/ITU-R/study-groups/rsg3/rwp3m/Software%20Products/P_2001_6.zip'
            zip_pathname = _du.download(url, target_dir)
            pathnames = _du.extract_dirs(zip_pathname, ['validation_examples'],
                                         create_dirs=False,
                                         delete_zip_archive=True)
            _du.print_notice()
            return pathnames
        return pathnames

    return None


def _download_file(url: str, directory: str, overwrite: bool=False, print_itu_notice=True) -> str:
    """
    Downloads the file at the specified URL into the specified directory.

    Args:
        url (str): The uniform resource locator (URL) of the file to download.
        directory (str): Full path directory where the file should be saved.
        overwrite (bool): Whether the file should be downloaded and overwritten when it already
            exists.
        print_itu_notice (bool): Should be set to True when the file to download is from the ITU
            website.

    Returns:
        str: Full path to the downloaded file.
    """
    filename = os.path.basename(url)
    #filename = urllib.parse.unquote(filename)
    pathname = os.path.join(directory, filename)
    if overwrite is True or os.path.exists(pathname) is False:
        new_pathname = _du.download(url, directory)
        if print_itu_notice is True:
            _du.print_notice()
        return new_pathname
    return pathname


def _get_pathnames(directory: str, extension: str|None=None) -> list[str]:
    """
    Returns a list of full paths to files located in the specified directory and any sub-directory.
    """
    pathnames = []
    for root, _dirs, files in os.walk(directory):
        for f in files:
            pathname = os.path.join(root, f)
            if extension is not None:
                if os.path.splitext(pathname)[1].lstrip('.') == extension:
                    pathnames.append(pathname)
            else:
                pathnames.append(pathname)
    return pathnames
