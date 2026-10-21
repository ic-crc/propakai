# Copyright (c) 2025 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.838-3.

P.838 : Specific attenuation model for rain for use in prediction methods.

https://www.itu.int/rec/R-REC-P.838/en
"""

from math import log10, exp, radians, cos


__all__ = ['rain_attenuation',
           'coefficients']


def rain_attenuation(f_ghz: float, r_mmhr: float, theta_deg: float, tau_deg: float) -> float:
    """
    ITU-R P.838-3.

    Attenuation due to rain (dB/km).

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000.
        r_mmhr (float): Rain rate (mm/hr).
        theta_deg (float): Path elevation angle (degrees).
        tau_deg (float): Polarization tilt angle relative to the horizontal (degrees). Use 45° for
            circular polarization.

    Returns:
        gamma_R (float): Attenuation due to rain (dB/km).
    """
    k, alpha = coefficients(f_ghz, theta_deg, tau_deg)
    gamma_R = k*pow(r_mmhr, alpha)
    return gamma_R


def coefficients(f_ghz: float, theta_deg: float, tau_deg: float) -> tuple[float, float]:
    """
    ITU-R P.838-3.
    
    Gets the coefficients k and alpha from equations (4) and (5).

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000.
        theta_deg (float): Path elevation angle (degrees).
        tau_deg (float): Polarization tilt angle relative to the horizontal (degrees). Use 45° for
            circular polarization.

    Returns:
        k (float): Coefficient k.
        alpha (float): Coefficient alpha.
    """
    theta_rad = radians(theta_deg)
    tau_rad = radians(tau_deg)
    kH = _kH(f_ghz)
    kV = _kV(f_ghz)
    aH = _alphaH(f_ghz)
    aV = _alphaV(f_ghz)
    cos_th = cos(theta_rad)
    cos_2tau = cos(2*tau_rad)
    k = (kH+kV+((kH-kV)*cos_th*cos_th*cos_2tau))/2
    alpha = ((kH*aH)+(kV*aV)+(((kH*aH)-(kV*aV))*cos_th*cos_th*cos_2tau))/(2*k)
    return (k, alpha)


def _kH(f_ghz: float) -> float:
    mk = -0.18961
    ck = 0.71147
    a = [-5.33980, -0.35351, -0.23789, -0.94158]
    b = [-0.10008, 1.26970, 0.86036, 0.64552]
    c = [1.13098, 0.45400, 0.15354, 0.16817]
    return _k(f_ghz, a, b, c, mk, ck)


def _kV(f_ghz: float) -> float:
    mk = -0.16398
    ck = 0.63297
    a = [-3.80595, -3.44965, -0.39902, 0.50167]
    b = [0.56934, -0.22911, 0.73042, 1.07319]
    c = [0.81061, 0.51059, 0.11899, 0.27195]
    return _k(f_ghz, a, b, c, mk, ck)


def _alphaH(f_ghz: float) -> float:
    ma = 0.67849
    ca = -1.95537
    a = [-0.14318, 0.29591, 0.32177, -5.37610, 16.1721]
    b = [1.82442, 0.77564, 0.63773, -0.96230, -3.29980]
    c = [-0.55187, 0.19822, 0.13164, 1.47828, 3.43990]
    return _alpha(f_ghz, a, b, c, ma, ca)


def _alphaV(f_ghz: float) -> float:
    ma = -0.053739
    ca = 0.83433
    a = [-0.07771, 0.56727, -0.20238, -48.2991, 48.5833]
    b = [2.33840, 0.95545, 1.14520, 0.791669, 0.791459]
    c = [-0.76284, 0.54039, 0.26809, 0.116226, 0.116479]
    return _alpha(f_ghz, a, b, c, ma, ca)


def _k(f_ghz: float, a: list, b: list, c: list, mk: float, ck: float) -> float:
    log10_f = log10(f_ghz)
    sum_ = 0
    for j in range(0, 4, 1):
        base = (log10_f-b[j])/c[j]
        sum_ += a[j]*exp(-(base*base))
    log10_k = sum_+(mk*log10_f)+ck
    k = pow(10, log10_k)
    return k


def _alpha(f_ghz: float, a: list, b: list, c: list, ma: float, ca: float) -> float:
    log10_f = log10(f_ghz)
    sum_ = 0
    for j in range(0, 5, 1):
        base = (log10_f-b[j])/c[j]
        sum_ += a[j]*exp(-(base*base))
    alpha = sum_+(ma*log10_f)+ca
    return alpha
