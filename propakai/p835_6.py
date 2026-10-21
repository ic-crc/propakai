# Copyright (c) 2025 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.835-6.

P.835 : Reference atmospheres.

https://www.itu.int/rec/R-REC-P.835/en
"""

from enum import Enum
from math import exp, sqrt


__all__ = ['ReferenceAtmosphere',
           'temperature',
           'pressure',
           'water_vapour_density']


class ReferenceAtmosphere(Enum):
    """
    Enumerates available reference atmospheres.
    """
    MEAN_ANNUAL_GLOBAL   = 1
    LOW_LATITUDE         = 2  # smaller than 22°
    MID_LATITUDE_SUMMER  = 3  # between 22° and 45°
    MID_LATITUDE_WINTER  = 4  # between 22° and 45°
    HIGH_LATITUDE_SUMMER = 5  # higher than 45°
    HIGH_LATITUDE_WINTER = 6  # higher than 45°


def _geometric_to_geopentential_height(h_km: float) -> float:
    """
    ITU-R P.835-6, Annex 1, Section 1.1.

    Converts geopentential height (km) to geometric height (km).

    Args:
        h_km (float): Geometric height (km).
        
    Returns:
        hp (float): Geopotential height (km).
    """
    return (6356.766*h_km)/(6356.766+h_km)


def _geopentential_to_geometric_height(hp_km: float) -> float:
    """
    ITU-R P.835-6, Annex 1, Section 1.1.

    Converts geometric height (km) to geopentential height (km).

    Args:
        hp_km (float): Geopotential height (km).
        
    Returns:
        h (float): Geometric height (km).
    """
    return (6356.766*hp_km)/(6356.766-hp_km)


def temperature(h_km: float, atm: ReferenceAtmosphere=ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL
                ) -> float:
    """
    ITU-R P.835-6, Annex 1.

    Gets the atmospheric temperature (K) at geometric height h_km (km).

    Args:
        h_km (float): Geometric height (km), with 0 <= h_km <= 100.
        atm (ReferenceAtmosphere, optional): A reference atmosphere. Default value is
            MEAN_ANNUAL_GLOBAL.

    Returns:
        T (float): The atmospheric temperature (K) at geometric height h_km.
    """
    if h_km < 0 or h_km > 100:
        raise ValueError('h_km is out of range.')

    if atm == ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL:
        T = _magra_temperature(h_km)
    elif atm == ReferenceAtmosphere.LOW_LATITUDE:
        T = _low_lat_temperature(h_km)
    elif atm == ReferenceAtmosphere.MID_LATITUDE_SUMMER:
        T = _summer_mid_lat_temperature(h_km)
    elif atm == ReferenceAtmosphere.MID_LATITUDE_WINTER:
        T = _winter_mid_lat_temperature(h_km)
    elif atm == ReferenceAtmosphere.HIGH_LATITUDE_SUMMER:
        T = _summer_high_lat_temperature(h_km)
    elif atm == ReferenceAtmosphere.HIGH_LATITUDE_WINTER:
        T= _winter_high_lat_temperature(h_km)
    else:
        raise ValueError('Invalid value for atm.')

    return T


def pressure(h_km: float, atm: ReferenceAtmosphere=ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL) -> float:
    """
    ITU-R P.835-6, Annex 1.

    Gets the total atmospheric pressure (hPa) at geometric height h_km (km).

    Args:
        h_km (float): Geometric height (km), with 0 <= h_km <= 100.
        atm (ReferenceAtmosphere, optional): A reference atmosphere. Default value is
            MEAN_ANNUAL_GLOBAL.

    Returns:
        P (float): The total atmospheric pressure (hPa) at geometric height h_km.
    """
    if h_km < 0 or h_km > 100:
        raise ValueError('h_km is out of range.')

    if atm == ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL:
        P = _magra_pressure(h_km)
    elif atm == ReferenceAtmosphere.LOW_LATITUDE:
        P = _low_lat_pressure(h_km)
    elif atm == ReferenceAtmosphere.MID_LATITUDE_SUMMER:
        P = _summer_mid_lat_pressure(h_km)
    elif atm == ReferenceAtmosphere.MID_LATITUDE_WINTER:
        P = _winter_mid_lat_pressure(h_km)
    elif atm == ReferenceAtmosphere.HIGH_LATITUDE_SUMMER:
        P = _summer_high_lat_pressure(h_km)
    elif atm == ReferenceAtmosphere.HIGH_LATITUDE_WINTER:
        P = _winter_high_lat_pressure(h_km)
    else:
        raise ValueError('Invalid value for atm.')

    return P


def water_vapour_density(h_km: float,
                         atm: ReferenceAtmosphere=ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL,
                         rho0_gm3: float=7.5, h0_km: float=2) -> float:
    """
    ITU-R P.835-6, Annex 1.

    Gets the water-vapour density (g/m3) at geometric height h_km (km).

    Args:
        h_km (float): Geometric height (km), with 0 <= h_km <= 100.
        atm (ReferenceAtmosphere, optional): A reference atmosphere. Default value is
            MEAN_ANNUAL_GLOBAL.
        rho0_gm3 (float, optional): Ground-level water vapour density (g/m3). Only applies when atm
            is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.
        h0_km (float, optional): Scale height (km). Only applies when atm is set to
            MEAN_ANNUAL_GLOBAL. Default value is 2.

    Returns:
        rho (float): The water-vapour density (g/m3) at geometric height h_km.
    """
    if h_km < 0 or h_km > 100:
        raise ValueError('h_km is out of range.')

    if atm == ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL:
        rho = rho0_gm3*exp(-h_km/h0_km)

        # See Section 1.2 of Annex 1
        P = pressure(h_km, atm)
        if rho/P < 2E-6:
            T = temperature(h_km, atm)
            rho = 2E-6 * 216.7 * P / T
            # make sure rho is not higher than the specified ground-level rho
            # i.e. to always return 0 if rho0_gm3 is 0
            rho = min(rho, rho0_gm3)
    elif atm == ReferenceAtmosphere.LOW_LATITUDE:
        rho = _low_lat_water_vapour_density(h_km)
    elif atm == ReferenceAtmosphere.MID_LATITUDE_SUMMER:
        rho = _summer_mid_lat_water_vapour_density(h_km)
    elif atm == ReferenceAtmosphere.MID_LATITUDE_WINTER:
        rho = _winter_mid_lat_water_vapour_density(h_km)
    elif atm == ReferenceAtmosphere.HIGH_LATITUDE_SUMMER:
        rho = _summer_high_lat_water_vapour_density(h_km)
    elif atm == ReferenceAtmosphere.HIGH_LATITUDE_WINTER:
        rho = _winter_high_lat_water_vapour_density(h_km)

    return rho


def _magra_pressure(h: float) -> float:
    if h < 86:
        hp = _geometric_to_geopentential_height(h)
        if hp <= 11:
            return 1013.25*pow(288.15/(288.15-6.5*hp), -34.1632/6.5)
        elif hp <= 20:
            return 226.3226*exp(-34.1632*(hp-11)/216.65)
        elif hp <= 32:
            return 54.74980*pow(216.65/(216.65+(hp-20)), 34.1632)
        elif hp <= 47:
            return 8.680422*pow(228.65/(228.65+2.8*(hp-32)), 34.1632/2.8)
        elif hp <= 51:
            return 1.109106*exp(-34.1632*(hp-47)/270.65)
        elif hp <= 71:
            return 0.6694167*pow(270.65/(270.65-2.8*(hp-51)), -34.1632/2.8)
        else:
            return 0.03956649*pow(214.65/(214.65-2.0*(hp-71)), -34.1632/2.0)
    else:
        return exp(95.571899-(4.011801*h)+(6.424731E-2*h*h)-(4.789660E-4*h*h*h)+
                   (1.340543E-6*h*h*h*h))


def _magra_temperature(h: float) -> float:
    if h < 86:
        hp = _geometric_to_geopentential_height(h)
        if hp <= 11:
            return 288.15-(6.5*hp)
        elif hp <= 20:
            return 216.65
        elif hp <= 32:
            return 216.65+(hp-20)
        elif hp <= 47:
            return 228.65+(2.8*(hp-32))
        elif hp <= 51:
            return 270.65
        elif hp <= 71:
            return 270.65-(2.8*(hp-51))
        else:
            return 214.65-(2.0*(hp-71))
    else:
        if h <= 91:
            return 186.8673
        else:
            x = (h-91)/19.9429
            return 263.1905-76.3232*sqrt(1-(x*x))


def _low_lat_temperature(h: float) -> float:
    if h < 17:
        return 300.4222-(6.3533*h)+(0.005886*h*h)
    elif h < 47:
        return 194+((h-17)*2.533)
    elif h < 52:
        return 270
    elif h < 80:
        return 270-((h-52)*3.0714)
    else:
        return 184


def _low_lat_pressure(h: float) -> float:
    if h <= 10:
        return 1012.0306-(109.0338*h)+(3.6316*h*h)
    elif h <= 72:
        return _low_lat_pressure(10)*exp(-0.147*(h-10))
    else:
        return _low_lat_pressure(72)*exp(-0.165*(h-72))


def _low_lat_water_vapour_density(h: float) -> float:
    if h <= 15:
        return 19.6542*exp(-(0.2313*h)-(0.1122*h*h)+(0.01351*h*h*h)-0.0005923*h*h*h*h)
    else:
        return 0


def _summer_mid_lat_temperature(h: float) -> float:
    if h < 13:
        return 294.9838-(5.2159*h)-(0.07109*h*h)
    elif h < 17:
        return 215.15
    elif h < 47:
        return 215.15*exp((h-17)*0.008128)
    elif h < 53:
        return 275
    elif h < 80:
        return 275+((1-exp((h-53)*0.06))*20)
    else:
        return 175


def _summer_mid_lat_pressure(h: float) -> float:
    if h <= 10:
        return 1012.8186-(111.5569*h)+(3.8646*h*h)
    elif h <= 72:
        return _summer_mid_lat_pressure(10)*exp(-0.147*(h-10))
    else:
        return _summer_mid_lat_pressure(72)*exp(-0.165*(h-72))


def _summer_mid_lat_water_vapour_density(h: float) -> float:
    if h <= 15:
        return 14.3542*exp(-(0.4174*h)-(0.02290*h*h)+(0.001007*h*h*h))
    else:
        return 0


def _winter_mid_lat_temperature(h: float) -> float:
    if h < 10:
        return 272.7241-(3.6217*h)-(0.1759*h*h)
    elif h < 33:
        return 218
    elif h < 47:
        return 218+((h-33)*3.3571)
    elif h < 53:
        return 265
    elif h < 80:
        return 265-((h-53)*2.0370)
    else:
        return 210


def _winter_mid_lat_pressure(h: float) -> float:
    if h <= 10:
        return 1018.8627-(124.2954*h)+(4.8307*h*h)
    elif h <= 72:
        return _winter_mid_lat_pressure(10)*exp(-0.147*(h-10))
    else:
        return _winter_mid_lat_pressure(72)*exp(-0.155*(h-72))


def _winter_mid_lat_water_vapour_density(h: float) -> float:
    if h <= 10:
        return 3.4742*exp(-(0.2697*h)-(0.03604*h*h)+(0.0004489*h*h*h))
    else:
        return 0


def _summer_high_lat_temperature(h: float) -> float:
    if h < 10:
        return 286.8374-(4.7805*h)-(0.1402*h*h)
    elif h < 23:
        return 225
    elif h < 48:
        return 225*exp((h-23)*0.008317)
    elif h < 53:
        return 277
    elif h < 79:
        return 277-((h-53)*4.0769)
    else:
        return 171


def _summer_high_lat_pressure(h: float) -> float:
    if h <= 10:
        return 1008.0278-(113.2494*h)+(3.9408*h*h)
    elif h <= 72:
        return _summer_high_lat_pressure(10)*exp(-0.140*(h-10))
    else:
        return _summer_high_lat_pressure(72)*exp(-0.165*(h-72))


def _summer_high_lat_water_vapour_density(h: float) -> float:
    if h <= 15:
        return 8.988*exp(-(0.3614*h)-(0.005402*h*h)-(0.001955*h*h*h))
    else:
        return 0


def _winter_high_lat_temperature(h: float) -> float:
    if h < 8.5:
        return 257.4345+(2.3474*h)-(1.5479*h*h)+(0.08473*h*h*h)
    elif h < 30:
        return 217.5
    elif h < 50:
        return 217.5+((h-30)*2.125)
    elif h < 54:
        return 260
    else:
        return 260-((h-54)*1.667)


def _winter_high_lat_pressure(h: float) -> float:
    if h <= 10:
        return 1010.8828-(122.2411*h)+(4.554*h*h)
    elif h <= 72:
        return _winter_high_lat_pressure(10)*exp(-0.147*(h-10))
    else:
        return _winter_high_lat_pressure(72)*exp(-0.150*(h-72))


def _winter_high_lat_water_vapour_density(h: float) -> float:
    if h <= 10:
        return 1.2319*exp((0.07481*h)-(0.0981*h*h)+(0.00281*h*h*h))
    else:
        return 0
