# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Utility module for handling executable binary files.
"""

import os
import sys
import platform
from threading import Lock
import ctypes
from enum import Enum
import shutil


__all__ = ['OperatingSystem',
           'PythonBitArchitecture',
           'ProcessorArchitecture',
           'get_dynamic_library',
           'cleanup']


class OperatingSystem(Enum):
    WINDOWS = 1
    LINUX   = 2
    MAC_OS  = 3
    OTHER   = 4


class PythonBitArchitecture(Enum):
    PY_32_BIT = 1
    PY_64_BIT = 2


class ProcessorArchitecture(Enum):
    INTEL_AMD_64_BIT = 1
    INTEL_AMD_32_BIT = 2
    ARM_64_BIT       = 3
    ARM_32_BIT       = 4
    OTHER            = 5


def operating_system() -> OperatingSystem:
    """Operating system."""
    os_name = platform.system()
    if os_name == "Windows":
        return OperatingSystem.WINDOWS
    elif os_name == "Linux":
        return OperatingSystem.LINUX
    elif os_name == "Darwin":
        return OperatingSystem.MAC_OS
    else:
        return OperatingSystem.OTHER


def python_bit_arch() -> PythonBitArchitecture:
    """Bit architecture of the current python implementation."""
    if sys.maxsize > 2**31 - 1:
        return PythonBitArchitecture.PY_64_BIT
    else:
        return PythonBitArchitecture.PY_32_BIT


def processor_arch() -> ProcessorArchitecture:
    """Processor architecutre."""
    proc_arch = platform.machine().lower()
    if proc_arch == 'x86_64' or proc_arch == 'amd64':
        return ProcessorArchitecture.INTEL_AMD_64_BIT
    elif proc_arch == 'i386' or proc_arch == 'i686':
        return ProcessorArchitecture.INTEL_AMD_32_BIT
    elif proc_arch == 'aarch64' or proc_arch == 'arm64':
        return ProcessorArchitecture.ARM_64_BIT
    elif proc_arch == 'armv7l':
        return ProcessorArchitecture.ARM_32_BIT
    else:
        return ProcessorArchitecture.OTHER


def get_dynamic_library(filename_no_ext: str) -> ctypes.CDLL:
    """
    Gets a loaded dll/shared library, loading it first if not already loaded.

    Args:
        filename_no_ext (str): Filename without extension of the dll/shared library to load.
    
    Returns:
        (ctypes.CDLL): A representation of the loaded dll/shared library.
    """
    with _bin_utils_shared['loaded_dyn_libs_lock']:
        libs = _bin_utils_shared['loaded_dyn_libs']
        if filename_no_ext not in libs:
            lib = _load_dynamic_library(filename_no_ext)
            libs[filename_no_ext] = lib
        lib = libs[filename_no_ext]
    return lib


def _load_dynamic_library(filename_no_ext: str) -> ctypes.CDLL:
    """
    Loads a dll/shared library.

    Args:
        filename_no_ext (str): Filename without extension of the dll/shared library to load.
    
    Returns:
        (ctypes.CDLL): A representation of the loaded dll/shared library.
    """
    module_dir = os.path.dirname(os.path.abspath(__file__))

    oper_sys = operating_system()
    if oper_sys == OperatingSystem.WINDOWS:
        ext = 'dll'
        os_dir = os.path.join(module_dir, 'bin', 'win')
    elif oper_sys == OperatingSystem.LINUX:
        ext = 'so'
        os_dir = os.path.join(module_dir, 'bin', 'linux')
    elif oper_sys == OperatingSystem.MAC_OS:
        ext = 'dylib'
        os_dir = os.path.join(module_dir, 'bin', 'macos')
    else:
        raise ImportError('No compiled binary available for the current platform.')

    proc_arch = processor_arch()
    py_bit_arch = python_bit_arch()
    if proc_arch == ProcessorArchitecture.INTEL_AMD_64_BIT and \
       py_bit_arch == PythonBitArchitecture.PY_64_BIT:
        dso_dir = os.path.join(os_dir, 'x86_64')
    elif proc_arch == ProcessorArchitecture.ARM_64_BIT and \
       py_bit_arch == PythonBitArchitecture.PY_64_BIT:
        dso_dir = os.path.join(os_dir, 'arm64')
    else:
        raise ImportError('No compiled binary available for the current platform.')

    lib_pathname = os.path.join(dso_dir, f'{filename_no_ext}.{ext}')
    if not os.path.isfile(lib_pathname):
        if oper_sys == OperatingSystem.MAC_OS:
            # try universal (fat bin) instead on macOS
            dso_dir = os.path.join(module_dir, 'bin', 'macos', 'universal')
            lib_pathname = os.path.join(dso_dir, f'{filename_no_ext}.{ext}')
            if not os.path.isfile(lib_pathname):
                raise FileNotFoundError(f"{lib_pathname} not found.")
        else:
            raise FileNotFoundError(f"{lib_pathname} not found.")

    lib = ctypes.CDLL(lib_pathname)
    if lib is None:
        raise ImportError(f'Failed to load {lib_pathname} as dynamic library.')

    return lib


def cleanup(skip_prompt: bool=True) -> None:
    """
    Deletes unsuitable binaries for the current OS and processor architecture.
    
    Args:
        skip_prompt (bool, optional): If True, proceed will deletion without prompting user to
            confirm.
    """
    module_dir = os.path.dirname(os.path.abspath(__file__))
    win_dir = os.path.join(module_dir, 'bin', 'win')
    linux_dir = os.path.join(module_dir, 'bin', 'linux')
    macos_dir = os.path.join(module_dir, 'bin', 'macos')

    oper_sys = operating_system()
    if oper_sys == OperatingSystem.WINDOWS:
        cur_os_dir = win_dir
        to_delete = [linux_dir, macos_dir]
    elif oper_sys == OperatingSystem.LINUX:
        cur_os_dir = linux_dir
        to_delete = [win_dir, macos_dir]
    elif oper_sys == OperatingSystem.MAC_OS:
        cur_os_dir = macos_dir
        to_delete = [win_dir, linux_dir]
    else:
        cur_os_dir = None
        to_delete = [win_dir, linux_dir, macos_dir]

    if cur_os_dir is not None:
        proc_arch = processor_arch()
        if proc_arch == ProcessorArchitecture.INTEL_AMD_64_BIT:
            to_delete.append(os.path.join(cur_os_dir, 'arm64'))
        elif proc_arch == ProcessorArchitecture.ARM_64_BIT:
            to_delete.append(os.path.join(cur_os_dir, 'x86_64'))
        else:
            to_delete.append(os.path.join(cur_os_dir, 'arm64'))
            to_delete.append(os.path.join(cur_os_dir, 'x86_64'))
            to_delete.append(os.path.join(cur_os_dir, 'universal'))

    existing_to_delete = [d for d in to_delete if os.path.isdir(d)]
    if len(existing_to_delete) > 0:
        response = 'yes'
        if skip_prompt is False:
            print('Will delete:')
            for d in existing_to_delete:
                print(f'  {d}')
            response = input('Proceed (Y/n)? ').strip().lower()
        if response == 'yes' or response == 'y' or response == '':
            for d in existing_to_delete:
                try:
                    shutil.rmtree(d)
                    print(f'Deleted directory "{d}"')
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(e)
        else:
            print('Cleanup skipped.')
    else:
        print('No cleanup required.')


_bin_utils_shared = {
    'loaded_dyn_libs_lock': Lock(),
    'loaded_dyn_libs': {}
}
