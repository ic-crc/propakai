# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.617-6
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.617-6-202509
"""

from ._interpolation_service import query


__all__ = ['avg_refractivity_gradient_1km',
           'avg_sea_level_surface_refractivity']


def avg_refractivity_gradient_1km(lat: float, lon: float) -> float:
    """
    ITU-R P.617-6, Annex 1, Section 2.

    "Average" annual value of gradient of the radio refractivity, ΔN (N-units/km), in the lowest
    1000 m of the atmosphere.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        ΔN (float): "Average" annual value of gradient of the radio refractivity (N-units/km), in
            the lowest 1000 m of the atmosphere.
    """
    return query('Rec-ITU-R-P617-6-202509_delta_n', lat, lon)


def avg_sea_level_surface_refractivity(lat: float, lon: float) -> float:
    """
    ITU-R P.617-6, Annex 1, Section 2.

    "Average" sea level value of the surface refractivity, N0 (N-units).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        N0 (float): "Average" sea level value of the surface refractivity, N0 (N-units).
    """
    return query('Rec-ITU-R-P617-6-202509_n_0', lat, lon)
