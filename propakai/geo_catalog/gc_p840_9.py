# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.840-9
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.840-9-202308
"""

from enum import Enum
from ._interpolation_service import query, percent_to_str_v1, int_month_to_str


__all__ = ['ModelParam',
           'log_normal_approximation_params',
           'annual_integrated_cloud_liquid_water_content',
           'monthly_integrated_cloud_liquid_water_content']


class ModelParam(Enum):
    """To use as input for functions."""
    PROBABILITY = 1
    MEAN        = 2
    STD_DEV     = 3


def log_normal_approximation_params(lat: float, lon: float, param: ModelParam) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 3.3.

    Parameters for the log-normal approximation to the slant path statistical cloud attenuation:
    log-normal mean parameter mL, log-normal standard deviation parameter sL, probability of cloud
    at the desired location PL (%).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ModelParam): PROBABILITY, MEAN or STD_DEV.

    Returns:
        float: The log-normal mean parameter mL, the log-normal standard deviation parameter sL or
            the probability of cloud at the desired location PL (%).
    """
    asset_str = ''
    if param == ModelParam.PROBABILITY:
        asset_str = 'pl'
    elif param == ModelParam.MEAN:
        asset_str = 'ml'
    elif param == ModelParam.STD_DEV:
        asset_str = 'sl'
    return query('Rec-ITU-R-P840-9-202308_lognormal_approximation', lat, lon, ['asset'],
                 [asset_str])


def annual_integrated_cloud_liquid_water_content(lat: float, lon: float, param: ModelParam,
                                                 p_percent: float|None=None) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 4.

    Annual integrated cloud liquid water content statistics, L, in kg/m2, or, equivalently, mm, at
    the exceedance probability (CCDF) p_percent.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ModelParam): PROBABILITY, MEAN or STD_DEV.
        p_percent (float or None, optional): Exceedance probability (CCDF) of interest (%).
            p_percent is ignored when param is set to MEAN or STD_DEV. Otherwise, must be one of:
            0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90,
            95, 99, 100.

    Returns:
        L (float): Annual integrated cloud liquid water content statistics in kg/m2, or,
            equivalently, mm, at the exceedance probability (CCDF) p_percent.
    """
    asset_str = ''
    if param == ModelParam.PROBABILITY:
        if p_percent is None:
            raise ValueError('p_percent must be specified when param is set to PROBABILITY.')
        nominals = [0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70,
                    80, 90, 95, 99, 100]
        asset_str = percent_to_str_v1(p_percent, nominals)
    elif param == ModelParam.MEAN:
        asset_str = 'mean'
    elif param == ModelParam.STD_DEV:
        asset_str = 'std'
    return query('Rec-ITU-R-P840-9-202308_annual', lat, lon, ['asset'], [asset_str])


def monthly_integrated_cloud_liquid_water_content(lat: float, lon: float, month: int,
                                                  param: ModelParam, p_percent: float|None=None
                                                  ) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 4.

    Monthly integrated cloud liquid water content statistics, L, in kg/m2, or, equivalently, mm, at
    the exceedance probability (CCDF) p_percent.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        month (int): Month (1=Jan, ..., 12=Dec).
        param (ModelParam): PROBABILITY, MEAN or STD_DEV.
        p_percent (float or None, optional): Exceedance probability (CCDF) of interest (%).
            p_percent is ignored when param is set to MEAN or STD_DEV. Otherwise, must be one of:
            0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99, 100.

    Returns:
        L (float): Monthly integrated cloud liquid water content statistics in kg/m2, or,
            equivalently, mm, at the exceedance probability (CCDF) p_percent.
    """
    asset_str = ''
    if param == ModelParam.PROBABILITY:
        if p_percent is None:
            raise ValueError('p_percent must be specified when param is set to PROBABILITY.')
        nominals = [0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99, 100]
        asset_str = percent_to_str_v1(p_percent, nominals)
    elif param == ModelParam.MEAN:
        asset_str = 'mean'
    elif param == ModelParam.STD_DEV:
        asset_str = 'std'
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P840-9-202308_monthly', lat, lon, ['asset', 'month'],
                 [asset_str, month_str])
