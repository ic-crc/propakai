# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.534-6
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.534-6-202109
"""

from ._interpolation_service import query, percent_to_str_v3


__all__ = ['sporadic_e_critical_frequency']


def sporadic_e_critical_frequency(lat: float, lon: float, p_percent: float) -> float:
    """
    ITU-R P.534-6.

    Sporadic E critical frequency, foEs (MHz), exceeded for average annual time percentage of
    p_percent.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Average annual time percentage (%). Must be one of: 0.1, 1, 10, 50.

    Returns:
        foEs (float): Sporadic E critical frequency (MHz), exceeded for average annual time
            percentage of p_percent.
    """
    nominals = [0.1, 1, 10, 50]
    p_str = percent_to_str_v3(p_percent, nominals)
    return query('Rec-ITU-R-P534-6-202109_foes', lat, lon, ['asset'], [p_str])
