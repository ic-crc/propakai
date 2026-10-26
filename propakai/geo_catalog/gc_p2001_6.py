# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the ITU-R Geospatial Catalog for the ITU-R P.2001-6
recommendation.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/rec-itu-r-p.2001-6-202509
"""

from ._interpolation_service import query, percent_to_str_v3


__all__ = ['median_avg_refractivity_gradient_1km',
           'supslope_avg_refractivity_gradient_1km',
           'subslope_avg_refractivity_gradient_1km',
           'refractivity_gradient_65m',
           'probability_of_rain_6h',
           'annual_rainfall_accumulation',
           'beta_rain_ratio',
           'mean_annual_0c_isotherm_height',
           'surface_water_vapour_density',
           'sporadic_e_critical_frequency',
           'climatic_zone']


def median_avg_refractivity_gradient_1km(lat: float, lon: float) -> float:
    """
    ITU-R P.2001-6, Annex, Section 2.4 & Section 3.4.1.

    Median value of average refractivity gradient, Nd1km50 (DN_Median) in the lowest 1 km of the
    atmosphere (N-units).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        Nd1km50 (float): Median value of average refractivity gradient in the lowest 1 km of the
            atmosphere (N-units).
    """
    return query('Rec-ITU-R-P2001-6-202509_dn_median', lat, lon) *-1 # to get negative value


def supslope_avg_refractivity_gradient_1km(lat: float, lon: float) -> float:
    """
    ITU-R P.2001-6, Annex, Section 2.4 & Section 3.4.1.

    Parameter S∆Nsup (DN_SupSlope) gives the change in refractivity, in N-units, from the surface
    to 1 km above the surface of the Earth, not exceeded for p less than 50% of an average year.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        S∆Nsup (float): Change in refractivity, in N-units, from the surface to 1 km above the
            surface of the Earth, not exceeded for p less than 50% of an average year.
    """
    return query('Rec-ITU-R-P2001-6-202509_dn_supslope', lat, lon)


def subslope_avg_refractivity_gradient_1km(lat: float, lon: float) -> float:
    """
    ITU-R P.2001-6, Annex, Section 2.4 & Section 3.4.1.

    Parameter S∆Nsub (DN_SubSlope) gives the change in refractivity, in N-units, from the surface
    to 1 km above the surface of the Earth, not exceeded for p greater than or equal to 50% of an
    average year.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        S∆Nsub (float): Change in refractivity, in N-units, from the surface to 1 km above the
            surface of the Earth, not exceeded for p greater than or equal to 50% of an average
            year.
    """
    return query('Rec-ITU-R-P2001-6-202509_dn_subslope', lat, lon)


def refractivity_gradient_65m(lat: float, lon: float) -> float:
    """
    ITU-R P.2001-6, Annex, Section 2.4 & Section 3.4.2.

    The refractivity gradient in the lowest 65 m of the atmosphere Nd65m1 (dndz_01) not exceeded
    for 1% of an average year (N-units).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        Nd65m1 (float): Refractivity gradient in the lowest 65 m of the atmosphere, not exceeded
            for 1% of an average year (N-units).
    """
    return query('Rec-ITU-R-P2001-6-202509_dndz_01', lat, lon)


def probability_of_rain_6h(lat: float, lon: float) -> float:
    """
    ITU-R P.2001-6, Annex, Section 2.4 & Attachment C.

    Probability of rain in 6-hours slots, Pr6 (Esarain_Pr6).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        Pr6 (float): Probability of rain in 6-hours slots.

    Bug:
        As of Sept. 2026, there is a known bug in the ITU-R Geospatial Catalog API:
        `Esarain_Pr6` returns the value of `Esarain_Beta` and vice-versa.
        Be aware that this wrapper passes through the API response without correction.
    """
    return query('Rec-ITU-R-P2001-6-202509_esarain_pr6', lat, lon)


def annual_rainfall_accumulation(lat: float, lon: float) -> float:
    """
    ITU-R P.2001-6, Annex, Section 2.4 & Attachment C.

    Annual rainfall accumulation, MT (Esarain_Mt), in mm.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        MT (float): Annual rainfall accumulation (mm).
    """
    return query('Rec-ITU-R-P2001-6-202509_esarain_mt', lat, lon)


def beta_rain_ratio(lat: float, lon: float) -> float:
    """
    ITU-R P.2001-6, Annex, Section 2.4 & Attachment C.

    Ratio between convective and total precipitation, βrain (Esarain_Beta).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        βrain (float): Ratio between convective and total precipitation.
    
    Bug:
        As of Sept. 2026, there is a known bug in the ITU-R Geospatial Catalog API:
        `Esarain_Beta` returns the value of `Esarain_Pr6` and vice-versa.
        Be aware that this wrapper passes through the API response without correction.
    """
    return query('Rec-ITU-R-P2001-6-202509_esarain_beta', lat, lon)


def mean_annual_0c_isotherm_height(lat: float, lon: float) -> float:
    """
    ITU-R P.2001-6, Annex, Section 2.4 & Attachment C.
    
    Mean 0°C isotherm rain height, h0, in km above mean sea level.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        h0 (float): Mean 0°C isotherm rain height (km amsl).
    """
    return query('Rec-ITU-R-P2001-6-202509_h0', lat, lon)


def surface_water_vapour_density(lat: float, lon: float) -> float:
    """
    ITU-R P.2001-6, Annex, Section 2.4 & Attachment F.

    Surface water-vapour density, ρsur (Surfwv_50_fixed), in g/m3 under non-rain conditions.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        ρsur (float): Surface water-vapour density (g/m3), under non-rain conditions.
    """
    return query('Rec-ITU-R-P2001-6-202509_psur', lat, lon)


def sporadic_e_critical_frequency(lat: float, lon: float, p_percent: float) -> float:
    """
    ITU-R P.2001-6, Annex, Section 2.4 & Attachment G.

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
    nominals = (0.1, 1, 10, 50)
    p_str = percent_to_str_v3(p_percent, nominals)
    return query('Rec-ITU-R-P2001-6-202509_foes', lat, lon, ['asset'], [p_str])


def climatic_zone(lat: float, lon: float) -> int:
    """
    ITU-R P.2001-6, Annex, Section 2.4 & Attachment E.

    Climatic zone identfiers required for the troposcatter model. Integer 0 represents a sea
    location for which a special procedure is required.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        int: Climatic zone identifier, in the range 0 to 6.
    """
    return round(query('Rec-ITU-R-P2001-6-202509_tropoclim', lat, lon))
