# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.1546-6
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.1546-6-201908
"""

from ._interpolation_service import query, percent_to_str_v3


__all__ = ['radio_refractivity_gradient']


def radio_refractivity_gradient(lat: float, lon: float, p_percent: float) -> float:
    """
    ITU-R P.1546-6, Annex 7.

    Radio refractivity gradient, dN, exceeded for p_percent of time of an average year
    (N-units/km).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Percentage of time of an average year (%). Must be one of: 1, 10, 50.

    Returns:
        dN (float): Radio refractivity gradient, exceeded for p_percent of time of an average year
            (N-units/km).
    """
    nominals = [1, 10, 50]
    p_str = percent_to_str_v3(p_percent, nominals)
    return query('Rec-ITU-R-P1546-6-201908_dn', lat, lon, ['asset'], [p_str])
