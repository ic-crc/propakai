# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.834-9.

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite this software
    package along with the underlying ITU-R standard:

    * **ITU-R Standard:** International Telecommunication Union (2017).
      *Recommendation ITU-R P.834-9: Effects of tropospheric refraction on radiowave propagation*.
      Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.834/en
"""

from math import log10


__all__ = ['beam_spreading_loss']


def beam_spreading_loss(theta0_deg: float, h_km: float) -> float:
    """
    ITU-R P.834-9, Annex 1, Section 5.

    "Beam spreading loss is a non-ohmic loss due to spreading of the antenna beam in the vertical
    elevation plane due to the variation of the radio refractive index vs height. This effect is
    insignificant for elevation angles above 5 degrees".

    Args:
        theta0_deg (float): Elevation angle of the line connecting the transmitting and receiving
            points (degrees), with theta0_deg < 10.
        h_km (float): Altitude of the lower point above sea level (km), with h_km <= 5.
    
    Returns:
        Abs (float): The signal loss due to beam spreading for a wave propagating through the total
            atmosphere in the Earth-space and space-Earth directions (dB).
    """
    t0 = theta0_deg
    h = h_km
    x = 0.5411 + (0.07446*t0) + (h*(0.06272+(0.0276*t0))) + (h*h*0.008288)
    y = 1.728 + (0.5411*t0) + (0.03723*t0*t0) + (h*(0.1815+(0.06272*t0)+(0.0138*t0*t0))) + \
        (h*h*(0.01727+(0.008288*t0)))
    B = 1 - (x/(y*y))

    Abs = -10*log10(B)

    return Abs
