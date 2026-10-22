# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.2148-0
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.2148-0-202208
"""

from ._interpolation_service import query, percent_to_str_v1


__all__ = ['average_annual_wind_speed']


def average_annual_wind_speed(lat: float, lon: float, p_percent: float) -> float:
    """
    ITU-R P.2148-0, Annex 1.

    Average annual wind speed, W (m/s), at a height of 10 m above the surface of the Earth exceeded
    for p_percent of an average year.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Percentage of time of an average year (%). Must be one of: 0.01, 0.02,
            0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95 and 99.

    Returns:
        W (float): Average annual wind speed (m/s), at a height of 10 m above the surface of the
            Earth exceeded for p_percent of an average year.
    """
    nominals = (0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80,
                90, 95, 99)
    p_str = percent_to_str_v1(p_percent, nominals)
    return query('Rec-ITU-R-P2148-0-202208_wind_speed', lat, lon, ['asset'], [p_str])
