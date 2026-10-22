# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.453-14
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.453-14-201908
"""

from enum import Enum
from ._interpolation_service import query, int_month_to_str, percent_to_str_v1, percent_to_str_v2


__all__ = ['SModelParam',
           'EModelParam',
           'annual_surface_refractivity_wet_term',
           'monthly_surface_refractivity_wet_term',
           'annual_refractivity_gradient_1km',
           'monthly_refractivity_gradient_1km',
           'annual_refractivity_gradient_65m',
           'monthly_refractivity_gradient_65m',
           'percentage_annual_time_beta',
           'percentage_monthly_time_beta',
           'surface_ducts_avg_annual_stats',
           'elevated_ducts_avg_year_stats',
           'land_sea_mask']


class SModelParam(Enum):
    """To use as input for surface_ducts_avg_annual_stats()."""
    OCCURRENCE = 1
    STRENGTH   = 2
    THICKNESS  = 3


class EModelParam(Enum):
    """To use as input for elevated_ducts_avg_year_stats()."""
    OCCURRENCE = 1
    STRENGTH   = 2
    THICKNESS  = 3
    BASE       = 4
    MAX        = 5


def annual_surface_refractivity_wet_term(lat: float, lon: float, p_percent: float) -> float:
    """
    ITU-R P.453-14, Annex 1, Section 2.2.

    Annual value of the wet term of the surface refractivity, Nwet (ppm), exceeded for p_percent of
    an average year.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Time percentage (%) of an average year. Must be one of: 0.1, 0.2, 0.3,
            0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99.

    Returns:
        Nwet (float): Annual value of the wet term of the surface refractivity (ppm), exceeded for
            p_percent of an average year.
    """
    nominals = (0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99)
    p_str = percent_to_str_v1(p_percent, nominals)
    return query('Rec-ITU-R-P453-14-201908_nwet_annual', lat, lon, ['asset'], [p_str])


def monthly_surface_refractivity_wet_term(lat: float, lon: float, p_percent: float, month: int
                                          ) -> float:
    """
     ITU-R P.453-14, Annex 1, Section 2.2.

    Monthly value of the wet term of the surface refractivity, Nwet (ppm), exceeded for p_percent
    of an average month.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Time percentage (%) of an average year. Must be one of: 0.1, 0.2, 0.3,
            0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        Nwet (float): Monthly value of the wet term of the surface refractivity (ppm), exceeded for
            p_percent of an average month.
    """
    nominals = (0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 60, 70, 80, 90, 95, 99)
    p_str = percent_to_str_v1(p_percent, nominals)
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P453-14-201908_nwet_monthly', lat, lon, ['asset', 'month'],
                 [p_str, month_str])


def annual_refractivity_gradient_1km(lat: float, lon: float, p_percent: float) -> float:
    """
    ITU-R P.453-14, Annex 1, Section 3.1.

    Value of the annual mean decrease (i.e., lapse) in radio refractivity over a 1 km layer from
    the surface, ΔN_1km, exceeded for p_percent of an average year (N-units/km).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Time percentage (%) of an average year. Must be one of: 0.1, 0.2, 0.5,
            1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 99.5, 99.8, 99.9.

    Returns:
        ΔN_1km (float): Value of the annual mean decrease (i.e., lapse) in radio refractivity over
            a 1 km layer from the surface, exceeded for p_percent of an average year (N-units/km).
    """
    nominals = (0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 99.5, 99.8,
                99.9)
    p_str = percent_to_str_v2(p_percent, nominals)
    return query('Rec-ITU-R-P453-14-201908_delta_n1km_annual', lat, lon, ['asset'], [p_str])


def monthly_refractivity_gradient_1km(lat: float, lon: float, p_percent: float, month: int
                                      ) -> float:
    """
    ITU-R P.453-14, Annex 1, Section 3.1.

    Value of the monthly mean decrease (i.e., lapse) in radio refractivity over a 1 km layer from
    the surface, ΔN_1km, exceeded for p_percent of an average month (N-units/km).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Time percentage (%) of an average year. Must be one of: 0.1, 0.2, 0.5,
            1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 99.5, 99.8, 99.9.

    Returns:
        ΔN_1km (float): Value of the monthly mean decrease (i.e., lapse) in radio refractivity over
            a 1 km layer from the surface, exceeded for p_percent of an average month (N-units/km).
    """
    nominals = (0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 99.5, 99.8,
                99.9)
    p_str = percent_to_str_v2(p_percent, nominals)
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P453-14-201908_delta_n1km_monthly', lat, lon, ['asset', 'month'],
                 [p_str, month_str])


def annual_refractivity_gradient_65m(lat: float, lon: float, p_percent: float) -> float:
    """
    ITU-R P.453-14, Annex 1, Section 3.2.

    Annual value of the refractivity gradient in the lowest 65 m from the surface of the Earth,
    ΔN_65m, not exceeded for p_percent of an average year (N-units/km).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Time percentage (%) of an average year. Must be one of: 0.1, 0.2, 0.5,
            1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 99.5, 99.8, 99.9.

    Returns:
        ΔN_65m (float): Annual value of the refractivity gradient in the lowest 65 m from the
            surface of the Earth, not exceeded for p_percent of an average year (N-units/km).
    """
    nominals = (0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 99.5, 99.8,
                99.9)
    p_str = percent_to_str_v2(p_percent, nominals)
    return query('Rec-ITU-R-P453-14-201908_delta_n65m_anual', lat, lon, ['asset'], [p_str])


def monthly_refractivity_gradient_65m(lat: float, lon: float, p_percent: float, month: int
                                      ) -> float:
    """
    ITU-R P.453-14, Annex 1, Section 3.2.

    Monthly value of the refractivity gradient in the lowest 65 m from the surface of the Earth,
    ΔN_65m, not exceeded for p_percent of an average month (N-units/km).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        p_percent (float): Time percentage (%) of an average year. Must be one of: 0.1, 0.2, 0.5,
            1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 99.5, 99.8, 99.9.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        ΔN_65m (float): Monthly value of the refractivity gradient in the lowest 65 m from the
            surface of the Earth, not exceeded for p_percent of an average month (N-units/km).
    """
    nominals = (0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 99.5, 99.8,
                99.9)
    p_str = percent_to_str_v2(p_percent, nominals)
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P453-14-201908_delta_n65m_monthly', lat, lon, ['asset', 'month'],
                 [p_str, month_str])


def percentage_annual_time_beta(lat: float, lon: float) -> float:
    """
    ITU-R P.453-14, Annex 1, Section 3.2.

    The percentage of annual time, β, for which refractivity gradient, ΔN over 100 m is lower than
    -100 N-unit/km, (%).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        β (float): The percentage of annual time for which refractivity gradient, ΔN over 100 m is
            lower than -100 N-unit/km, (%).
    """
    return query('Rec-ITU-R-P453-14-201908_beta_annual', lat, lon)


def percentage_monthly_time_beta(lat: float, lon: float, month: int) -> float:
    """
    ITU-R P.453-14, Annex 1, Section 3.2.

    The percentage of monthly time, β, for which refractivity gradient, ΔN over 100 m is lower than
    -100 N-unit/km, (%).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        β (float): The percentage of monthly time for which refractivity gradient, ΔN over 100 m is
            lower than -100 N-unit/km, (%).
    """
    month_str = int_month_to_str(month)
    return query('Rec-ITU-R-P453-14-201908_beta_monthly', lat, lon, ['month'], [month_str])


def surface_ducts_avg_annual_stats(lat: float, lon: float, param: SModelParam) -> float:
    """
    ITU-R P.453-14, Annex 1, Section 5.

    Average annual statistics of surface ducts in terms of probability of occurrence Sp (%), mean
    strength Ss (M-units), and mean thickness St (m).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (SModelParam): OCCURRENCE, STRENGTH or THICKNESS.

    Returns:
        float: One of the following: probability of occurrence Sp (%), mean strength Ss (M-units),
            or mean thickness St (m).
    """
    mapping = {
        SModelParam.STRENGTH: 'strength',
        SModelParam.THICKNESS: 'thickness',
        SModelParam.OCCURRENCE: 'occurrence'
    }
    asset_str = mapping[param]
    return query('Rec-ITU-R-P453-14-201908_surface_duct', lat, lon, ['asset'], [asset_str])


def elevated_ducts_avg_year_stats(lat: float, lon: float, param: EModelParam) -> float:
    """
    ITU-R P.453-14, Annex 1, Section 5.

    Average year statistics of elevated ducts in terms of probability of occurrence Ep (%), mean
    strength Es (M-units), mean thickness Et (m), mean base height of the duct Eb (m), mean coupling
    height Em (m).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        param (EModelParam): OCCURRENCE, STRENGTH, THICKNESS, BASE or MAX.

    Returns:
        float: One of the following: probability of occurrence Ep (%), mean strength Es (M-units),
            mean thickness Et (m), mean base height of the duct Eb (m), mean coupling height Em
            (m).
    """
    mapping = {
        EModelParam.BASE: 'base',
        EModelParam.MAX: 'max',
        EModelParam.STRENGTH: 'strength',
        EModelParam.THICKNESS: 'thickness',
        EModelParam.OCCURRENCE: 'occurrence'
    }
    asset_str = mapping[param]
    return query('Rec-ITU-R-P453-14-201908_elevated_duct', lat, lon, ['asset'], [asset_str])


def land_sea_mask(lat: float, lon: float) -> int:
    """
    Land-sea mask, where 0 denotes sea and 1 denotes land.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        int: Land-sea mask, where 0 denotes sea and 1 denotes land.
    """
    return round(query('Rec-ITU-R-P453-14-201908_land_mask', lat, lon))
