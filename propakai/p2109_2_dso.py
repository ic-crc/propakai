# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.2109-2, dynamic shared object version (i.e. using a compiled binary).

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite this software
    package along with the underlying ITU-R standard:

    * **ITU-R Standard:** International Telecommunication Union (2023).
      *Recommendation ITU-R P.2109-2: Prediction of building entry loss*. Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.2109/en
"""

import ctypes as ct
from propakai import _bin_utils as _bu
from propakai.p2109_2 import BuildingType


__all__ = ['BuildingType',
           'building_entry_loss']


def building_entry_loss(f_ghz: float, theta_deg: float, p_percent: float, bldg: BuildingType
                        ) -> float:
    """
    ITU-R P.2109-2, Annex 1, Section 3.

    Gets the building entry loss (dB).

    Args:
        f_ghz (float): Frequency (GHz), with 0.08 <= f_ghz <= 100.
        theta_deg (float): Elevation angle of the path at the building façade (degrees above the
            horizontal), with -90 <= theta_deg <= 90.
        p_percent (float): Probability that loss is not exceeded (%), with 1 <= p_percent <= 99.
        bldg (BuildingType): Building type (TRADITIONAL or THERMALLY_EFFICIENT).

    Returns:
        L_BEL_omni (float): Building entry loss (dB).
    """
    if bldg == BuildingType.TRADITIONAL:
        thermally_efficient = False
    elif bldg == BuildingType.THERMALLY_EFFICIENT:
        thermally_efficient = True
    else:
        raise ValueError('Unexpected value for bldg.')
    cdll = _p2109_2_dso_shared['cdll']
    L_BEL_omni = cdll.P2109_2_BuildingEntryLoss(f_ghz, p_percent, theta_deg, thermally_efficient)
    return L_BEL_omni


def _init_dynamic_library() -> ct.CDLL:
    lib = _bu.get_dynamic_library('propakai_cpp')
    _set_args_and_return_ctypes(lib)
    return lib


def _set_args_and_return_ctypes(lib):
    lib.P2109_2_BuildingEntryLoss.argtypes = [ct.c_double, ct.c_double, ct.c_double, ct.c_bool]
    lib.P2109_2_BuildingEntryLoss.restype = ct.c_double


_p2109_2_dso_shared = {
    'cdll': _init_dynamic_library()
}
