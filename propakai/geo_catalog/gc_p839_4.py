# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.839-4
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.839-4-201309
"""

from ._interpolation_service import query


__all__ = ['mean_annual_rain_height']


def mean_annual_rain_height(lat: float, lon: float) -> float:
    """
    ITU-R P.839-4.

    Mean annual rain height, hR (km above mean sea level).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        hR (float): Mean annual rain height (km above mean sea level).
    """
    return query('Rec-ITU-R-P839-4-201309_rain_height', lat, lon)
