# Copyright (c) 2025 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.835-7.

P.835 : Reference atmospheres.

https://www.itu.int/rec/R-REC-P.835/en
"""

from enum import Enum
from math import exp, sqrt
from typing import Callable


__all__ = ['ReferenceAtmosphere',
           'temperature',
           'pressure',
           'water_vapour_density']


class ReferenceAtmosphere(Enum):
    """
    Enumerates available reference atmospheres.
    """
    ITU_R           = 1
    SEASONAL_SUMMER = 2
    SEASONAL_WINTER = 3



def _geometric_to_geopentential_height(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 1, Section 1.1.

    Converts geopentential height (km) to geometric height (km).

    Args:
        z_km (float): Geometric height (km).
        
    Returns:
        H (float): Geopotential height (km).
    """
    return (6356.766*z_km)/(6356.766+z_km)


def _geopentential_to_geometric_height(h_km: float) -> float:
    """
    ITU-R P.835-7, Annex 1, Section 1.1.

    Converts geometric height (km) to geopentential height (km).

    Args:
        h_km (float): Geopotential height (km).
        
    Returns:
        Z (float): Geometric height (km).
    """
    return (6356.766*h_km)/(6356.766-h_km)


def temperature(z_km: float, atm: ReferenceAtmosphere=ReferenceAtmosphere.ITU_R, lat: float=45
                ) -> float:
    """
    ITU-R P.835-7, Annex 1 & 2.

    Gets the atmospheric temperature (K) at geometric height z_km (km).

    Args:
        z_km (float): Geometric height (km), with 0 <= z_km <= 100.
        atm (ReferenceAtmosphere, optional): A reference atmosphere (ITU_R, SEASONAL_SUMMER or
            SEASONAL_WINTER). Default value is ITU_R.
        lat (float, optional): Latitude (degrees), with -90 <= lat <= 90. Unused when atm is set to
            ITU_R. Default value is 45.

    Returns:
        T (float): The atmospheric temperature (K) at geometric height z_km.
    """
    if z_km < 0 or z_km > 100:
        raise ValueError('z_km is out of range.')

    if atm == ReferenceAtmosphere.ITU_R:
        T = _itur_temperature(z_km)
    else:
        T = _seasonal_interpolate(z_km=z_km, seasonal_atm=atm, lat=lat,
                                  low_lat_func=_low_lat_temperature,
                                  summer_mid_lat_func=_summer_mid_lat_temperature,
                                  winter_mid_lat_func=_winter_mid_lat_temperature,
                                  summer_high_lat_func=_summer_high_lat_temperature,
                                  winter_high_lat_func=_winter_high_lat_temperature)
    return T


def pressure(z_km: float, atm: ReferenceAtmosphere=ReferenceAtmosphere.ITU_R, lat: float=45
             ) -> float:
    """
    ITU-R P.835-7, Annex 1 & 2.

    Gets the total (barometric) atmospheric pressure (hPa) at geometric height z_km (km).

    Args:
        z_km (float): Geometric height (km), with 0 <= z_km <= 100.
        atm (ReferenceAtmosphere, optional): A reference atmosphere (ITU_R, SEASONAL_SUMMER or
            SEASONAL_WINTER). Default value is ITU_R.
        lat (float, optional): Latitude (degrees), with -90 <= lat <= 90. Unused when atm is set to
            ITU_R. Default value is 45.

    Returns:
        P (float): The total (barometric) atmospheric pressure (hPa) at geometric height z_km.
    """
    if z_km < 0 or z_km > 100:
        raise ValueError('z_km is out of range.')

    if atm == ReferenceAtmosphere.ITU_R:
        P = _itur_pressure(z_km)
    else:
        P = _seasonal_interpolate(z_km=z_km, seasonal_atm=atm, lat=lat,
                                  low_lat_func=_low_lat_pressure,
                                  summer_mid_lat_func=_summer_mid_lat_pressure,
                                  winter_mid_lat_func=_winter_mid_lat_pressure,
                                  summer_high_lat_func=_summer_high_lat_pressure,
                                  winter_high_lat_func=_winter_high_lat_pressure)
    return P


def water_vapour_density(z_km: float, atm: ReferenceAtmosphere=ReferenceAtmosphere.ITU_R,
                         lat: float=45) -> float:
    """
    ITU-R P.835-7, Annex 1 & 2.

    Gets the atmospheric water vapour density (g/m3) at geometric height z_km (km).

    Args:
        z_km (float): Geometric height (km), with 0 <= z_km <= 100.
        atm (ReferenceAtmosphere, optional): A reference atmosphere (ITU_R, SEASONAL_SUMMER or
            SEASONAL_WINTER). Default value is ITU_R.
        lat (float, optional): Latitude (degrees), with -90 <= lat <= 90. Unused when atm is set to
            ITU_R. Default value is 45.

    Returns:
        rho (float): The water-vapour density (g/m3) at geometric height z_km.
    """
    if z_km < 0 or z_km > 100:
        raise ValueError('z_km is out of range.')

    if atm == ReferenceAtmosphere.ITU_R:
        rho = 7.5*exp(-z_km/2)
        T = temperature(z_km)
        e = rho*T/216.7
        P = pressure(z_km)
        if e/P < 2E-6:
            rho = 2E-6*P*216.7/T
    else:
        rho = _seasonal_interpolate(z_km=z_km, seasonal_atm=atm, lat=lat,
                                    low_lat_func=_low_lat_water_vapour_density,
                                    summer_mid_lat_func=_summer_mid_lat_water_vapour_density,
                                    winter_mid_lat_func=_winter_mid_lat_water_vapour_density,
                                    summer_high_lat_func=_summer_high_lat_water_vapour_density,
                                    winter_high_lat_func=_winter_high_lat_water_vapour_density)
    return rho


def _itur_temperature(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 1, Section 1.1.

    Returns temperature (K) from geometric height (km).
    """
    if z_km < 86:
        H = _geometric_to_geopentential_height(z_km)
        if H <= 11:
            return 288.15-(6.5*H)
        elif H <= 20:
            return 216.65
        elif H <= 32:
            return 216.65+(H-20)
        elif H <= 47:
            return 228.65+(2.8*(H-32))
        elif H <= 51:
            return 270.65
        elif H <= 71:
            return 270.65-(2.8*(H-51))
        else:
            return 214.65-(2.0*(H-71))
    else:
        if z_km <= 91:
            return 186.8673
        else:
            x = (z_km-91)/19.9429
            return 263.1905-76.3232*sqrt(1-(x*x))


def _itur_pressure(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 1, Section 1.1.

    Returns pressure (hPa) from geometric height (km).
    """
    Z = z_km
    if Z < 86:
        H = _geometric_to_geopentential_height(Z)
        if H <= 11:
            return 1013.25*pow(288.15/(288.15-6.5*H), -34.1632/6.5)
        elif H <= 20:
            return 226.3226*exp(-34.1632*(H-11)/216.65)
        elif H <= 32:
            return 54.74980*pow(216.65/(216.65+(H-20)), 34.1632)
        elif H <= 47:
            return 8.680422*pow(228.65/(228.65+2.8*(H-32)), 34.1632/2.8)
        elif H <= 51:
            return 1.109106*exp(-34.1632*(H-47)/270.65)
        elif H <= 71:
            return 0.6694167*pow(270.65/(270.65-2.8*(H-51)), -34.1632/2.8)
        else:
            return 0.03956649*pow(214.65/(214.65-2.0*(H-71)), -34.1632/2.0)
    else:
        return exp(95.571899-(4.011801*Z)+(6.424731E-2*Z*Z)-(4.789660E-4*Z*Z*Z)+
                   (1.340543E-6*Z*Z*Z*Z))


def _low_lat_temperature(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.1.

    Returns the temperature (K) from geometric height (km) for low latitude (15 deg N) and all
    seasons.
    """
    if z_km < 17:
        return 300.4222-(6.3533*z_km)+(0.005886*z_km*z_km)
    elif z_km < 47:
        return 194+((z_km-17)*2.533)
    elif z_km < 52:
        return 270
    elif z_km < 80:
        return 270-((z_km-52)*3.0714)
    else:
        return 184


def _low_lat_pressure(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.1.

    Returns the total (barometric) pressure (hPa) from geometric height (km) for low latitude
    (15 deg N) and all seasons.
    """
    if z_km <= 10:
        return 1012.0306-(109.0338*z_km)+(3.6316*z_km*z_km)
    elif z_km <= 72:
        return _low_lat_pressure(10)*exp(-0.147*(z_km-10))
    else:
        return _low_lat_pressure(72)*exp(-0.165*(z_km-72))


def _low_lat_water_vapour_density(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.1.

    Returns the water vapour density (g/m3) from geometric height (km) for low latitude
    (15 deg N) and all seasons.
    """
    if z_km <= 15:
        return 19.6542*exp(-(0.2313*z_km)-(0.1122*z_km*z_km)+(0.01351*z_km*z_km*z_km)-
                           (0.0005923*z_km*z_km*z_km*z_km))
    else:
        return 0


def _summer_mid_lat_temperature(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.2.1.

    Returns the temperature (K) from geometric height (km) for summer at mid latitude (45 deg N).
    """
    if z_km < 13:
        return 294.9838-(5.2159*z_km)-(0.07109*z_km*z_km)
    elif z_km < 17:
        return 215.15
    elif z_km < 47:
        return 215.15*exp((z_km-17)*0.008128)
    elif z_km < 53:
        return 275
    elif z_km < 80:
        return 275+111.57755*(1-exp(0.0237*(z_km-53)))
    else:
        return 175


def _summer_mid_lat_pressure(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.2.1.

    Returns the total (barometric) pressure (hPa) from geometric height (km) for summer at mid
    latitude (45 deg N).
    """
    if z_km <= 10:
        return 1012.8186-(111.5569*z_km)+(3.8646*z_km*z_km)
    elif z_km <= 72:
        return _summer_mid_lat_pressure(10)*exp(-0.147*(z_km-10))
    else:
        return _summer_mid_lat_pressure(72)*exp(-0.165*(z_km-72))


def _summer_mid_lat_water_vapour_density(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.2.1.

    Returns the water vapour density (g/m3) from geometric height (km) for summer at mid latitude
    (45 deg N).
    """
    if z_km <= 15:
        return 14.3542*exp(-(0.4174*z_km)-(0.02290*z_km*z_km)+(0.001007*z_km*z_km*z_km))
    else:
        return 0


def _winter_mid_lat_temperature(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.2.2.

    Returns the temperature (K) from geometric height (km) for winter at mid latitude (45 deg N).
    """
    if z_km < 10:
        return 272.7241-(3.6217*z_km)-(0.1759*z_km*z_km)
    elif z_km < 33:
        return 218
    elif z_km < 47:
        return 218+((z_km-33)*3.3571)
    elif z_km < 53:
        return 265
    elif z_km < 80:
        return 265-((z_km-53)*2.0370)
    else:
        return 210


def _winter_mid_lat_pressure(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.2.2.

    Returns the total (barometric) pressure (hPa) from geometric height (km) for winter at mid
    latitude (45 deg N).
    """
    if z_km <= 10:
        return 1018.8627-(124.2954*z_km)+(4.8307*z_km*z_km)
    elif z_km <= 72:
        return _winter_mid_lat_pressure(10)*exp(-0.147*(z_km-10))
    else:
        return _winter_mid_lat_pressure(72)*exp(-0.155*(z_km-72))


def _winter_mid_lat_water_vapour_density(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.2.2.

    Returns the water vapour density (g/m3) from geometric height (km) for winter at mid latitude
    (45 deg N).
    """
    if z_km <= 10:
        return 3.4742*exp(-(0.2697*z_km)-(0.03604*z_km*z_km)+(0.0004489*z_km*z_km*z_km))
    else:
        return 0


def _summer_high_lat_temperature(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.3.1.

    Returns the temperature (K) from geometric height (km) for summer at high latitude (60 deg N).
    """
    if z_km < 10:
        return 286.8374-(4.7805*z_km)-(0.1402*z_km*z_km)
    elif z_km < 23:
        return 225
    elif z_km < 48:
        return 225*exp((z_km-23)*0.008317)
    elif z_km < 53:
        return 277
    elif z_km < 79:
        return 277-((z_km-53)*4.0769)
    else:
        return 171


def _summer_high_lat_pressure(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.3.1.

    Returns the total (barometric) pressure (hPa) from geometric height (km) for summer at high
    latitude (60 deg N).
    """
    if z_km <= 10:
        return 1008.0278-(113.2494*z_km)+(3.9408*z_km*z_km)
    elif z_km <= 72:
        return _summer_high_lat_pressure(10)*exp(-0.140*(z_km-10))
    else:
        return _summer_high_lat_pressure(72)*exp(-0.165*(z_km-72))


def _summer_high_lat_water_vapour_density(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.3.1.

    Returns the water vapour density (g/m3) from geometric height (km) for summer at high latitude
    (60 deg N).
    """
    if z_km <= 15:
        return 8.988*exp(-(0.3614*z_km)-(0.005402*z_km*z_km)-(0.001955*z_km*z_km*z_km))
    else:
        return 0


def _winter_high_lat_temperature(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.3.2.

    Returns the temperature (K) from geometric height (km) for winter at high latitude (60 deg N).
    """
    if z_km < 8.5:
        return 257.4345+(2.3474*z_km)-(1.5479*z_km*z_km)+(0.08473*z_km*z_km*z_km)
    elif z_km < 30:
        return 217.5
    elif z_km < 50:
        return 217.5+((z_km-30)*2.125)
    elif z_km < 54:
        return 260
    else:
        return 260-((z_km-54)*1.667)


def _winter_high_lat_pressure(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.3.2.

    Returns the total (barometric) pressure (hPa) from geometric height (km) for winter at high
    latitude (60 deg N).
    """
    if z_km <= 10:
        return 1010.8828-(122.2411*z_km)+(4.554*z_km*z_km)
    elif z_km <= 72:
        return _winter_high_lat_pressure(10)*exp(-0.147*(z_km-10))
    else:
        return _winter_high_lat_pressure(72)*exp(-0.150*(z_km-72))


def _winter_high_lat_water_vapour_density(z_km: float) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.3.2.

    Returns the water vapour density (g/m3) from geometric height (km) for winter at high latitude
    (60 deg N).
    """
    if z_km <= 10:
        return 1.2319*exp((0.07481*z_km)-(0.0981*z_km*z_km)+(0.00281*z_km*z_km*z_km))
    else:
        return 0


def _seasonal_interpolate(z_km: float, seasonal_atm: ReferenceAtmosphere, lat: float,
                          low_lat_func: Callable, summer_mid_lat_func: Callable,
                          winter_mid_lat_func: Callable, summer_high_lat_func: Callable,
                          winter_high_lat_func: Callable) -> float:
    """
    ITU-R P.835-7, Annex 2, Section 1.
    """
    abs_lat = abs(lat)
    if abs_lat <= 15:
        return low_lat_func(z_km)
    elif abs_lat >= 60:
        if seasonal_atm == ReferenceAtmosphere.SEASONAL_SUMMER:
            return summer_high_lat_func(z_km)
        else:
            return winter_high_lat_func(z_km)
    else:
        if abs_lat < 45:
            x0 = 15
            x1 = 45
            y0 = low_lat_func(z_km)
            if seasonal_atm == ReferenceAtmosphere.SEASONAL_SUMMER:
                y1 = summer_mid_lat_func(z_km)
            else:
                y1 = winter_mid_lat_func(z_km)
        else:
            x0 = 45
            x1 = 60
            if seasonal_atm == ReferenceAtmosphere.SEASONAL_SUMMER:
                y0 = summer_mid_lat_func(z_km)
                y1 = summer_high_lat_func(z_km)
            else:
                y0 = winter_mid_lat_func(z_km)
                y1 = winter_high_lat_func(z_km)
        x = abs_lat
        y = (y0*(x1-x) + y1*(x-x0))/(x1-x0)
        return y
