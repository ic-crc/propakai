# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.837-8
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.837-8-202509
"""

from ._interpolation_service import query, int_month_to_str


__all__ = ['annual_rainfall_rate_001',
           'total_monthly_mean_rainfall']


def annual_rainfall_rate_001(lat: float, lon: float) -> float:
    """
    ITU-R P.837-8, Annex 1.

    Annual rainfall rate exceeded for 0.01% of an average year, R0_01 (mm/hr).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        R0_01 (float): Annual rainfall rate exceeded for 0.01% of an average year (mm/hr).
    """
    return query('Rec-ITU-R-P837-8-202509_rainfall_annual', lat, lon)


def total_monthly_mean_rainfall(lat: float, lon: float, month: int) -> float:
    """
    ITU-R P.837-8, Annex 1.

    Total monthly mean rainfall, MT (mm).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        MT (float): Total monthly mean rainfall (mm).
    """
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P837-8-202509_rainfall_monthly', lat, lon, ['month'], [month_str])
