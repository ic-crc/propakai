# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.1511-3
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.1511-3-202408
"""

from ._interpolation_service import query


__all__ = ['topographic_height',
           'geoid_undulation']


def topographic_height(lat: float, lon: float) -> float:
    """
    ITU-R P.1511-3, Annex 1, Section 1.1.

    Topographic height of the surface of the Earth above mean sea level (m).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        float: The topographic height of the surface of the Earth above mean sea level (m).
    """
    return query('Rec-ITU-R-P1511-3-202408_topo', lat, lon)


def geoid_undulation(lat: float, lon: float) -> float:
    """
    ITU-R P.1511-3, Annex 1, Section 1.1.

    Geoid undulation (m), that is, the height difference between the WGS 84 geoid and the
    WGS 84 ellipsoid.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        h_EGM2008 (float): The Geoid undulation (m), that is, the height difference between the
            WGS 84 geoid and the WGS 84 ellipsoid.
    """
    return query('Rec-ITU-R-P1511-3-202408_egm', lat, lon)
