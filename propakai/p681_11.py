# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.681-11.

P.681 : Propagation data required for the design systems in the land mobile-satellite service.

https://www.itu.int/rec/R-REC-P.681/en
"""

from math import log as ln, exp, sqrt, sin, radians, cos, tan, atan, degrees, erf
from enum import Enum
import warnings


__all__ = ['ShadowingLevel',
           'roadside_trees_shadowing_fade',
           'roadside_trees_shadowing_fade_ex',
           'non_gso_roadside_trees_shadowing_unavail',
           'fade_duration_distribution',
           'non_fade_duration_distribution',
           'building_blockage_probability',
           'street_canyon_masking_function',
           'single_wall_masking_function',
           'street_crossing_masking_function',
           't_junction_masking_function',
           'mountainous_multipath_fading_distribution',
           'roadside_trees_multipath_fading_distribution',
           'shadowing_cross_correlation_coefficient',
           'availability_improbability']


class ShadowingLevel(Enum):
    """
    MODERATE: percentage of optical shadowing between 55% and 75%
    EXTREME: percentage of optical shadowing between 75% and 90%
    """
    MODERATE = 1
    EXTREME  = 2


def roadside_trees_shadowing_fade(f_ghz: float, theta_deg: float, p_percent: float) -> float:
    """
    ITU-R P.681-5, Annex 1, Section 4.1.1.

    Estimates fade du to roadside tree-shadowing (dB).

    "The predicted fade distributions apply for highways and rural roads where the overall aspect
    of the propagation path is, for the most part, orthogonal to the lines of roadside trees and
    utility poles and it is assumed that the dominant cause of LMSS signal fading is tree canopy
    shadowing".

    Args:
        f_ghz (float): Frequency (GHz), with 0.8 <= f_ghz <= 20.
        theta_deg (float): Path elevation angle to the satellite (degrees),
            with 7 <= theta_deg <= 60.
        p_percent (float): Percentage of distance travelled over which fade is exceeded (%),
            with 1 <= p_percent <= 80.

    Returns:
        A (float): Fade exceeded for the specified percentage of distance travelled (dB).
    """
    # Step 4
    theta_deg = max(theta_deg, 20)

    # Step 1
    def _AL_func(p_percent: float, theta_deg: float) -> float:
        """Valid for f_ghz = 1.5, 1 <= p_percent <= 20 and 20 <= theta_deg <= 60."""
        M = 3.44 + 0.0975*theta_deg - 0.002*theta_deg*theta_deg
        N = -0.443*theta_deg + 34.76
        AL = -M*ln(p_percent) + N
        return AL

    # Step 2
    def _A20_func(p_percent: float, theta_deg: float, f_ghz: float) -> float:
        """Valid for 0.8 <= f_ghz <= 20 and 1 <= p_percent <= 20."""
        AL = _AL_func(p_percent, theta_deg)
        A20 = AL*exp(1.5*((1/sqrt(1.5))-(1/sqrt(f_ghz))))
        return A20

    # Step 3
    if p_percent > 20:
        A = _A20_func(20, theta_deg, f_ghz)*(1/ln(4))*ln(80/p_percent)
    else:
        A = _A20_func(p_percent, theta_deg, f_ghz)

    return A


def roadside_trees_shadowing_fade_ex(f_ghz: float, theta_deg: float, p_percent: int) -> float:
    """
    ITU-R P.681-5, Annex 1, Section 4.1.1.1.

    Extension of the roadside trees model for elevation angles greater than 60 degrees at
    frequencies of 1.6 GHz and 2.6 GHz.

    Args:
        f_ghz (float): Frequency (GHz), with f_ghz = 1.6 or f_ghz = 2.6.
        theta_deg (float): Path elevation angle to the satellite (degrees),
            with 60 <= theta_deg <= 90.
        p_percent (int): Percentage of distance travelled over which fade is exceeded (%).
            p_percent must be set to one of: 1, 5, 10, 15, 20 or 30.

    Returns:
        A (float): Fade exceeded for the specified percentage of distance travelled (dB).
    """
    nominal_freqs_ghz = [1.6, 2.6]
    if f_ghz not in nominal_freqs_ghz:
        freqs_str = ', '.join(map(str, nominal_freqs_ghz))
        raise ValueError(f'f_ghz must be set to one of: {freqs_str}.')

    if theta_deg < 60 or theta_deg > 90:
        raise ValueError('theta_deg must be between 60 and 90.')

    nominal_percents = [1, 5, 10, 15, 20, 30]
    if p_percent not in nominal_percents:
        percents_str = ', '.join(map(str, nominal_percents))
        raise ValueError(f'p_percent must be set to one of: {percents_str}.')

    A60 = roadside_trees_shadowing_fade(f_ghz, 60, p_percent)

    if f_ghz == 1.6:
        nominal_fades = {1: 4.1, 5: 2.0, 10: 1.5, 15: 1.4, 20: 1.3, 30: 1.2}
    else:
        nominal_fades = {1: 9.0, 5: 5.2, 10: 3.8, 15: 3.2, 20: 2.8, 30: 2.5}

    A80 = nominal_fades[p_percent]
    if theta_deg <= 80:
        A = (A60*(80-theta_deg) + A80*(theta_deg-60))/(80-60)
    else:
        A = (A80*(90-theta_deg))/(90-80)

    return A


def non_gso_roadside_trees_shadowing_unavail(f_ghz: float, theta_list_deg: list[float],
                                             time_list_percent: list[float],
                                             gm_list_dbi: list[float],
                                             a_db: float) -> float:
    """
    ITU-R P.681-5, Annex 1, Section 4.1.1.2.

    Estimates the percentage of unavailability due to roadside trees shadowing for non-
    geostationary (non-GSO) and mobile-satellite systems.

    Args:
        f_ghz (float): Frequency (GHz), with 0.8 <= f_ghz <= 20.
        theta_list_deg (list[float]): List of path elevation angles under which the terminal will
            see the satellite (degrees), with 7 <= theta_list_deg[i] <= 60 for any i.
        time_list_percent (list[float]): For each elevation angle in theta_list_deg, the percentage
            of time (%) for which the terminal will see the satellite at that angle, with
            0 <= time_list_percent[i] <= 100 for any i.
        gm_list_dbi (list[float]): For each elevation angle in theta_list_deg, the mobile terminal's
            antenna gain (dBi) at the corresponding elevation angle.
        a_db (float): Fade margin (dB).

    Returns:
        p_unavail (float): The total system unavailability (%), from 0 to 100.
    """
    total_unavailability_percent = 0
    for theta_deg, time_percent, gm_dbi in zip(theta_list_deg, time_list_percent, gm_list_dbi):
        dist_travelled_percent = _roadside_trees_shadowing_fade_inv(f_ghz=f_ghz,
                                                                    theta_deg=theta_deg,
                                                                    a_db=a_db+gm_dbi)
        total_unavailability_percent += time_percent * dist_travelled_percent / 100.0
    return total_unavailability_percent


def _roadside_trees_shadowing_fade_inv(f_ghz: float, theta_deg: float, a_db: float) -> float:
    """
    ITU-R P.681-5, Annex 1, Section 4.1.1.2.

    See roadside tree-shadowing from Section 4.1.1.

    Args:
        f_ghz (float): Frequency (GHz), with 0.8 <= f_ghz <= 20.
        theta_deg (float): Path elevation angle to the satellite (degrees),
            with 7 <= theta_deg <= 60.
        a_db (float): Fade exceeded for the returned percentage of distance travelled (dB).

    Returns:
        p (float): Percentage of distance travelled over which the specified fade is exceeded (%).
            Returned value will be between 1 and 80.
    """
    min_p = 1
    max_p = 80
    mid_p = (max_p + min_p)/2.0
    while True:
        temp_a_db = roadside_trees_shadowing_fade(f_ghz=f_ghz, theta_deg=theta_deg, p_percent=mid_p)
        if temp_a_db < a_db:
            max_p = mid_p
        else:
            min_p = mid_p
        temp_mid_p = (max_p + min_p)/2.0
        if abs(mid_p-temp_mid_p) < 1E-4: # arbitrary value
            break
        mid_p = temp_mid_p
    if abs(a_db-temp_a_db) > 0.01: # arbitrary value, accept max diff of 0.01 dB
        raise ValueError('Cannot calculate result. a_db and/or other input parameters may be '\
                          'outside the validity range of the model.')
    return mid_p


def fade_duration_distribution(dd_m: float) -> float:
    """
    ITU-R P.681-5, Annex 1, Section 4.1.2.

    Estimates the probability that the distance fade duration exceeds the distance dd (m), under
    the condition that the attenuation exceeds 5 dB.

    The model "is based on measurements at an elevation angle of 51 degrees and is applicable for
    [roads that exhibit] moderate to severe shadowing (percentage of optical shadowing between 55%
    and 90%)".

    Args:
        dd_m (float): Distance fade duration (meters), with 0.02 <= dd_m.

    Returns:
        p (float): Probability (%) that the distance fade duration exceeds the distance dd_m, under
            the condition that the attenuation exceeds 5 dB. Returned value will be between 0 and
            100.
    """
    alpha = 0.22
    sigma = 1.215
    P = 0.5*(1-erf((ln(dd_m)-ln(alpha))/(sqrt(2)*sigma)))
    return P*100


def non_fade_duration_distribution(dd_m: float, sl: ShadowingLevel) -> float:
    """
    ITU-R P.681-5, Annex 1, Section 4.1.3.

    Estimates the probability that a continuous non-fade distance duration exceeds the distance dd
    (m), given that the fade is smaller than a 5 dB threshold.

    The model "is based on measurements at an elevation angle of 51 degrees and is applicable for
    [roads that exhibit] moderate to severe shadowing (percentage of optical shadowing between 55%
    and 90%)".

    Args:
        dd_m (float): Distance fade duration (meters).
        sl (ShadowingLevel): One of MODERATE (percentage of optical shadowing between 55% and 75%)
            or EXTREME (percentage of optical shadowing between 75% and 90%).

    Returns:
        p (float): Probability that a continuous non-fade distance duration exceeds the distance dd
            (m), given that the fade is smaller than a 5 dB threshold. Returned value will be
            between 0 and 100.
    """
    if sl == ShadowingLevel.MODERATE:
        beta = 20.54
        gamma = 0.58
    elif sl == ShadowingLevel.EXTREME:
        beta = 11.71
        gamma = 0.8371
    else:
        raise ValueError('Unsupported value for parameter sl (shadowing level).')
    p = beta*pow(dd_m, -gamma)
    p = min(p, 100) # NOTE: not in the rec., avoid exceeding 100%
    return p # already a percentage, do not multipy by 100


def building_blockage_probability(f_ghz: float, cf: float, theta_deg: float, hm_m: float,
                                  dm_m: float, hb_m: float, phi_deg: float) -> float:
    """
    ITU-R P.681-11, Annex 1, Section 4.2.

    Estimates the percentage probability of blockage due to the buildings (%).

    Args:
        f_ghz (float): Frequency (GHz), with f_ghz from about 0.8 to 20.
        cf (float): Required clearance as a fraction of the first Fresnel zone.
        theta_deg (float): Elevation angle of the ray to the satellite above horizontal (degrees),
            with 0 < theta_deg < 90.
        hm_m (float): Height of mobile above ground (meters).
        dm_m (float): Distance of the mobile from the front of the buildings (meters).
        hb_m (float): The most common (modal) building heigh (meters).
        phi_deg (float): Azimuth angle of the ray relative to street direction (degrees),
            with 0 < phi_deg < 180.

    Returns:
        p (float): Percentage probability of blockage due to the buildings (%).
    """
    sin_phi = sin(radians(phi_deg))
    cos_theta = cos(radians(theta_deg))
    dr_m = dm_m/(sin_phi/cos_theta)
    lambda_m = 1.0E-9*2.998E8/f_ghz
    h2_m = cf*sqrt(lambda_m*dr_m)
    tan_theta = tan(radians(theta_deg))
    h1_m = hm_m + (dm_m*tan_theta/sin_phi)
    p = 100*exp(-(h1_m-h2_m)**2/(2*hb_m*hb_m))
    return p


def _SA(h_m: float, w_m: float, phi_deg: float) -> float:
    """
    ITU-R P.681-11, Annex 1, Section 4.4.

    Equations (11a), (11b). See FIGURES 5 & 6.
    
    Args:
        h_m (float): Average building height (meters).
        w_m (float): Street width (meters).
        phi_deg (float): Street orientation with respect to the link (degrees),
            with 0 <= phi_deg <= 90.

    Returns:
        theta (float): Elevation angle (degrees) at which the frontier between link (non-shaded
            areas) and no-link (shaded areas) occurs.
    """
    if phi_deg == 90:
        theta_rad = atan(h_m/(w_m/2))
    elif phi_deg == 0:
        theta_rad = 0
    else:
        tan_phi = tan(radians(phi_deg))
        theta_rad = atan(h_m/sqrt((w_m*w_m/4)*((1/(tan_phi*tan_phi))+1)))
    theta_deg = degrees(theta_rad)
    return theta_deg


def _SB(h_m: float, w1_m: float, w2_m: float, phi_deg: float) -> float:
    """
    ITU-R P.681-11, Annex 1, Section 4.4.

    Equations (11c), (11d), (11e). See FIGURES 5 & 6.
    
    Args:
        h_m (float): Average building height (meters).
        w1_m (float): Width of first street (meters).
        w2_m (float): Width of second street (meters).
        phi_deg (float): Street orientation with respect to the link (degrees),
            with 0 <= phi_deg <= 90.

    Returns:
        theta (float): Elevation angle (degrees) at which the frontier between link (non-shaded
            areas) and no-link (shaded areas) occurs.
    """
    if radians(phi_deg) > atan(w1_m/w2_m):
        phi_deg = 90-phi_deg
    return _SA(h_m, w1_m, phi_deg)


def street_canyon_masking_function(theta_deg: float, h_m: float, w_m: float, phi_deg: float
                                   ) -> bool:
    """
    ITU-R P.681-11, Annex 1, Section 4.4.

    Estimates whether a link can be completed for the street canyon scenario.

    Args:
        theta_deg (float): Path elevation angle, with 0 <= theta_deg <= 90.
        h_m (float): Average building height (meters).
        w_m (float): Street width (meters).
        phi_deg (float): Street orientation with respect to the link (degrees),
            with -180 <= phi_deg <= 180.
    
    Returns:
        bool: True when a link can be completed (non-shaded), False otherwise (shaded areas).
    """
    # have phi_deg in the -180 to 180 range
    while phi_deg > 180:
        phi_deg -= 360
    while phi_deg < -180:
        phi_deg += 360

    phi_deg = abs(phi_deg)
    if phi_deg > 90:
        phi_deg = 180 - phi_deg
    if theta_deg > _SA(h_m, w_m, phi_deg):
        return True
    return False


def single_wall_masking_function(theta_deg: float, h_m: float, w_m: float, phi_deg: float) -> bool:
    """
    ITU-R P.681-11, Annex 1, Section 4.4.

    Estimates whether a link can be completed for the single wall scenario.

    Args:
        theta_deg (float): Path elevation angle, with 0 <= theta_deg <= 90.
        h_m (float): Average building height (meters).
        w_m (float): Street width (meters).
        phi_deg (float): Street orientation with respect to the link (degrees),
            with -180 <= phi_deg <= 180.
    
    Returns:
        bool: True when a link can be completed (non-shaded), False otherwise (shaded areas).
    """
    # have phi_deg in the -180 to 180 range
    while phi_deg > 180:
        phi_deg -= 360
    while phi_deg < -180:
        phi_deg += 360

    if phi_deg >= 0:
        return True

    phi_deg = abs(phi_deg)
    if phi_deg > 90:
        phi_deg = 180 - phi_deg
    if theta_deg > _SA(h_m, w_m, phi_deg):
        return True
    return False


def street_crossing_masking_function(theta_deg: float, h_m: float, w1_m: float, w2_m: float,
                                     phi_deg: float) -> bool:
    """
    ITU-R P.681-11, Annex 1, Section 4.4.

    Estimates whether a link can be completed for the street crossing scenario.

    Args:
        theta_deg (float): Path elevation angle, with 0 <= theta_deg <= 90.
        h_m (float): Average building height (meters).
        w1_m (float): Width of first street (meters).
        w2_m (float): Width of second street (meters).
        phi_deg (float): Street orientation with respect to the link (degrees),
            with -180 <= phi_deg <= 180.
    
    Returns:
        bool: True when a link can be completed (non-shaded), False otherwise (shaded areas).
    """
    # have phi_deg in the -180 to 180 range
    while phi_deg > 180:
        phi_deg -= 360
    while phi_deg < -180:
        phi_deg += 360

    phi_deg = abs(phi_deg)
    if phi_deg > 90:
        phi_deg = 180 - phi_deg
    if theta_deg > _SB(h_m, w1_m, w2_m, phi_deg):
        return True
    return False


def t_junction_masking_function(theta_deg: float, h_m: float, w1_m: float, w2_m: float,
                                phi_deg: float) -> bool:
    """
    ITU-R P.681-11, Annex 1, Section 4.4.

    Estimates whether a link can be completed for the T-junction scenario.

    Args:
        theta_deg (float): Path elevation angle, with 0 <= theta_deg <= 90.
        h_m (float): Average building height (meters).
        w1_m (float): Width of first street (meters).
        w2_m (float): Width of second street (meters).
        phi_deg (float): Street orientation with respect to the link (degrees),
            with -180 <= phi_deg <= 180.
    
    Returns:
        bool: True when a link can be completed (non-shaded), False otherwise (shaded areas).
    """
    # have phi_deg in the -180 to 180 range
    while phi_deg > 180:
        phi_deg -= 360
    while phi_deg < -180:
        phi_deg += 360

    if phi_deg >= 0:
        if phi_deg > 90:
            phi_deg = 180 - phi_deg
        if theta_deg > _SB(h_m, w1_m, w2_m, phi_deg):
            return True
        return False
    else:
        phi_deg = abs(phi_deg)
        if phi_deg > 90:
            phi_deg = 180 - phi_deg
        if theta_deg > _SA(h_m, w1_m, phi_deg):
            return True
        return False


def mountainous_multipath_fading_distribution(f_ghz: float, theta_deg: float, a_db: float,
                                              warnings_on: bool=True) -> float:
    """
    ITU-R P.681-11, Annex 1, Section 5.1.

    Distribution of fade depths due to multipath in mountainous terrain. The model is valid when
    the effect of shadowing is negligible.

    Supported input values (from the recommendation's TABLE 3):

    | f_ghz  | theta_deg | a_db  |
    |--------|-----------|-------|
    | 0.87   | 30        | 2-7   |
    | 1.5    | 30        | 2-8   |
    | 0.87   | 45        | 2-4   |
    | 1.5    | 45        | 2-5   |

    Args:
        f_ghz (float): Frequency (GHz), with f_ghz = 0.87 or f_ghz = 1.5.
        theta_deg (float): Path elevation angle to the satellite (degrees),
            with theta_deg = 30 or theta_deg = 45.
        a_db (float): Fade exceeded (dB). See table above for ranges of valid values.
        warnings_on (bool, optional): Indicates whether to raise a warning when a_db is out of
            validity range. Default value is True.

    Returns:
        p (float): Percentage of distance over which the fade is exceeded (%), from 1 to 10.
    """
    if f_ghz == 0.87 and theta_deg == 30:
        a = 34.52
        b = 1.855
        if warnings_on and (a_db < 2 or a_db > 7):
            warnings.warn("a_db is outside its validity range of 2-7.", UserWarning)
    elif f_ghz == 1.5 and theta_deg == 30:
        a = 33.19
        b = 1.710
        if warnings_on and (a_db < 2 or a_db > 8):
            warnings.warn("a_db is outside its validity range of 2-8.", UserWarning)
    elif f_ghz == 0.87 and theta_deg == 45:
        a = 31.64
        b = 2.464
        if warnings_on and (a_db < 2 or a_db > 4):
            warnings.warn("a_db is outside its validity range of 2-4.", UserWarning)
    elif f_ghz == 1.5 and theta_deg == 45:
        a = 39.95
        b = 2.321
        if warnings_on and (a_db < 2 or a_db > 5):
            warnings.warn("a_db is outside its validity range of 2-5.", UserWarning)
    else:
        if not(f_ghz == 0.87 or f_ghz == 1.5):
            raise ValueError('f_ghz must be set to one of: 0.87, 1.5.')
        if not(theta_deg == 30 or theta_deg == 45):
            raise ValueError('theta_deg must be set to one of: 30, 45.')
        raise ValueError('Failed to compute p.')
    p = a*pow(a_db, -b)
    return p


def roadside_trees_multipath_fading_distribution(f_ghz: float, a_db: float, warnings_on: bool=True
                                                 ) -> float:
    """
    ITU-R P.681-11, Annex 1, Section 5.2.

    Distribution of fade depths due to multipath in a roadsite trees environment. The model assumes
    negligible shadowing.

    "Experiments conducted along tree-lined roads in the United States of America have shown that
    multipath fading is relatively insensitive to path elevation over the range of 30° to 60°".

    Supported input values (from the recommendation's TABLE 4):

    | f_ghz  | a_db  |
    |--------|-------|
    | 0.87   | 1-4.5 |
    | 1.5    | 1-6   |

    Args:
        f_ghz (float): Frequency (GHz), with f_ghz = 0.87 or f_ghz = 1.5.
        a_db (float): Fade exceeded (dB). See table above for ranges of valid values.
        warnings_on (bool, optional): Indicates whether to raise a warning when a_db is out of
            validity range. Default value is True.

    Returns:
        p (float): Percentage of distance over which the fade is exceeded (%), from 1 to 50.
    """
    if f_ghz == 0.87:
        u = 125.6
        v = 1.116
        if warnings_on and (a_db < 1 or a_db > 4.5):
            warnings.warn("a_db is outside its validity range of 1-4.5.", UserWarning)
    elif f_ghz == 1.5:
        u = 127.7
        v = 0.8573
        if warnings_on and (a_db < 1 or a_db > 6):
            warnings.warn("a_db is outside its validity range of 1-6.", UserWarning)
    else:
        raise ValueError('f_ghz must be set to one of: 0.87, 1.5.')
    p = u*exp(-v*a_db)
    return p


def _three_segment_model_points(theta1_deg: float, theta2_deg: float, h_m: float, w_m: float,
                                l_m: float) -> tuple[float, float, float|None, float|None]:
    """
    ITU-R P.681-11, Annex 1, Section 9.2.1.

    Args:
        theta1_deg (float): Satellite 1 elevation angle (degrees), with 0 < theta1_deg < 90.
        theta2_deg (float): Satellite 2 elevation angle (degrees), with 0 < theta2_deg < 90 and
            with theta2_deg >= theta1_deg.
        h_m (float): Average building height (meters).
        w_m (float): Average street width (meters).
        l_m (float): Length of street under consideration (meters). A large value is advised for
            this parameter, i.e. l_m >= 200.

    Returns:
        rho_A (float): Cross-correlation coefficient at point A (no units), from -1 to +1.
        rho_D (float): Cross-correlation coefficient at point D (no units), from -1 to +1.
        delta_phi_B (float or None): Azimuth spacing at point B (degrees), from 0 to 90 degrees.
        delta_phi_C (float or None): Azimuth spacing at point C (degrees), from 0 to 90 degrees.

    """
    xi1_deg = xi2_deg = M1 = M2 = None

    # Step 1
    tan_theta_1 = tan(radians(theta1_deg))
    tan_theta_2 = tan(radians(theta2_deg))
    x1_squared = ((h_m*h_m)/(tan_theta_1*tan_theta_1)) - (w_m*w_m/4)
    # NOTE: Using theta_2 instead of theta_1 for calculating x2 (likely an editing error in
    #       P.681-11).
    x2_squared = ((h_m*h_m)/(tan_theta_2*tan_theta_2)) - (w_m*w_m/4)

    if x1_squared < 0 and x2_squared < 0:
        # Step 6
        return (1, 1, None, None)

    if x1_squared >= 0:
        x1 = sqrt(x1_squared)
        x1 = min(x1, l_m/2)
        xi1_deg = round(degrees(atan((w_m/2)/x1)))
        M1 = (xi1_deg+0.5)/90

    if x2_squared >= 0:
        x2 = sqrt(x2_squared)
        x2 = min(x2, l_m/2)
        xi2_deg = round(degrees(atan((w_m/2)/x2)))
        M2 = (xi2_deg+0.5)/90

    if x1_squared >= 0 and x2_squared < 0:
        # Step 6
        assert xi1_deg is not None
        N11 = 4*xi1_deg + 2
        rho = (N11/180)-1
        return (rho, rho, None, None)

    if x1_squared < 0 and x2_squared >= 0: # should not happend unless theta2_deg < theta1_deg
        if theta2_deg < theta1_deg:
            raise ValueError('theta2_deg must be greater than or equal to theta1_deg.')
        else:
            raise RuntimeError('Cannot compute three-segment model points.')

    assert (
        xi1_deg is not None
        and xi2_deg is not None
        and M1 is not None
        and M2 is not None
    )

    # Steps 2 & 3
    rho_A = _rho_A(xi1_deg=xi1_deg, xi2_deg=xi2_deg, m1=M1, m2=M2)
    rho_D = _rho_D(xi1_deg=xi1_deg, xi2_deg=xi2_deg, m1=M1, m2=M2)

    # Step 4
    delta_phi_B = xi2_deg - xi1_deg

    # Step 5
    if (xi1_deg+xi2_deg) <= 90:
        # NOTE: using plus (+) instead of minus (-) (likely an editing error in P.681-11)
        delta_phi_C = xi1_deg + xi2_deg
    else:
        delta_phi_C = 180 - xi1_deg - xi2_deg

    return (rho_A, rho_D, delta_phi_B, delta_phi_C)


def _rho_A(xi1_deg: float, xi2_deg: float, m1: float, m2: float) -> float:
    """
    ITU-R P.681-11, Annex 1, Section 9.2.1, eq. (39), (41), (42a), (42b).
    """
    N11 = 4*xi1_deg + 2
    N00 = 360 - 4*xi2_deg - 2
    N01 = 4*(xi2_deg-xi1_deg)
    N10 = 0
    return _rho(xi1_deg=xi1_deg, xi2_deg=xi2_deg, m1=m1, m2=m2, n11=N11, n00=N00, n01=N01, n10=N10)


def _rho_D(xi1_deg: float, xi2_deg: float, m1: float, m2: float) -> float:
    """
    ITU-R P.681-11, Annex 1, Section 9.2.1, eq. (40a), (40b), (41), (42a), (42b).
    """
    if (xi1_deg+xi2_deg) <= 90:
        N11 = 0
        N00 = 360 - 4*xi1_deg - 4*xi2_deg - 4
        N01 = 4*xi2_deg + 2
        N10 = 4*xi1_deg + 2
    else:
        N11 = 4*xi1_deg + 4*xi2_deg + 4 - 360
        N00 = 0
        N01 = 360 - 4*xi1_deg - 2
        N10 = 360 - 4*xi2_deg - 2
    return _rho(xi1_deg=xi1_deg, xi2_deg=xi2_deg, m1=m1, m2=m2, n11=N11, n00=N00, n01=N01, n10=N10)


def _rho(xi1_deg: float, xi2_deg: float, m1: float, m2: float, n11: float, n00: float, n01: float,
         n10: float) -> float:
    """
    ITU-R P.681-11, Annex 1, Section 9.2.1, eq. (41), (42a), (42b).
    """
    num = n11*(1-m1)*(1-m2) + n00*(0-m1)*(0-m2) + n10*(1-m1)*(0-m2) + n01*(0-m1)*(1-m2)
    sigma_of_theta1 = sqrt(_sigma_squared(xi1_deg, m1))
    sigma_of_theta2 = sqrt(_sigma_squared(xi2_deg, m2))
    rho = num/(359*sigma_of_theta1*sigma_of_theta2)
    return rho


def _sigma_squared(xi_deg: float, m: float) -> float:
    """
    ITU-R P.681-11, Annex 1, Section 9.2.1, eq. (42a), (42b).
    """
    return ((4*xi_deg+2)*(1-m)*(1-m) + (360-4*xi_deg-2)*(0-m)*(0-m))/359


def shadowing_cross_correlation_coefficient(delta_phi_deg: float, theta1_deg: float,
                                            theta2_deg: float, h_m: float, w_m: float, l_m: float
                                            ) -> float:
    """
    ITU-R P.681-11, Annex 1, Section 9.2.1.

    Quantifies the cross-correlation coefficient between shadowing events in urban areas (using a
    "street canyon" area geometry).

    Args:
        delta_phi_deg (float): Azimuth spacing between two separate satellite-to-mobile links in
            street canyons (degrees), with -180 <= delta_phi_deg <= 180.
        theta1_deg (float): Satellite 1 elevation angle (degrees), with 0 < theta1_deg < 90.
        theta2_deg (float): Satellite 2 elevation angle (degrees), with 0 < theta2_deg < 90 and
            with theta2_deg >= theta1_deg.
        h_m (float): Average building height (meters).
        w_m (float): Average street width (meters).
        l_m (float): Length of street under consideration (meters). A large value is advised for
            this parameter, i.e. l_m >= 200.

    Returns:
        rho (float): The cross-correlation coefficient (no units).
    """
    rho_A, rho_D, delta_phi_B, delta_phi_C = _three_segment_model_points(theta1_deg, theta2_deg,
                                                                         h_m, w_m, l_m)

    # have delta_phi_deg in the -180 to 180 range
    while delta_phi_deg > 180:
        delta_phi_deg -= 360
    while delta_phi_deg < -180:
        delta_phi_deg += 360

    # apply symmetry, as "correlation values are symmetric for all four Δφ quadrants"
    delta_phi_deg = abs(delta_phi_deg)
    if delta_phi_deg > 90:
        delta_phi_deg = 180 - delta_phi_deg

    # See FIGURE 25 regarding following code

    if rho_A == rho_D:
        return rho_A

    if delta_phi_B is None or delta_phi_C is None:
        raise RuntimeError('Cannot compute cross-correlation coefficient.')

    if delta_phi_deg <= delta_phi_B:
        return rho_A
    if delta_phi_deg >= delta_phi_C:
        return rho_D

    # linear interpolation
    rho = (rho_A*(delta_phi_C-delta_phi_deg) + rho_D*(delta_phi_deg-delta_phi_B))/ \
            (delta_phi_C-delta_phi_B)

    return rho


def availability_improbability(rho: float, p1_percent: float, p2_percent: float) -> float:
    """
    ITU-R P.681-11, Annex 1, Section 9.2.1.

    Computes the overall availability improbability after satellite diversity.

    Args:
        rho (float): Cross-correlation coefficient. May be obtained from the
            shadowing_cross_correlation_coefficient() function.
        p1_percent (float): Unavailability probability for the first link (%), with 0 <= p1 <= 100.
        p2_percent (float): Unavailability probability for the second link (%), with
            0 <= p2 <= 100. For urban areas, p1 and p2 values may be computed using the
            building_blockage_probability() function.

    Returns:
        p0 (float): The overall availability improbability after satellite diversity (%). The
            probability of availability will be 100-p0.
    """
    p1 = p1_percent/100
    p2 = p2_percent/100
    p0 = rho*sqrt(p1*(1-p1))*sqrt(p1*(1-p2)) + p1*p2
    if p0 < 0:
        raise ValueError('Input values are yielding a negative probability value.')
    return p0*100
