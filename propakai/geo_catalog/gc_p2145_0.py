# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.2145-0
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.2145-0-202208
"""

from enum import Enum
from ._interpolation_service import query, percent_to_str_v1, int_month_to_str


__all__ = ['ModelParam',

           'annual_surface_total_pressure',
           'annual_surface_temperature',
           'annual_surface_water_vapour_density',
           'annual_integrated_water_vapour_content',

           'annual_surface_total_pressure_stats',
           'annual_surface_temperature_stats',
           'annual_surface_water_vapour_density_stats',
           'annual_integrated_water_vapour_content_stats',

           'annual_surface_total_pressure_scale_height',
           'annual_surface_temperature_scale_height',
           'annual_water_vapour_scale_height',

           'monthly_surface_total_pressure',
           'monthly_surface_temperature',
           'monthly_surface_water_vapour_density',
           'monthly_integrated_water_vapour_content',

           'monthly_surface_total_pressure_stats',
           'monthly_surface_temperature_stats',
           'monthly_surface_water_vapour_density_stats',
           'monthly_integrated_water_vapour_content_stats',

           'monthly_surface_total_pressure_scale_height',
           'monthly_surface_temperature_scale_height',
           'monthly_water_vapour_scale_height',

           'surface_height',

           'weibull_scale_parameter',
           'weibull_shape_parameter']


class ModelParam(Enum):
    """To use as input for functions."""
    MEAN        = 1
    STD_DEV     = 2


def annual_surface_total_pressure(lat: float, lon: float, p_percent: float) -> float:
    """
    ITU-R P.2145-0.

    Annual surface total (barometric) pressure, Ps (hPa), at an exceedance probability of
    p_percent.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Exceedance probability (%). Must be one of: 0.01, 0.02, 0.03, 0.05, 0.1,
            0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99.

    Returns:
        Ps (float): Annual surface total (barometric) pressure (hPa), at an exceedance probability
            of p_percent.
    """
    nominals = (0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80,
                90, 95, 99)
    p_str = percent_to_str_v1(p_percent, nominals)
    return query('Rec-ITU-R-P2145-0-202208_p_annual', lat, lon, ['asset'], [p_str])


def annual_surface_temperature(lat: float, lon: float, p_percent: float) -> float:
    """
    ITU-R P.2145-0.

    Annual surface temperature, Ts (K), at an exceedance probability of p_percent.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Exceedance probability (%). Must be one of: 0.01, 0.02, 0.03, 0.05, 0.1,
            0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99.

    Returns:
        Ts (float): Annual surface temperature (K), at an exceedance probability of p_percent.
    """
    nominals = (0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80,
                90, 95, 99)
    p_str = percent_to_str_v1(p_percent, nominals)
    return query('Rec-ITU-R-P2145-0-202208_t_annual', lat, lon, ['asset'], [p_str])


def annual_surface_water_vapour_density(lat: float, lon: float, p_percent: float) -> float:
    """
    ITU-R P.2145-0.

    Annual surface water vapour density, ρws (g/m3), at an exceedance probability of p_percent.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Exceedance probability (%). Must be one of: 0.01, 0.02, 0.03, 0.05, 0.1,
            0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99.

    Returns:
        ρws (float): Annual surface water vapour density (g/m3), at an exceedance
            probability of p_percent.
    """
    nominals = (0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80,
                90, 95, 99)
    p_str = percent_to_str_v1(p_percent, nominals)
    return query('Rec-ITU-R-P2145-0-202208_rho_annual', lat, lon, ['asset'], [p_str])


def annual_integrated_water_vapour_content(lat: float, lon: float, p_percent: float) -> float:
    """
    ITU-R P.2145-0.

    Annual integrated water vapour content, Vs (kg/m2), at an exceedance probability of p_percent.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Exceedance probability (%). Must be one of: 0.01, 0.02, 0.03, 0.05, 0.1,
            0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99.

    Returns:
        Vs (float): Annual integrated water vapour content (kg/m2), at an exceedance probability of
            p_percent.
    """
    nominals = (0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80,
                90, 95, 99)
    p_str = percent_to_str_v1(p_percent, nominals)
    return query('Rec-ITU-R-P2145-0-202208_v_annual', lat, lon, ['asset'], [p_str])


def annual_surface_total_pressure_stats(lat: float, lon: float, param: ModelParam) -> float:
    """
    ITU-R P.2145-0.

    Mean and standard deviation annual surface total (barometric) pressure, P̅s and σPs (hPa).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ModelParam): One of MEAN or STD_DEV.

    Returns:
        float: Mean or standard deviation annual surface total (barometric) pressure (hPa).
    """
    mapping = {ModelParam.MEAN: 'mean', ModelParam.STD_DEV: 'std'}
    asset_str = mapping[param]
    return query('Rec-ITU-R-P2145-0-202208_p_annual_statistics', lat, lon, ['asset'], [asset_str])


def annual_surface_temperature_stats(lat: float, lon: float, param: ModelParam) -> float:
    """
    ITU-R P.2145-0.

    Mean and standard deviation annual surface temperature, T̅s and σTs (K).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ModelParam): One of MEAN or STD_DEV.

    Returns:
        float: Mean or standard deviation annual surface temperature (K).
    """
    mapping = {ModelParam.MEAN: 'mean', ModelParam.STD_DEV: 'std'}
    asset_str = mapping[param]
    return query('Rec-ITU-R-P2145-0-202208_t_annual_statistics', lat, lon, ['asset'], [asset_str])


def annual_surface_water_vapour_density_stats(lat: float, lon: float, param: ModelParam) -> float:
    """
    ITU-R P.2145-0.

    Mean and standard deviation annual surface water vapour density, ρ̅ws and σρws (g/m3).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ModelParam): One of MEAN or STD_DEV.

    Returns:
        float: Mean or standard deviation annual surface water vapour density (g/m3).
    """
    mapping = {ModelParam.MEAN: 'mean', ModelParam.STD_DEV: 'std'}
    asset_str = mapping[param]
    return query('Rec-ITU-R-P2145-0-202208_rho_annual_statistics', lat, lon, ['asset'], [asset_str])


def annual_integrated_water_vapour_content_stats(lat: float, lon: float, param: ModelParam
                                                 ) -> float:
    """
    ITU-R P.2145-0.

    Mean and standard deviation annual integrated water vapour content, V̅s and σVs (kg/m2).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ModelParam): One of MEAN or STD_DEV.

    Returns:
        float: Mean or standard deviation annual integrated water vapour content (kg/m2).
    """
    mapping = {ModelParam.MEAN: 'mean', ModelParam.STD_DEV: 'std'}
    asset_str = mapping[param]
    return query('Rec-ITU-R-P2145-0-202208_v_annual_statistics', lat, lon, ['asset'], [asset_str])


def annual_surface_total_pressure_scale_height(lat: float, lon: float) -> float:
    """
    ITU-R P.2145-0.
    
    Annual surface total (barometric) pressure scale height, psch.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        psch (float): Annual surface total (barometric) pressure scale height.
    """
    return query('Rec-ITU-R-P2145-0-202208_p_annual_psch', lat, lon)


def annual_surface_temperature_scale_height(lat: float, lon: float) -> float:
    """
    ITU-R P.2145-0.
    
    Annual surface temperature scale height, tsch.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        tsch (float): Annual surface temperature scale height.
    """
    return query('Rec-ITU-R-P2145-0-202208_t_annual_tsch', lat, lon)


def annual_water_vapour_scale_height(lat: float, lon: float) -> float:
    """
    ITU-R P.2145-0.
    
    Annual surface water vapour density and integrated water vapour content scale heights, vsch.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        vsch (float): Annual surface water vapour density and integrated water vapour content scale
            heights.
    """
    return query('Rec-ITU-R-P2145-0-202208_rho_annual_vsch', lat, lon)


def monthly_surface_total_pressure(lat: float, lon: float, p_percent: float, month: int) -> float:
    """
    ITU-R P.2145-0.

    Monthly surface total (barometric) pressure, Ps (hPa), at an exceedance probability of
    p_percent.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Exceedance probability (%). Must be one of: 0.1, 0.2, 0.3, 0.5, 1, 2, 3,
            5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        Ps (float): Monthly surface total (barometric) pressure (hPa), at an exceedance probability
            of p_percent.
    """
    nominals = (0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80,
                90, 95, 99)
    p_str = percent_to_str_v1(p_percent, nominals)
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P2145-0-202208_p_monthly', lat, lon, ['asset', 'month'],
                 [p_str, month_str])


def monthly_surface_temperature(lat: float, lon: float, p_percent: float, month: int) -> float:
    """
    ITU-R P.2145-0.

    Monthly surface temperature, Ts (K), at an exceedance probability of p_percent.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Exceedance probability (%). Must be one of: 0.1, 0.2, 0.3, 0.5, 1, 2, 3,
            5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        Ts (float): Monthly surface temperature (K), at an exceedance probability of p_percent.
    """
    nominals = (0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99)
    p_str = percent_to_str_v1(p_percent, nominals)
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P2145-0-202208_t_monthly', lat, lon, ['asset', 'month'],
                 [p_str, month_str])


def monthly_surface_water_vapour_density(lat: float, lon: float, p_percent: float, month: int
                                         ) -> float:
    """
    ITU-R P.2145-0.

    Monthly surface water vapour density, ρws (g/m3), at an exceedance probability of p_percent.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Exceedance probability (%). Must be one of: 0.1, 0.2, 0.3, 0.5, 1, 2, 3,
            5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        ρws (float): Monthly surface water vapour density (g/m3), at an exceedance
            probability of p_percent.
    """
    nominals = (0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99)
    p_str = percent_to_str_v1(p_percent, nominals)
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P2145-0-202208_rho_monthly', lat, lon, ['asset', 'month'],
                 [p_str, month_str])


def monthly_integrated_water_vapour_content(lat: float, lon: float, p_percent: float, month: int
                                            ) -> float:
    """
    ITU-R P.2145-0.

    Monthly integrated water vapour content, Vs (kg/m2), at an exceedance probability of p_percent.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Exceedance probability (%). Must be one of: 0.1, 0.2, 0.3, 0.5, 1, 2, 3,
            5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        Vs (float): Monthly integrated water vapour content (kg/m2), at an exceedance probability of
            p_percent.
    """
    nominals = (0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99)
    p_str = percent_to_str_v1(p_percent, nominals)
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P2145-0-202208_v_monthly', lat, lon, ['asset', 'month'],
                 [p_str, month_str])


def monthly_surface_total_pressure_stats(lat: float, lon: float, param: ModelParam, month: int
                                         ) -> float:
    """
    ITU-R P.2145-0.

    Mean and standard deviation monthly surface total (barometric) pressure, P̅s and σPs (hPa).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ModelParam): One of MEAN or STD_DEV.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        float: Mean or standard deviation monthly surface total (barometric) pressure (hPa).
    """
    mapping = {ModelParam.MEAN: 'mean', ModelParam.STD_DEV: 'std'}
    asset_str = mapping[param]
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P2145-0-202208_p_monthly_statistics', lat, lon, ['asset', 'month'],
                 [asset_str, month_str])


def monthly_surface_temperature_stats(lat: float, lon: float, param: ModelParam, month: int
                                      ) -> float:
    """
    ITU-R P.2145-0.

    Mean and standard deviation monthly surface temperature, T̅s and σTs (K).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ModelParam): One of MEAN or STD_DEV.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        float: Mean or standard deviation monthly surface temperature (K).
    """
    mapping = {ModelParam.MEAN: 'mean', ModelParam.STD_DEV: 'std'}
    asset_str = mapping[param]
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P2145-0-202208_t_monthly_statistics', lat, lon, ['asset', 'month'],
                 [asset_str, month_str])


def monthly_surface_water_vapour_density_stats(lat: float, lon: float, param: ModelParam,
                                               month: int) -> float:
    """
    ITU-R P.2145-0.

    Mean and standard deviation monthly surface water vapour density, ρ̅ws and σρws (g/m3).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ModelParam): One of MEAN or STD_DEV.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        float: Mean or standard deviation monthly surface water vapour density (g/m3).
    """
    mapping = {ModelParam.MEAN: 'mean', ModelParam.STD_DEV: 'std'}
    asset_str = mapping[param]
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P2145-0-202208_rho_monthly_statistics', lat, lon, ['asset', 'month'],
                 [asset_str, month_str])


def monthly_integrated_water_vapour_content_stats(lat: float, lon: float, param: ModelParam,
                                                  month: int) -> float:
    """
    ITU-R P.2145-0.

    Mean and standard deviation monthly integrated water vapour content, V̅s and σVs (kg/m2).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (ModelParam): One of MEAN or STD_DEV.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        float: Mean or standard deviation monthly integrated water vapour content (kg/m2).
    """
    mapping = {ModelParam.MEAN: 'mean', ModelParam.STD_DEV: 'std'}
    asset_str = mapping[param]
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P2145-0-202208_v_monthly_statistics', lat, lon, ['asset', 'month'],
                 [asset_str, month_str])


def monthly_surface_total_pressure_scale_height(lat: float, lon: float, month: int) -> float:
    """
    ITU-R P.2145-0.
    
    Monthly surface total (barometric) pressure scale height, psch.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        psch (float): Monthly surface total (barometric) pressure scale height.
    """
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P2145-0-202208_psch_monthly', lat, lon, ['month'], [month_str])


def monthly_surface_temperature_scale_height(lat: float, lon: float, month: int) -> float:
    """
    ITU-R P.2145-0.
    
    Monthly surface temperature scale height, tsch.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        tsch (float): Monthly surface temperature scale height.
    """
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P2145-0-202208_tsch_monthly', lat, lon, ['month'], [month_str])


def monthly_water_vapour_scale_height(lat: float, lon: float, month: int) -> float:
    """
    ITU-R P.2145-0.
    
    Monthly surface water vapour density and integrated water vapour content scale heights, vsch.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        vsch (float): Monthly surface water vapour density and integrated water vapour content
            scale heights.
    """
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P2145-0-202208_vsch_monthly', lat, lon, ['month'], [month_str])


def surface_height(lat: float, lon: float) -> float:
    """
    ITU-R P.2145-0.

    Surface height above mean sea level, Zground (m).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        Zground (float): Surface height (m amsl).
    """
    return query('Rec-ITU-R-P2145-0-202208_z_ground', lat, lon) *1000 # km to m


def weibull_scale_parameter(lat: float, lon: float) -> float:
    """
    ITU-R P.2145-0.
    
    Scale parameter, λVs, of the Weibull probability distribution of integrated water vapour
    content.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        λVs (float): Scale parameter of the Weibull probability distribution of integrated water
            vapour content.
    """
    return query('Rec-ITU-R-P2145-0-202208_weibull_lambda', lat, lon)


def weibull_shape_parameter(lat: float, lon: float) -> float:
    """
    ITU-R P.2145-0.
    
    Shape parameter, kVs, of the Weibull probability distribution of integrated water vapour
    content.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        kVs (float): Shape parameter of the Weibull probability distribution of integrated water
            vapour content.
    """
    return query('Rec-ITU-R-P2145-0-202208_weibull_k', lat, lon)
