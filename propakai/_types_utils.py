# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Data types utilities for interoperability with C/C++.
"""

from typing import Tuple, Any, TYPE_CHECKING
from collections.abc import Sequence
import array
import ctypes as ct
from propakai import types
try:
    import numpy as np
except ImportError:
    np = None

if TYPE_CHECKING:
    import numpy as tnp


__all__ = ['to_c_double_ptr',
           'to_c_float_ptr',
           'to_c_int_ptr',
           'to_c_short_ptr']


def to_c_double_ptr(data: types.FloatArray|None, expected_num_elem: int|None=None
                    ) -> Tuple[ct._Pointer, int, array.array|Any|None]:
    """
    Gets a pointer to a C/C++ double array for interoperability.

    Args:
        data (FloatArray|None): The input data, which must be a sequence of float-like values,
            an array.array, or a numpy.ndarray. If None, returns a null pointer.
        expected_num_elem (int|None, optional): If provided and not None, checks that the number of
            elements in data equals this value. Raises ValueError if the check fails.

    Returns:
        ptr (ct._Pointer): Pointer to C/C++ double array (null pointer if data is None).
        num_elem (int): Number of double values in the contiguous array pointed to by ptr.
        backing (array.array|Any|None): Object that should be kept alive while ptr is used, to
            prevent the underlying data from being garbage collected (None if data is None).
    """
    return _to_c_ptr(data, ct.c_double, np.float64 if np else float, 'd', expected_num_elem)


def to_c_float_ptr(data: types.FloatArray|None, expected_num_elem: int|None=None
                   ) -> Tuple[ct._Pointer, int, array.array|Any|None]:
    """
    Gets a pointer to a C/C++ float array for interoperability.

    Args:
        data (FloatArray|None): The input data, which must be a sequence of float-like values,
            an array.array, or a numpy.ndarray. If None, returns a null pointer.
        expected_num_elem (int|None, optional): If provided and not None, checks that the number of
            elements in data equals this value. Raises ValueError if the check fails.

    Returns:
        ptr (ct._Pointer): Pointer to C/C++ float array (null pointer if data is None).
        num_elem (int): Number of float values in the contiguous array pointed to by ptr.
        backing (array.array|Any|None): Object that should be kept alive while ptr is used, to
            prevent the underlying data from being garbage collected (None if data is None).
    """
    return _to_c_ptr(data, ct.c_float, np.float32 if np else float, 'f', expected_num_elem)


def to_c_int_ptr(data: types.IntArray|None, expected_num_elem: int|None=None
                 ) -> Tuple[ct._Pointer, int, array.array|Any|None]:
    """
    Gets a pointer to a C/C++ int array for interoperability.

    Args:
        data (IntArray|None): The input data, which must be a sequence of int-like values,
            an array.array, or a numpy.ndarray. If None, returns a null pointer.
        expected_num_elem (int|None, optional): If provided and not None, checks that the number of
            elements in data equals this value. Raises ValueError if the check fails.

    Returns:
        ptr (ct._Pointer): Pointer to C/C++ int array (null pointer if data is None).
        num_elem (int): Number of int values in the contiguous array pointed to by ptr.
        backing (array.array|Any|None): Object that should be kept alive while ptr is used, to
            prevent the underlying data from being garbage collected (None if data is None).
    """
    return _to_c_ptr(data, ct.c_int, np.int32 if np else int, 'i', expected_num_elem)


def to_c_short_ptr(data: types.IntArray|None, expected_num_elem: int|None=None
                   ) -> Tuple[ct._Pointer, int, array.array|Any|None]:
    """
    Gets a pointer to a C/C++ short array for interoperability.

    Args:
        data (IntArray|None): The input data, which must be a sequence of int-like values,
            an array.array, or a numpy.ndarray. If None, returns a null pointer.
        expected_num_elem (int|None, optional): If provided and not None, checks that the number of
            elements in data equals this value. Raises ValueError if the check fails.

    Returns:
        ptr (ct._Pointer): Pointer to C/C++ short array (null pointer if data is None).
        num_elem (int): Number of short values in the contiguous array pointed to by ptr.
        backing (array.array|Any|None): Object that should be kept alive while ptr is used, to
            prevent the underlying data from being garbage collected (None if data is None).
    """
    return _to_c_ptr(data, ct.c_short, np.int16 if np else int, 'h', expected_num_elem)


def _to_c_ptr(data: types.NumArray|None, wanted_ct_type: Any, wanted_np_type: Any,
              wanted_array_type: str, expected_num_elem: int|None=None
              ) -> Tuple[ct._Pointer, int, array.array|Any|None]:
    if data is None:
        backing = None
        ptr = ct.POINTER(wanted_ct_type)()
        num_elem = 0
    else:
        if np is not None and isinstance(data, np.ndarray):
            # no copy performed if data is already in the required format
            np_data: Any = data  # Tells Pylance: stop treating this as a Sequence or array.array
            if np_data.dtype == wanted_np_type:
                backing = np_data
            else:
                backing = np_data.astype(wanted_np_type)
            if not backing.flags['C_CONTIGUOUS']:
                backing = np.ascontiguousarray(backing)
            ptr = backing.ctypes.data_as(ct.POINTER(wanted_ct_type))
            num_elem = backing.size
        elif isinstance(data, array.array):
            # no copy performed if data is already in the required format
            if data.typecode == wanted_array_type:
                backing = data
            else:
                backing = array.array(wanted_array_type, data)
            ptr = (wanted_ct_type*len(backing)).from_buffer(backing)
            num_elem = len(backing)
        elif isinstance(data, Sequence) and not isinstance(data, (str, bytes, bytearray)):
            # always require a copy
            backing = array.array(wanted_array_type, data)
            ptr = (wanted_ct_type*len(backing)).from_buffer(backing)
            num_elem = len(backing)
        else:
            raise TypeError('Expected Sequence, array.array or numpy.ndarray')
        if expected_num_elem is not None:
            if num_elem != expected_num_elem:
                raise ValueError('Unexpected array size')

    return ptr, num_elem, backing # must keep the backing alive while using the pointer
