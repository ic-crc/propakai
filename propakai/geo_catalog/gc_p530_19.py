# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.530-19
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.530-19-202509
"""

from ._interpolation_service import query


__all__ = ['avg_worst_month_refractivity_gradient_75m',
           'log10_geoclimatic_factor']


def avg_worst_month_refractivity_gradient_75m(lat: float, lon: float) -> float:
    """
    ITU-R P.530-18, Annex 1, Sections 1.1 and 2.3.1.
    
    Empirical prediction of 0.1% of the average worst month refractivity increase, dN75, with
    height over the lowest 75 m of the atmosphere (N-units).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        dN75 (float): Empirical prediction of 0.1% of the average worst month refractivity increase,
            with height over the lowest 75 m of the atmosphere (N-units).
    """
    return query('Rec-ITU-R-P530-19-202509_dn75', lat, lon)


def log10_geoclimatic_factor(lat: float, lon: float) -> float:
    """
    ITU-R P.530-18, Annex 1, Sections 1.1 and 2.3.1.

    Estimate of the logarithm base 10 of the geoclimatic factor K for the average worst month.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        logK (float): Estimate of the logarithm base 10 of the geoclimatic factor K for the average
            worst month.
    """
    return query('Rec-ITU-R-P530-19-202509_logk', lat, lon)
