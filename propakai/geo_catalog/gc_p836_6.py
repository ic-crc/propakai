# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.836-6
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.836-6-201712
"""

from ._interpolation_service import query, percent_to_str_v1, int_month_to_str


__all__ = ['annual_water_vapour_scale_height',
           'monthly_water_vapour_scale_height',
           'annual_surface_water_vapour_density',
           'monthly_surface_water_vapour_density',
           'annual_total_columnar_water_vapour_content',
           'monthly_total_columnar_water_vapour_content',
           'topographic_altitude']


def annual_water_vapour_scale_height(lat: float, lon: float, p_percent: float) -> float:
    """
    ITU-R P.836-6, Annex 1.

    Annual water vapour scale height, vsch, in km, exceeded for p_percent of an average year.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Time percentage (%) of an average year. Must be one of: 0.1, 0.2, 0.3,
            0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99.

    Returns:
        vsch (float): Annual water vapour scale height (km), exceeded for p_percent of an average
            year.
    """
    nominals = [0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99]
    p_str = percent_to_str_v1(p_percent, nominals)
    return query('Rec-ITU-R-P836-6-201712_tcwc_annual_vsch', lat, lon, ['asset'], [p_str])


def monthly_water_vapour_scale_height(lat: float, lon: float, p_percent: float, month: int
                                      ) -> float:
    """
    ITU-R P.836-6, Annex 1.

    Monthly water vapour scale height, vsch, in km, exceeded for p_percent of an average month.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Time percentage (%) of an average month. Must be one of: 1, 2, 3, 5, 10,
            20, 30, 50, 60, 70, 80, 90, 95, 99.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        vsch (float): Monthly water vapour scale height (km), exceeded for p_percent of an average
            month.
    """
    nominals = [1.0, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99]
    p_str = percent_to_str_v1(p_percent, nominals)
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P836-6-201712_tcwc_monthly_vsch', lat, lon, ['asset', 'month'],
                 [p_str, month_str])


def annual_surface_water_vapour_density(lat: float, lon: float, p_percent: float) -> float:
    """
    ITU-R P.836-6, Annex 1.

    Annual values of surface water vapour density, rho, in g/m3, exceeded for p_percent of an
    average year.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Time percentage (%) of an average year. Must be one of: 0.1, 0.2, 0.3,
            0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99.

    Returns:
        rho (float): Annual values of surface water vapour density (g/m3), exceeded for p_percent
            of an average year.
    """
    nominals = [0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99]
    p_str = percent_to_str_v1(p_percent, nominals)
    return query('Rec-ITU-R-P836-6-201712_swvd_annual', lat, lon, ['asset'], [p_str])


def monthly_surface_water_vapour_density(lat: float, lon: float, p_percent: float, month: int
                                         ) -> float:
    """
    ITU-R P.836-6, Annex 1.

    Monthly values of surface water vapour density, rho, in g/m3, exceeded for p_percent of an
    average month.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Time percentage (%) of an average month. Must be one of: 1, 2, 3, 5, 10,
            20, 30, 50, 60, 70, 80, 90, 95, 99.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        rho (float): Monthly values of surface water vapour density (g/m3), exceeded for p_percent
            of an average month.
    """
    nominals = [1.0, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99]
    p_str = percent_to_str_v1(p_percent, nominals)
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P836-6-201712_swvd_monthly', lat, lon, ['asset', 'month'],
                 [p_str, month_str])


def annual_total_columnar_water_vapour_content(lat: float, lon: float, p_percent: float) -> float:
    """
    ITU-R P.836-6, Annex 2.

    Annual total columnar water vapour content, V, in kg/m2, exceeded for p_percent of the year.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Time percentage (%) of an average year. Must be one of: 0.1, 0.2, 0.3,
            0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99.

    Returns:
        V (float): Annual total columnar water vapour content (kg/m2), exceeded for p_percent of
            the year.
    """
    nominals = [0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99]
    p_str = percent_to_str_v1(p_percent, nominals)
    return query('Rec-ITU-R-P836-6-201712_tcwc_annual_v', lat, lon, ['asset'], [p_str])


def monthly_total_columnar_water_vapour_content(lat: float, lon: float, p_percent: float, month: int
                                         ) -> float:
    """
    ITU-R P.836-6, Annex 2.

    Monthly total columnar water vapour content, V, in kg/m2, exceeded for p_percent of an average
    month.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Time percentage (%) of an average month. Must be one of: 1, 2, 3, 5, 10,
            20, 30, 50, 60, 70, 80, 90, 95, 99.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        V (float): Monthly total columnar water vapour content (kg/m2), exceeded for p_percent of
            an average month.
    """
    nominals = [1.0, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99]
    p_str = percent_to_str_v1(p_percent, nominals)
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P836-6-201712_swvd_monthly', lat, lon, ['asset', 'month'],
                 [p_str, month_str])


def topographic_altitude(lat: float, lon: float) -> float:
    """
    ITU-R P.836-6, Annex 1 and 2.

    Topographic altitude (km).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        alt (float): Topographic altitude (km).
    """
    return query('Rec-ITU-R-P836-6-201712_topo', lat, lon)
