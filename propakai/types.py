# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Additional data types.
"""
from collections.abc import Sequence
from typing import Any, TypeAlias

try:
    import numpy as _np
    import numpy.typing as _npt
except ImportError:
    # Fallback, still works if numpy is not installed
    NDArrayF: TypeAlias = Sequence[float] # type: ignore
    NDArrayI: TypeAlias = Sequence[int]   # type: ignore
else:
    # Pylance sees this LAST (so this one overwrites the first one)
    NDArrayF: TypeAlias = _npt.NDArray[_np.floating[Any]] # type: ignore
    NDArrayI: TypeAlias = _npt.NDArray[_np.integer[Any]]  # type: ignore


__all__ = ['FloatArray', 'IntArray', 'NumArray']


FloatArray = Sequence[float] | NDArrayF
"""
A flat sequence of floats, typically a list, tuple, array.array or a one-dimensional numpy array.
"""

IntArray = Sequence[int] | NDArrayI
"""
A flat sequence of integers, typically a list, tuple, array.array or a one-dimensional numpy array.
"""

NumArray = FloatArray | IntArray
"""
Either a FloatArray or an IntArray.
"""
