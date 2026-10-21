# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.678-3
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.678-3-201507
"""

from ._interpolation_service import query


__all__ = ['climatic_ratio']


def climatic_ratio(lat: float, lon: float) -> float:
    """
    ITU-R P.678-3, Annex 2.

    Climatic ratio, derived from 50 years of Global Precipitation Climatology Centre (GPCC) data
    over land and from 34 years of Global Precipitation Climatology Project (GPCP) data over the
    ocean.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        rc (float): Climatic ratio.
    """
    return query('Rec-ITU-R-P678-3-201507_climatic_ratio', lat, lon)
