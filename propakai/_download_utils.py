# Copyright (c) 2025 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Utility module to download and extract ITU digital maps and other ITU data files that are integral
parts of recommendations.

see https://www.itu.int/en/Pages/copyright.aspx
"""

import os
import sys
import urllib.error
import urllib.request
import urllib.parse
from zipfile import ZipFile
import shutil
from platformdirs import user_data_dir


__all__ = ['install_dir',
           'print_notice',
           'download',
           'extract_all',
           'extract_files',
           'extract_exts',
           'extract_dirs',
           'files_all_exist',
           'print_already_installed',
           'get_lockfile_pathname',
           'delete_all_itu_files']


def install_dir() -> str:
    """Returns the installation directory for ITU digital maps and other ITU data files."""
    data_dir = user_data_dir(appname='propakai')
    install_directory = os.path.join(data_dir, 'itu_proprietary')
    return install_directory


def print_notice() -> None:
    """
    Prints notice to the console as requested by the ITU when downloading files from their website.
    See https://www.itu.int/en/Pages/copyright.aspx
    """
    print('\nNOTICE:\n  Data files obtained from the International Telecommunication Union ' \
          'website\n  (www.itu.int) are for personal use only. These files are not ' \
          'redistributable\n  without the explicit consent of the ITU.\n', flush=True)


def _handle_progress(block_num: int, block_size: int, total_size: int) -> object|None:
    """Updates the progress bar during downloads."""
    bar_length = 33
    progress = 0
    if total_size > 0:
        progress = min(1, block_num*block_size/total_size)
    block = int(bar_length*progress)
    hashes = '#'*block + '-'*(bar_length-block)
    text = f'\r[{hashes}] {progress*100:.1f}% of {total_size/1E6:.2f} MB  '
    sys.stdout.write(text)
    sys.stdout.flush()


def download(url: str, directory: str, filename:str|None=None, show_progress: bool=True) -> str:
    """
    Downloads the file at the specified URL into the specified directory, displaying a progress bar
    in the console window during the download process.

    Args:
        url (str): The uniform resource locator (URL) of the file to download.
        directory (str): The local directory where the file should be saved.
        filename (str|None, optional): If specified, the name of the file to be created locally in
            the speficied directory, otherwise the filename is extracted from the provided URL.
        show_progress (bool, optional): Whether to show a progress bar. Default is True.

    Returns:
        str: Full path to the downloaded file.
    """
    def _validate_url(url) -> str:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != 'https':
            raise ValueError(f'Refusing download: unapproved URL scheme "{parsed.scheme}".')
        allowed_hosts = {'www.itu.int', 'br-geoportal.itu.int'}
        if parsed.netloc not in allowed_hosts:
            raise ValueError(f'Refusing download: unapproved domain "{parsed.netloc}".')
        if not parsed.path or parsed.path.endswith('/'):
            raise ValueError('Refusing download: URL path is missing or invalid.')
        return url

    def _download(url, directory, filename, show_progress) -> str:
        os.makedirs(directory, exist_ok=True)
        if filename is None:
            filename = os.path.basename(url)
        pathname = os.path.join(directory, filename)
        print(f'\ndownloading {url}', flush=True)
        if show_progress is True:
            _handle_progress(0, 0, 0)
            reporthook = _handle_progress
        else:
            reporthook = None
        url = _validate_url(url)
        new_pathname, _ = urllib.request.urlretrieve(url, pathname, reporthook)
        print('')
        return new_pathname

    try:
        return _download(url, directory, filename, show_progress)
    except urllib.error.URLError:
        # recommendation version may have been superseded
        if url.find('-I!!ZIP') != -1:
            url = url.replace('-I!!ZIP', '-S!!ZIP')
            return _download(url, directory, filename, show_progress)
        else:
            raise


def extract_all(zip_pathname: str, delete_zip_archive: bool, create_new_dir: bool=False) -> None:
    """
    Extracts all files from the specified zip archive.

    Args:
        zip_pathname (str): Full path to the zip archive.
        delete_zip_archive (bool): Set to True to delete the zip archive file once done.
        create_new_dir (bool, optional): When set to True, the zip archive is extracted into a new
            directory named after the zip archive's filename. Default value is False.
    """
    zip_filename = os.path.basename(zip_pathname)
    output_dir = os.path.dirname(zip_pathname)
    if create_new_dir:
        zip_filename_no_ext, _ = os.path.splitext(zip_filename)
        output_dir = os.path.join(output_dir, zip_filename_no_ext)
        os.makedirs(output_dir, exist_ok=True)
    print(f'extracting all from "{zip_filename}" into "{os.path.realpath(output_dir)}"')
    with ZipFile(zip_pathname, 'r') as z_obj:
        z_obj.extractall(path=output_dir)
    if delete_zip_archive:
        print(f'deleting {zip_pathname}')
        os.remove(zip_pathname)


def extract_files(zip_pathname: str, filenames: list[str], create_dirs: bool,
                  delete_zip_archive: bool) -> list[str]:
    """
    Extracts specific file(s) from a zip archive. Files are extracted into the directory that
    contains the zip archive.
    
    Args:
        zip_pathname (str): Full path to the zip archive.
        filenames (list[str]): List of filenames to extract from the zip archive.
        create_dirs (bool): When True, the directory structure found within the zip archive is
            reproduced for each extracted file. When False, extracted files are directly placed
            within the directory containing the zip archive. 
        delete_zip_archive (bool): Set to True to delete the zip archive file once done.

    Returns:
        list[str]: List of extracted filenames with full paths.
    """
    z_items = _get_zip_items(zip_pathname)
    to_extract = []
    for z_item in z_items:
        filename = os.path.basename(z_item)
        if filename in filenames:
            to_extract.append(z_item)
    return _extract_specific_files(zip_pathname, to_extract, create_dirs, delete_zip_archive)


def extract_exts(zip_pathname: str, exts: list[str], create_dirs: bool, delete_zip_archive: bool
                 ) -> list[str]:
    """
    Extracts files having the specified extension(s) from a zip archive. Files are extracted into
    the directory that contains the zip archive.
    
    Args:
        zip_pathname (str): Full path to the zip archive.
        exts (list[str]): List of file extensions (do not include the dot).
        create_dirs (bool): When True, the directory structure found within the zip archive is
            reproduced for each extracted file. When False, extracted files are directly placed
            within the directory containing the zip archive. 
        delete_zip_archive (bool): Set to True to delete the zip archive file once done.

    Returns:
        list[str]: List of extracted filenames with full paths.
    """
    z_items = _get_zip_items(zip_pathname)
    to_extract = []
    for z_item in z_items:
        if os.path.splitext(z_item)[1].lstrip('.') in exts:
            to_extract.append(z_item)
    return _extract_specific_files(zip_pathname, to_extract, create_dirs, delete_zip_archive)


def extract_dirs(zip_pathname: str, parent_dirs: list[str], create_dirs: bool,
                 delete_zip_archive: bool) -> list[str]:
    """
    Extracts files within a one or more specific internal directories of a zip archive. Files are
    extracted into the directory that contains the zip archive.
    
    Args:
        zip_pathname (str): Full path to the zip archive.
        parent_dirs (list[str]): Parent directory(ies), within the zip archive, of files to extract.
        create_dirs (bool): When True, the directory structure found within the zip archive is
            reproduced for each extracted file. When False, extracted files are directly placed
            within the directory containing the zip archive. 
        delete_zip_archive (bool): Set to True to delete the zip archive file once done.

    Returns:
        list[str]: List of extracted filenames with full paths.
    """
    z_items = _get_zip_items(zip_pathname)
    to_extract = []
    for z_item in z_items:
        dirname = os.path.basename(os.path.dirname(z_item))
        if dirname in parent_dirs:
            to_extract.append(z_item)
    return _extract_specific_files(zip_pathname, to_extract, create_dirs, delete_zip_archive)


def _get_zip_items(zip_pathname: str) -> list[str]:
    """
    Get list of file items within a zip archive. A file item is a filename with its path within
    the zip archive.
    """
    with ZipFile(zip_pathname, 'r') as z_obj:
        z_items = [name for name in z_obj.namelist() if not name.endswith('/')] # file items only
    return z_items


def _extract_specific_files(zip_pathname: str, internal_pathnames: list[str], create_dirs: bool,
                            delete_zip_archive: bool) -> list[str]:
    """
    Extract specific files from a zip archive.

    Args:
        zip_pathname (str): Full path to the zip archive.
        internal_pathnames (list[str]): List of items to extract, that is the file names with their
            full path within the zip archive.
        create_dirs (bool): When True, the directory structure found within the zip archive is
            reproduced for each extracted file. When False, extracted files are directly placed
            within the directory containing the zip archive. 
        delete_zip_archive (bool): Set to True to delete the zip archive file once done.

    Returns:
        list[str]: List of extracted filenames with full paths.
    """
    extracted_pathnames = []
    zip_filename = os.path.basename(zip_pathname)
    extract_directory = os.path.dirname(zip_pathname)
    with ZipFile(zip_pathname, 'r') as z_obj:
        for z_item in internal_pathnames:
            item_filename = os.path.basename(z_item)
            print(f'extracting "{item_filename}" from "{zip_filename}" into ' \
                  f'"{os.path.realpath(extract_directory)}"')
            if create_dirs:
                extracted_pathnames.append(z_obj.extract(member=z_item, path=extract_directory))
            else:
                target_path = os.path.join(extract_directory, item_filename)
                with z_obj.open(z_item) as source, open(target_path, 'wb') as target:
                    target.write(source.read())
                    extracted_pathnames.append(target_path)
    if delete_zip_archive:
        print(f'deleting "{os.path.realpath(zip_pathname)}"')
        os.remove(zip_pathname)
    return extracted_pathnames


def files_all_exist(directory: str, filenames: list[str]) -> bool:
    """
    Verifies whether the specified files are all present within the specified directory (no
    sub-directory search takes place).

    Args:
        directory (str): A directory name. Ex. 'C:/temp'.
        filenames (list[str]): A list of filenames. Ex. ['notes.txt', 'map.dat'].

    Returns:
        bool: True when all files listed in filenames are found within the specified directory
            (no sub-directory search takes place), False otherwise.
    """
    for filename in filenames:
        pathname = os.path.join(directory, filename)
        if os.path.isfile(pathname) is False:
            return False
    return True


def print_already_installed(directory: str, filenames: list[str]) -> None:
    """
    Prints to the console a list of files to indicate them as being already installed.

    Args:
        directory (str): Directory containing the already installed files.
        filenames (list[str]): List of existing filenames in directory.
    """
    for filename in filenames:
        pathname = os.path.join(directory, filename)
        pathname = os.path.realpath(pathname)
        print(f'already installed: {pathname}')


def _get_lockfiles_directory() -> str:
    data_dir = user_data_dir(appname='propakai')
    lockfiles_dir = os.path.join(data_dir, 'locks')
    return lockfiles_dir


def get_lockfile_pathname(name: str) -> str:
    """
    Gets a proposed full path for a lock file to use when downloading ITU data files (the lock file
    is used to prevent concurrent access to the file(s) being downloaded).

    Args:
        name (str): Name to use for the lock file, without extension. Typically, this should be
            the name of the local directory for the ITU data files to be downloaded.
            Ex.: 'p453_14'.

    Returns:
        str: The full path to the propsed lock file.

    Example:
        ```
        from filelock import FileLock
        lock = FileLock(get_lockfile_pathname('p453_14'))
        with lock:
            # code to download file(s) here
        ```
    """
    lockfiles_dir = _get_lockfiles_directory()
    os.makedirs(lockfiles_dir, exist_ok=True)
    return os.path.join(lockfiles_dir, name + '.lock')


def delete_all_itu_files(skip_prompt: bool=False) -> None:
    """
    Deletes all installed ITU digital maps and other ITU data files. No check is made to verify
    whether the files are being used or not.

    Args:
        skip_prompt (bool, optional): If True, proceed will deletion without prompting user to
            confirm.
    """
    inst_dir = install_dir()
    file_count, total_size_bytes = _count_files_and_size(inst_dir)
    if file_count > 0:
        response = 'yes'
        if skip_prompt is False:
            print(f'Will delete {file_count} file(s) ({total_size_bytes / (1024*1024):.1f} MB)' \
                  ' from:')
            print(f'  {inst_dir}')
            response = input('Proceed (Y/n)? ').strip().lower()
        if response == 'yes' or response == 'y' or response == '':
            try:
                shutil.rmtree(inst_dir)
                print(f'{file_count} file(s) deleted ({total_size_bytes / (1024*1024):.1f} MB).')
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(e)
        else:
            print('Cleanup skipped.')
    else:
        print('No files to delete.')
    _lockfiles_cleanup()


def _count_files_and_size(directory) -> tuple[int, int]:
    file_count = 0
    total_size_bytes = 0
    for root, _, files in os.walk(directory):
        file_count += len(files)
        for f in files:
            fp = os.path.join(root, f)
            try:
                total_size_bytes += os.path.getsize(fp)
            except Exception: # pylint: disable=broad-exception-caught
                pass  # Inaccessible file, skip
    return file_count, total_size_bytes


def _lockfiles_cleanup() -> None:
    """Deletes unused lock files that may not have been properly deleted."""
    lockfiles_dir = _get_lockfiles_directory()
    if os.path.exists(lockfiles_dir) is False:
        return
    with os.scandir(lockfiles_dir) as entries:
        for entry in entries:
            if entry.is_file():
                _, extension = os.path.splitext(entry.path)
                if extension == '.lock':
                    try:
                        os.remove(entry.path)
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass # expected that lock files in used can't be deleted

_lockfiles_cleanup()
