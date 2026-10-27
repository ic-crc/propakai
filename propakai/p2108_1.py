# Copyright (c) 2025 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.2108-1.

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite this software
    package along with the underlying ITU-R standard:

    * **ITU-R Standard:** International Telecommunication Union (2021).
      *Recommendation ITU-R P.2108-1: Prediction of clutter loss*. Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.2108/en
"""

from enum import Enum
from math import log10, sqrt, pi, log, tan, degrees, atan
from propakai import p1057_7


__all__ = ['ClutterType',
           'height_gain_terminal_correction',
           'terrestrial_path_clutter_loss',
           'earth_space_clutter_loss']


class ClutterType(Enum):
    """Enumerates clutter types for the height_gain_terminal_correction() function."""
    WATER_SEA          = 1
    OPEN_RURAL         = 2
    SUBURBAN           = 3
    URBAN_TREES_FOREST = 4
    DENSE_URBAN        = 5


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
        if clut == ClutterType.URBAN_TREES_FOREST:
            r_m = 15.0
        elif clut == ClutterType.DENSE_URBAN:
            r_m = 20.0
        else:
            r_m = 10.0
    if h_m >= r_m:
        Ah = 0.0
    else:
        if clut==ClutterType.SUBURBAN or clut==ClutterType.URBAN_TREES_FOREST or \
           clut==ClutterType.DENSE_URBAN:
            Knu = 0.342*sqrt(f_ghz)
            hdif = r_m - h_m
            theta_clut_deg = degrees(atan(hdif/ws_m))
            v = Knu*sqrt(hdif*theta_clut_deg)
            if v <= -0.78:
                Jv = 0.0
            else:
                Jv = 6.9 + 20.0*log10(sqrt((v-0.1)*(v-0.1)+1.0)+v-0.1)
            Ah = Jv - 6.03
        else:
            Kh2 = 21.8 + 6.2*log10(f_ghz)
            Ah = -Kh2*log10(h_m/r_m)
    return Ah


def _terrestrial_path_clutter_loss(f_ghz: float, d_km: float, p_percent: float) -> float:
    """
    See terrestrial_path_clutter_loss().
    """
    d = d_km
    log10_f = log10(f_ghz)
    Ls = 32.98 + 23.9*log10(d) + 3.0*log10_f
    Ll = -2.0*log10(pow(10.0, -5.0*log10_f-12.5)+pow(10.0, -16.5))
    pow_Ll = pow(10.0, -0.2*Ll)
    pow_Ls = pow(10.0, -0.2*Ls)
    sigma_cb = sqrt((16.0*pow_Ll+36.0*pow_Ls) / (pow_Ll+pow_Ls))
    Lctt = -5.0*log10(pow_Ll+pow_Ls) - sigma_cb*p1057_7.q_inv(p_percent/100.0)
    return Lctt


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
    Lctt = _terrestrial_path_clutter_loss(f_ghz, d_km, p_percent)
    Lctt2km = _terrestrial_path_clutter_loss(f_ghz, 2.0, p_percent)
    return min(Lctt, Lctt2km)


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
    A1 = 0.05
    K1 = 93*pow(f_ghz, 0.175)
    a = -K1*(log(1-(p_percent/100)))
    b = 1/tan((A1*(1-(theta_deg/90)))+(pi*theta_deg/180))
    Lces = pow(a*b, 0.5*(90-theta_deg)/90)-1-(0.6*p1057_7.q_inv(p_percent/100))
    return Lces
