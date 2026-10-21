# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.1853-2
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.1853-2-201908
"""

from ._interpolation_service import query


__all__ = ['annual_mean_surface_pressure',
           'annual_mean_surface_water_vapour_density']


def annual_mean_surface_pressure(lat: float, lon: float) -> float:
    """
    ITU-R P.1853-2, Annex 1, Section 2.1.

    Annual mean surface pressure, Pannual (hPa).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        Pannual (float): Annual mean surface pressure (hPa).
    """
    return query('Rec-ITU-R-P1853-2-201908_annual_surface_pressure', lat, lon)


def annual_mean_surface_water_vapour_density(lat: float, lon: float) -> float:
    """
    ITU-R P.1853-2, Annex 1, Section 2.1.

    Annual mean surface water vapour density data, WVannual (g/m3).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        WVannual (float): Annual mean surface water vapour density data (g/m3).
    """
    return query('Rec-ITU-R-P1853-2-201908_annual_mean_surface_water_vapour_density', lat, lon)
