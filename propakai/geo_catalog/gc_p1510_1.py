# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.1510-1
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.1510-1-201706
"""

from ._interpolation_service import query, int_month_to_str


__all__ = ['annual_mean_surface_temperature',
           'monthly_mean_surface_temperature']


def annual_mean_surface_temperature(lat: float, lon: float) -> float:
    """
    ITU-R P.1510-1, Annex 1, Section 1.

    Annual mean surface temperature at 2 m above the surface of the Earth (K).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        TAnnual (float): Annual mean surface temperature at 2 m above the surface of the Earth (K).
    """
    return query('Rec-ITU-R-P1510-1-201706_annual', lat, lon)


def monthly_mean_surface_temperature(lat: float, lon: float, month: int) -> float:
    """
    ITU-R P.1510-1, Annex 1, Section 1.

    Monthly mean surface temperature at 2 m above the surface of the Earth (K).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        Tii (float): Monthly mean surface temperature at 2 m above the surface of the Earth (K).
    """
    return query('Rec-ITU-R-P1510-1-201706_monthly', lat, lon, ['month'], [int_month_to_str(month)])
