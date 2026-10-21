# Copyright (c) 2025 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.2109-2.

P.2109 : Prediction of building entry loss.

https://www.itu.int/rec/R-REC-P.2109/en
"""

from enum import Enum
from math import log10
from propakai import p1057_7


__all__ = ['BuildingType',
           'building_entry_loss']


class BuildingType(Enum):
    """Enumerates building types for the building_entry_loss() function."""
    TRADITIONAL         = 1
    THERMALLY_EFFICIENT = 2


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
        r, s, t, u, v, w, x, y, z = 12.64, 3.72, 0.96, 9.6, 2.0, 9.1, -3.0, 4.5, -2.0
    elif bldg == BuildingType.THERMALLY_EFFICIENT:
        r, s, t, u, v, w, x, y, z = 28.19, -3.00, 8.48, 13.5, 3.8, 27.8, -2.9, 9.4, -2.1
    else:
        raise ValueError('Unexpected value for bldg.')

    C = -3.0
    logf = log10(f_ghz)
    Lh = r + s*logf + t*logf*logf
    Le = 0.212*abs(theta_deg)
    mu1 = Lh + Le
    mu2 = w + x*logf
    sigma1 = u + v*logf
    sigma2 = y + z*logf
    FinvP = p1057_7.f_inv(p_percent/100.0)
    AP = FinvP*sigma1 + mu1
    BP = FinvP*sigma2 + mu2

    L_BEL_omni = 10.0*log10(pow(10.0, 0.1*AP) + pow(10.0, 0.1*BP) + pow(10.0, 0.1*C))
    return L_BEL_omni
