# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.834-9
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.834-9-201712
"""

from enum import Enum
from ._interpolation_service import query


__all__ = ['Coefficient',
           'ModelParam',
           'avg_height_reference_level',
           'coefficients',
           'vapour_pressure_decrease_factor',
           'air_total_pressure',
           'water_vapour_partial_pressure',
           'lapse_rate_mean_temperature_of_water_vapour',
           'mean_temperature_water_vapour']


class Coefficient(Enum):
    """To use as input for coefficients()."""
    A0H = 1
    A0W = 2
    A1H = 3
    A1W = 4
    A2H = 5
    A2W = 6
    B0H = 7
    B0W = 8
    B1H = 9
    B1W = 10
    B2H = 11
    B2W = 12


class ModelParam(Enum):
    """
    To use as input for vapour_pressure_decrease_factor(), air_total_pressure(),
    water_vapour_partial_pressure(), lapse_rate_mean_temperature_of_water_vapour() or
    mean_temperature_water_vapour().

    When DAY_OF_YEAR_OF_MIN_VALUE is used as the model parameter, the returned value is as follow:
    day of the year (1, 2, ... , 365.25), 1 = 1 January, 32 = 1 February, 60.25 = 1 March
    """
    AVERAGE_VALUE            = 1
    SEASONAL_FLUCTUATION     = 2
    DAY_OF_YEAR_OF_MIN_VALUE = 3


def avg_height_reference_level(lat: float, lon: float) -> float:
    """
    ITU-R P.834-9, Annex 1, Section 6.

    Average height of reference level with respect to the mean sea level, href (m).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        href (float): Average height of reference level with respect to the mean sea level (m).
    """
    return query('Rec-ITU-R-P834-9-201712_hreflev', lat, lon)


def coefficients(lat: float, lon: float, coeff: Coefficient) -> float:
    """
    ITU-R P.834-9, Annex 1, Section 6.

    Coefficients A0h, A1h, A2h, B1h, B2h, A0w, A1w, A2w, B1w and B2w for the calculation of the
    hydrostatic and wet components mh(θ) and mw(θ).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        coeff (Coefficient): Requested coefficient.

    Returns:
        float: Value of the requested coefficient.
    """
    asset_str = coeff.name[:2] + coeff.name[2].lower()
    return query('Rec-ITU-R-P834-9-201712_CoeffsMapFunction', lat, lon, ['asset'], [asset_str])


def vapour_pressure_decrease_factor(lat: float, lon: float, param: ModelParam) -> float:
    """
    ITU-R P.834-9, Annex 1, Section 6.

    Vapour pressure decrease factor, λ.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ParamType): One of AVERAGE_VALUE, SEASONAL_FLUCTUATION or DAY_OF_YEAR_OF_MIN_VALUE.

    Returns:
        λ (float): Vapour pressure decrease factor.
    """
    mapping = {
        ModelParam.AVERAGE_VALUE: 'lamd_gd_a1',
        ModelParam.SEASONAL_FLUCTUATION: 'lamd_gd_a2',
        ModelParam.DAY_OF_YEAR_OF_MIN_VALUE: 'lamd_gd_a3'
    }
    asset_str = mapping[param]
    return query('Rec-ITU-R-P834-9-201712_CoeffsVertExcPathLength', lat, lon, ['asset'],
                 [asset_str])


def air_total_pressure(lat: float, lon: float, param: ModelParam) -> float:
    """
    ITU-R P.834-9, Annex 1, Section 6.

    Air total pressure at the Earth's surface, ps (hPa).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ParamType): One of AVERAGE_VALUE, SEASONAL_FLUCTUATION or DAY_OF_YEAR_OF_MIN_VALUE.

    Returns:
        ps (float): Air total pressure at the Earth's surface (hPa).
    """
    mapping = {
        ModelParam.AVERAGE_VALUE: 'pres_gd_a1',
        ModelParam.SEASONAL_FLUCTUATION: 'pres_gd_a2',
        ModelParam.DAY_OF_YEAR_OF_MIN_VALUE: 'pres_gd_a3'
    }
    asset_str = mapping[param]
    return query('Rec-ITU-R-P834-9-201712_CoeffsVertExcPathLength', lat, lon, ['asset'],
                 [asset_str])


def water_vapour_partial_pressure(lat: float, lon: float, param: ModelParam) -> float:
    """
    ITU-R P.834-9, Annex 1, Section 6.

    Water vapour partial pressure at the Earth's surface, es (hPa).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ParamType): One of AVERAGE_VALUE, SEASONAL_FLUCTUATION or DAY_OF_YEAR_OF_MIN_VALUE.

    Returns:
        es (float): Water vapour partial pressure at the Earth's surface, es (hPa).
    """
    mapping = {
        ModelParam.AVERAGE_VALUE: 'vapr_gd_a1',
        ModelParam.SEASONAL_FLUCTUATION: 'vapr_gd_a1',
        ModelParam.DAY_OF_YEAR_OF_MIN_VALUE: 'vapr_gd_a1'
    }
    asset_str = mapping[param]
    return query('Rec-ITU-R-P834-9-201712_CoeffsVertExcPathLength', lat, lon, ['asset'],
                 [asset_str])


def lapse_rate_mean_temperature_of_water_vapour(lat: float, lon: float, param: ModelParam) -> float:
    """
    ITU-R P.834-9, Annex 1, Section 6.

    Lapse rate of the mean temperature of water vapour from Earth surface, αm (K/km).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ParamType): One of AVERAGE_VALUE, SEASONAL_FLUCTUATION or DAY_OF_YEAR_OF_MIN_VALUE.

    Returns:
        αm (float): Lapse rate of the mean temperature of water vapour from Earth surface (K/km).
    """
    mapping = {
        ModelParam.AVERAGE_VALUE: 'alfm_gd_a1',
        ModelParam.SEASONAL_FLUCTUATION: 'alfm_gd_a3',
        ModelParam.DAY_OF_YEAR_OF_MIN_VALUE: 'alfm_gd_a3'
    }
    asset_str = mapping[param]
    return query('Rec-ITU-R-P834-9-201712_CoeffsVertExcPathLength', lat, lon, ['asset'],
                 [asset_str])


def mean_temperature_water_vapour(lat: float, lon: float, param: ModelParam) -> float:
    """
    ITU-R P.834-9, Annex 1, Section 6.

    Mean temperature of the water vapour column above the surface, Tms (K).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ParamType): One of AVERAGE_VALUE, SEASONAL_FLUCTUATION or DAY_OF_YEAR_OF_MIN_VALUE.

    Returns:
        Tms (float): Mean temperature of the water vapour column above the surface (K).
    """
    mapping = {
        ModelParam.AVERAGE_VALUE: 'tmpm_gd_a1',
        ModelParam.SEASONAL_FLUCTUATION: 'tmpm_gd_a2',
        ModelParam.DAY_OF_YEAR_OF_MIN_VALUE: 'tmpm_gd_a3'
    }
    asset_str = mapping[param]
    return query('Rec-ITU-R-P834-9-201712_CoeffsVertExcPathLength', lat, lon, ['asset'],
                 [asset_str])
