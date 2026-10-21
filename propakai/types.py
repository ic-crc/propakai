# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Additional data types.
"""
from collections.abc import Sequence
import array
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING: # seen as True by static analysis tools (type checkers), False at runtime
    import numpy as np
    import numpy.typing as npt
else:
    np = None
    npt = None

try:
    import numpy as _np
    import numpy.typing as _npt
    NDArrayF = _npt.NDArray[_np.floating]
    NDArrayI = _npt.NDArray[_np.integer]
except ImportError:
    # Fallback, still works if numpy is not installed
    NDArrayF = Any
    NDArrayI = Any


__all__ = ['FloatArray', 'IntArray', 'NumArray']


FloatArray = Sequence[float] | array.array | NDArrayF
"""
A flat sequence of floats, typically a list, tuple, array.array or a one-dimensional numpy array.
"""

IntArray = Sequence[int] | array.array | NDArrayI
"""
A flat sequence of integers, typically a list, tuple, array.array or a one-dimensional numpy array.
"""

NumArray = FloatArray | IntArray
"""
Either a FloatArray or an IntArray.
"""
