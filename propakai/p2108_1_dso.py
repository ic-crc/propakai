# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.2108-1, dynamic shared object version (i.e. using a compiled binary).

P.2108 : Prediction of clutter loss.

https://www.itu.int/rec/R-REC-P.2108/en
"""

import ctypes as ct
from propakai import _bin_utils as _bu
from propakai.p2108_1 import ClutterType


__all__ = ['ClutterType',
           'height_gain_terminal_correction',
           'terrestrial_path_clutter_loss',
           'earth_space_clutter_loss']


def height_gain_terminal_correction(f_ghz: float, h_m: float, clut: ClutterType,
                                    r_m: float|None=None, ws_m: float=27.0) -> float:
    """
    ITU-R P.2108-1, Annex 1, Section 3.1.

    Gets the additional loss (dB) from the height gain terminal correction model.

    "An additional loss, Ah, is calculated which can be added to the basic transmission loss of a
    path calculated above the clutter, therefore basic transmission loss should be calculated
    to/from the height of the representative clutter height used. This model can be applied to both
    transmitting and receiving ends of the path."

    Args:
        f_ghz (float): Frequency (GHz), with 0.03 <= f_ghz <= 3.
        h_m (float): Antenna height (m), with 0 <= h_m.
        clut (ClutterType): One of the clutter types from the recommendation's Table 3.
        r_m (float or None, optional): Representative clutter height (m), with 0 < r_m. When r_m is
            set to None, the default representative clutter height for the specified clutter type
            is used. Default value is None.
        ws_m (float, optional): Street width (m). Default value is 27.
    
    Returns:
        Ah (float): Additional loss (dB).
    """
    if r_m is None:
        r_m = 0.0 # indicates to use default TABLE 3 values in cpp version
    cdll = _p2108_1_dso_shared['cdll']
    return cdll.P2108_1_HeightGainTerminalCorrection(f_ghz, h_m, clut, r_m, ws_m)


def terrestrial_path_clutter_loss(f_ghz: float, d_km: float, p_percent: float) -> float:
    """
    ITU-R P.2108-1, Annex 1, Section 3.2.

    "Statistical model which can be applied for modelling the clutter loss distribution for urban
    and suburban environments." Terminal heights are assumed to be well below the clutter height.

    Args:
        f_ghz (float): Frequency (GHz), with 0.5 <= f_ghz <= 67.
        d_km: Distance (km), with 0.25 <= d_km.
        p_percent: Percentage of locations (%), with 0 < p_percent < 100.
    
    Returns:
        Lctt (float): Median clutter loss for terrestrial paths (dB).
    """
    cdll = _p2108_1_dso_shared['cdll']
    return cdll.P2108_1_TerrestrialPathClutterLoss(f_ghz, d_km, p_percent)


def earth_space_clutter_loss(f_ghz: float, theta_deg: float, p_percent: float) -> float:
    """
    ITU-R P.2108-1, Annex 1, Section 3.3.

    "Statistical distribution of clutter loss where one end of the interference path is within
    man-made clutter, and the other is a satellite, aeroplane, or other platform above the surface
    of the Earth." "This model is applicable to urban and suburban environments."

    Args:
        f_ghz (float): Frequency (GHz), with 0.5 <= f_ghz <= 67.
        theta_deg (float): Elevation angle (degrees). The angle of the airborne platform or
            satellite as seen from the terminal, with 0 <= theta_deg <= 90.
        p_percent (float): Percentage of locations (%), with 0 < p_percent < 100.
    
    Returns:
        Lces (float): Additonal clutter loss (dB), "which can be added to the basic transmission
            loss of a path calculated. "
    """
    cdll = _p2108_1_dso_shared['cdll']
    return cdll.P2108_1_EarthSpaceClutterLoss(f_ghz, theta_deg, p_percent)


def _init_dynamic_library() -> ct.CDLL:
    lib = _bu.get_dynamic_library('propakai_cpp')
    _set_args_and_return_ctypes(lib)
    return lib


def _set_args_and_return_ctypes(lib):
    lib.P2108_1_HeightGainTerminalCorrection.argtypes = [ct.c_double, ct.c_double, ct.c_int,
                                                         ct.c_double, ct.c_double]
    lib.P2108_1_HeightGainTerminalCorrection.restype = ct.c_double

    lib.P2108_1_TerrestrialPathClutterLoss.argtypes = [ct.c_double, ct.c_double, ct.c_double]
    lib.P2108_1_TerrestrialPathClutterLoss.restype = ct.c_double

    lib.P2108_1_EarthSpaceClutterLoss.argtypes = [ct.c_double, ct.c_double, ct.c_double]
    lib.P2108_1_EarthSpaceClutterLoss.restype = ct.c_double


_p2108_1_dso_shared = {
    'cdll': _init_dynamic_library()
}
