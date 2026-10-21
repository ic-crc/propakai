# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.835-7
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.835-7-202408

WARNING:
    The interpolation service for this recommendation does not appear to be functional (last
    check: 2026-04-22).
"""

from ._interpolation_service import query, int_month_to_str


__all__ = ['annual_geometric_altitude',
           'monthly_geometric_altitude',
           'mean_annual_temperature',
           'mean_monthly_temperature',
           'mean_annual_total_pressure',
           'mean_monthly_total_pressure',
           'mean_annual_water_vapour_density',
           'mean_monthly_water_vapour_density']


def annual_geometric_altitude(lat: float, lon: float, altitude_level: int) -> float:
    """
    ITU-R P.835-7, Annex 3.

    Vertical profile of annual geometric altitude above mean sea level, Z (km).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        altitude_level (float): Altitude level abobe means sea level, with
            1 <= altitude_level <= 138.

    Returns:
        Z (float): Annual geometric altitude (km amsl).
    """
    asset_str = str(altitude_level).zfill(3)
    return query('Rec-ITU-R-P835-7-202408_z_annual', lat, lon, ['asset'], [asset_str])


def monthly_geometric_altitude(lat: float, lon: float, altitude_level: int, month: int) -> float:
    """
    ITU-R P.835-7, Annex 3.

    Vertical profile of monthly geometric altitude above mean sea level, Z (km).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        altitude_level (float): Altitude level abobe means sea level, with
            1 <= altitude_level <= 138.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        Z (float): Monthly geometric altitude (km amsl).
    """
    asset_str = str(altitude_level).zfill(3)
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P835-7-202408_z_monthly', lat, lon, ['asset', 'month'],
                 [asset_str, month_str])


def mean_annual_temperature(lat: float, lon: float, altitude_level: int) -> float:
    """
    ITU-R P.835-7, Annex 3.

    Vertical profile of mean annual temperature, T (K).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        altitude_level (float): Altitude level abobe means sea level, with
            1 <= altitude_level <= 138.

    Returns:
        T (float): Mean annual temperature (K).
    """
    asset_str = str(altitude_level).zfill(3)
    return query('Rec-ITU-R-P835-7-202408_t_annual', lat, lon, ['asset'], [asset_str])


def mean_monthly_temperature(lat: float, lon: float, altitude_level: int, month: int) -> float:
    """
    ITU-R P.835-7, Annex 3.

    Vertical profile of mean monthly temperature, T (K).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        altitude_level (float): Altitude level abobe means sea level, with
            1 <= altitude_level <= 138.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        T (float): Mean monthly temperature (K).
    """
    asset_str = str(altitude_level).zfill(3)
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P835-7-202408_t_monthly', lat, lon, ['asset', 'month'],
                 [asset_str, month_str])


def mean_annual_total_pressure(lat: float, lon: float, altitude_level: int) -> float:
    """
    ITU-R P.835-7, Annex 3.

    Vertical profile of mean annual total (barometric) pressure, P (hPa).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        altitude_level (float): Altitude level abobe means sea level, with
            1 <= altitude_level <= 138.

    Returns:
        P (float): Mean annual total (barometric) pressure (hPa).
    """
    asset_str = str(altitude_level).zfill(3)
    return query('Rec-ITU-R-P835-7-202408_p_annual', lat, lon, ['asset'], [asset_str])


def mean_monthly_total_pressure(lat: float, lon: float, altitude_level: int, month: int) -> float:
    """
    ITU-R P.835-7, Annex 3.

    Vertical profile of mean monthly total (barometric) pressure, P (hPa).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        altitude_level (float): Altitude level abobe means sea level, with
            1 <= altitude_level <= 138.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        P (float): Mean monthly total (barometric) pressure, P (hPa).
    """
    asset_str = str(altitude_level).zfill(3)
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P835-7-202408_p_monthly', lat, lon, ['asset', 'month'],
                 [asset_str, month_str])


def mean_annual_water_vapour_density(lat: float, lon: float, altitude_level: int) -> float:
    """
    ITU-R P.835-7, Annex 3.

    Vertical profile of mean annual water vapour density, WV (g/m3).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        altitude_level (float): Altitude level abobe means sea level, with
            1 <= altitude_level <= 138.

    Returns:
        WV (float): Mean annual water vapour density (g/m3).
    """
    asset_str = str(altitude_level).zfill(3)
    return query('Rec-ITU-R-P835-7-202408_wv_annual', lat, lon, ['asset'], [asset_str])


def mean_monthly_water_vapour_density(lat: float, lon: float, altitude_level: int, month: int
                                      ) -> float:
    """
    ITU-R P.835-7, Annex 3.

    Vertical profile of mean monthly water vapour density, WV (g/m3).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        altitude_level (float): Altitude level abobe means sea level, with
            1 <= altitude_level <= 138.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        WV (float): Mean monthly water vapour density (g/m3).
    """
    asset_str = str(altitude_level).zfill(3)
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P835-7-202408_wv_monthly', lat, lon, ['asset', 'month'],
                 [asset_str, month_str])
