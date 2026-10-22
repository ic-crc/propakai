# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.676-13.

P.676 : Attenuation by atmospheric gases and related effects.

https://www.itu.int/rec/R-REC-P.676/en
"""


from os.path import join
from math import cos, sin, radians, degrees, sqrt, acos, floor, ceil, log, asin, exp, e as e_const
from threading import Lock
from array import array
from filelock import FileLock
from propakai import _download_utils as _du
from propakai import p835_6
from propakai import p1144_13
from propakai import p2145_0


__all__ = ['gaseous_attenuation',
           'dry_air_gaseous_attenuation',
           'water_vapour_gaseous_attenuation',
           'terrestrial_path_gaseous_attenuation',
           'refractive_index',
           'slant_path_gaseous_attenuation',
           'space_based_station_apparent_elev_angle',
           'earth_based_station_apparent_elev_angle',
           'intercepts_earth',
           'phase_dispersion',
           'downwelling_microwave_brightness_temperature',
           'upwelling_microwave_brightness_temperature',
           'slant_path_instant_oxygen_gaseous_att',
           'slant_path_statistical_oxygen_gaseous_att',
           'slant_path_instant_water_vapour_gaseous_att_1',
           'slant_path_instant_water_vapour_gaseous_att_2',
           'slant_path_statistical_water_vapour_gaseous_att',
           'slant_path_instant_gaseous_attenuation',
           'slant_path_statistical_gaseous_attenuation',
           'weibull_approximation']


def gaseous_attenuation(f_ghz: float, p_hpa: float=1013.25, t_k: float=288.15,
                        rho_gm3: float=7.5) -> float:
    """
    ITU-R P.676-13, Annex 1, Section 1.

    Gaseous attenuation attributable to dry air and water vapour (dB/km).

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000.
        p_hpa (float, optional): Atmospheric pressure (hPa). Defaults to 1013.25.
        t_k (float, optional): Temperature (K). Defaults to 288.15.
        rho_gm3 (float, optional): Water vapour density (g/m3). Defaults to 7.5.

    Returns:
        gamma (float): Gaseous attenuation attributable to dry air and water vapour (dB/km).
    """
    gamma_o = dry_air_gaseous_attenuation(f_ghz, p_hpa, t_k, rho_gm3)
    gamma_w = water_vapour_gaseous_attenuation(f_ghz, p_hpa, t_k, rho_gm3)
    return gamma_o+gamma_w # eq. (1)


def dry_air_gaseous_attenuation(f_ghz: float, p_hpa: float=1013.25, t_k: float=288.15,
                                rho_gm3: float=7.5) -> float:
    """
    ITU-R P.676-13, Annex 1, Section 1.

    Specific gaseous attenuation attributable to dry air (dB/km).

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000.
        p_hpa (float, optional): Atmospheric pressure (hPa). Defaults to 1013.25.
        t_k (float, optional): Temperature (K). Defaults to 288.15.
        rho_gm3 (float, optional): Water vapour density (g/m3). Defaults to 7.5.

    Returns:
        gamma_o (float): Specific gaseous attenuation attributable to dry air (oxygen, pressure-
            induced nitrogen and non-resonant Debye attenuation), in dB/km.
    """
    gamma_o = 0.1820*f_ghz*_Npp_oxygen(f_ghz, p_hpa, t_k, rho_gm3) # eq. (1)
    return gamma_o


def water_vapour_gaseous_attenuation(f_ghz: float, p_hpa: float=1013.25, t_k: float=288.15,
                                     rho_gm3: float=7.5) -> float:
    """
    ITU-R P.676-13, Annex 1, Section 1.

    Specific gaseous attenuation attributable to water vapour (dB/km).

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000.
        p_hpa (float, optional): Atmospheric pressure (hPa). Defaults to 1013.25.
        t_k (float, optional): Temperature (K). Defaults to 288.15.
        rho_gm3 (float, optional): Water vapour density (g/m3). Defaults to 7.5.

    Returns:
        gamma_w (float): Specific gaseous attenuation attributable to water vapour (dB/km).
    """
    gamma_w = 0.1820*f_ghz*_Npp_water_vapour(f_ghz, p_hpa, t_k, rho_gm3) # eq. (1)
    return gamma_w


def _Npp_oxygen(f_ghz: float, p_hpa: float, t_k: float, rho_gm3: float) -> float:
    """
    ITU-R P.676-13, Annex 1, Section 1.

    N''Oxygen.

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000.
        p_hpa (float): Atmospheric pressure (hPa).
        t_k (float): Temperature (K).
        rho_gm3 (float): Water vapour density (g/m3).

    Returns:
        float: Imaginary part of the complex refractivity attributable to oxygen.
    """
    TABLE_1 = _p676_13_shared['TABLE_1']
    NUM_LINES = 44
    theta = 300.0/t_k
    e = rho_gm3*t_k/216.7
    NppO = 0.0
    prod1 = 1.0E-7*p_hpa*theta*theta*theta
    prod2 = 1.1*e*theta
    prod3 = 1.0E-4*(p_hpa+e)*pow(theta,0.8)
    for i in range(0, NUM_LINES, 1):
        fi, a1, a2, a3, a4, a5, a6 = TABLE_1[i*7 : (i*7)+7]
        Si = a1 * prod1 * exp(a2*(1.0-theta)) # eq. (3) for oxygen
        df = a3*1.0E-4*((p_hpa*pow(theta,0.8-a4))+prod2) # eq. (6a) for oxygen
        df = sqrt((df*df)+2.25E-6) # eq. (6b) for oxygen
        delta = (a5+(a6*theta))*prod3 # eq. (7) for oxygen
        # eq. (5)
        Fi = (f_ghz/fi)*( ((df-(delta*(fi-f_ghz)))/(((fi-f_ghz)*(fi-f_ghz))+(df*df))) +
                          ((df-(delta*(fi+f_ghz)))/(((fi+f_ghz)*(fi+f_ghz))+(df*df))) )
        NppO += Si*Fi # eq. (2a)
    d = 5.6E-4*(p_hpa+e)*pow(theta, 0.8) # eq. (9)
    # eq. (8)
    NppD = f_ghz*p_hpa*theta*theta*( (6.14E-5/(d*(1.0+((f_ghz*f_ghz)/(d*d))))) +
           ((1.4E-12*p_hpa*pow(theta,1.5))/(1.0+(1.9E-5*pow(f_ghz,1.5)))) )
    NppO += NppD
    return NppO


def _Npp_water_vapour(f_ghz: float, p_hpa: float, t_k: float, rho_gm3: float) -> float:
    """
    ITU-R P.676-13, Annex 1, Section 1.

    N''Water Vapour.

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000.
        p_hpa (float): Atmospheric pressure (hPa).
        t_k (float): Temperature (K).
        rho_gm3 (float): Water vapour density (g/m3).

    Returns:
        float: Imaginary part of the complex refractivity attributable to water vapour.
    """
    TABLE_2 = _p676_13_shared['TABLE_2']
    NUM_LINES = 35
    theta = 300.0/t_k
    e = rho_gm3*t_k/216.7
    NppWV = 0.0
    prod1 = 1.0E-1*e*pow(theta, 3.5)
    for i in range(0, NUM_LINES, 1):
        fi, b1, b2, b3, b4, b5, b6 = TABLE_2[i*7 : (i*7)+7]
        Si = b1 * prod1 * exp(b2*(1.0-theta)) # eq. (3) for water vapour
        df = b3*1.0E-4*((p_hpa*pow(theta,b4))+(b5*e*pow(theta,b6))) # eq.(6a) water vapour
        df = 0.535*df + sqrt((0.217*df*df)+(2.1316E-12*fi*fi/theta)) # eq. (6b) for water vapour
        # eq. (5) with delta=0 (eq.(7))
        Fi = (f_ghz/fi)*( (df/(((fi-f_ghz)*(fi-f_ghz))+(df*df))) +
                          (df/(((fi+f_ghz)*(fi+f_ghz))+(df*df))) )
        NppWV += Si*Fi
    return NppWV


def terrestrial_path_gaseous_attenuation(r0_km: float, f_ghz: float, p_hpa: float=1013.25,
                                         t_k: float=288.15, rho_gm3: float=7.5) -> float:
    """
    ITU-R P.676-13, Annex 1, Section 2.1.
    
    Path attenuation for a terrestrial path, or for slightly inclined paths close to the
    ground (dB).

    Args:
        r0_km (float): Path length (km).
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000.
        p_hpa (float, optional): Atmospheric pressure (hPa). Defaults to 1013.25.
        t_k (float, optional): Temperature (K). Defaults to 288.15.
        rho_gm3 (float, optional): Water vapour density (g/m3). Defaults to 7.5.

    Returns:
        A (float): Path attenuation for a terrestrial path, or for slightly inclined paths close to
            the ground (dB).
    """
    gamma = gaseous_attenuation(f_ghz, p_hpa, t_k, rho_gm3)
    A = r0_km*gamma
    return A


def refractive_index(h_km: float,
                     atm: p835_6.ReferenceAtmosphere=p835_6.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL,
                     rho0_gm3: float=7.5) -> float:
    """
    ITU-R P.676-13, Annex 1, Section 2.2.1.

    Calculates the atmospheric radio refractive index at any height for Earth-satellite paths.

    Args:
        h_km (float): Height in km, with h_km >= 0.
        atm (p835_6.ReferenceAtmosphere, optional): A reference atmosphere from ITU-R P.835-6.
            Default value is MEAN_ANNUAL_GLOBAL.
        rho0_gm3 (float, optional): Ground-level water vapour density (g/m3). Only applies when atm
            is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.

    Returns:
        n (float): The radio refractive index at height h_km (for Earth-satellite paths).
    """
    # Outer space conventionnally starts at 100 km above sea level.
    # See Section 2.2.3 of Annex 1 from ITU-R P.676-13.
    if h_km > 100:
        return 1

    # Extract from ITU-R P.453-14:
    # "For Earth-satellite paths, the refractive index at any height is obtained using equations
    # (1), (2) and (10) above, together with the appropriate values for the parameters given in
    # Recommendation ITU-R P.835, Annex 1."

    P = p835_6.pressure(h_km, atm) # total atmospheric pressure (hPa)
    T = p835_6.temperature(h_km, atm)
    rho = p835_6.water_vapour_density(h_km, atm, rho0_gm3)
    e = rho*T/216.7 # water vapour pressure, in hPa. eq. (10) of P.453-14
    Pd = P - e # dry atmospheric pressure (hPa).  eq. (5) of P.453-14
    N = (77.6*Pd/T) + (72*e/T) + (3.75E5*e/(T*T)) # eq. (2) of P.453-14
    n = 1 + (N*1E-6) # eq. (1) of P.453-14
    return n


def _layer_indices(h_lower: float, h_upper: float) -> tuple[int, int]:
    """ITU-R P.676-13, Section 2.2.1 of Annex 1"""
    e = e_const
    h_lower = max(0, h_lower)
    h_upper = min(100, h_upper)
    i_lower = floor(100*log(1E4*h_lower*((e**0.01)-1)+1)+1)
    i_upper = ceil(100*log(1E4*h_upper*((e**0.01)-1)+1)+1)
    return (i_lower, i_upper)


def _layer_thickness(i: int, i_lower: int, i_upper: int, h_lower: float, h_upper: float) -> float:
    """ITU-R P.676-13, Section 2.2.1 of Annex 1"""
    e = e_const
    if h_lower == 0 and h_upper > 100:
        delta_i_km =0.0001*e**((i-1)/100)
    else:
        m = ((e**0.02-e**0.01)/(e**(i_upper/100)-e**(i_lower/100)))* (h_upper-h_lower)
        delta_i_km = m*(e**((i-1)/100))
    return delta_i_km


def _layer_bottom_height(i: int, i_lower: int, i_upper: int, h_lower: float, h_upper: float
                         ) -> float:
    """ITU-R P.676-13, Section 2.2.1 of Annex 1"""
    e = e_const
    if h_lower == 0 and h_upper > 100:
        h_i_km = 0.0001*(((e**((i-1)/100))-1)/((e**0.01)-1))
    else:
        m = ((e**0.02-e**0.01)/(e**(i_upper/100)-e**(i_lower/100)))*(h_upper-h_lower)
        h_i_km = h_lower + m*(((e**((i-1)/100))-(e**((i_lower-1)/100))) / ((e**0.01)-1))
    return h_i_km


def slant_path_gaseous_attenuation(f_ghz: float, h1_km: float, h2_km: float, phi1_deg: float,
                                   atm: p835_6.ReferenceAtmosphere=
                                       p835_6.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL,
                                   rho0_gm3: float=7.5) -> tuple[float, float, float]:
    """
    ITU-R P.676-13, Annex 1, Section 2.2.

    Calculates the Earth-space slant path gaseous attenuation for an ascending path between a
    location on or near the surface of the Earth and a location above the surface of the Earth or
    in space.

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000.
        h1_km (float): Height of the first station (km), with 0 <= h1_km < h2_km.
        h2_km (float): Height of the second station (km), with 0 <= h1_km < h2_km.
        phi1_deg (float): The local apparent elevation angle at height h1_km (degrees).
            0°=horizon, +90°=zenith, -90°=nadir.
        atm (p835_6.ReferenceAtmosphere, optional): A reference atmosphere from ITU-R P.835-6.
            Default value is MEAN_ANNUAL_GLOBAL.
        rho0_gm3 (float, optional): Ground-level water vapour density (g/m3). Only applies when atm
            is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.

    Returns:
        Agas (float): The slant path gaseous attenuation (dB).
        bending (float): The total atmosphering bending along the path (radians).
        deltaL (float): The excess atmospheric path length (km).
    """
    if phi1_deg >= 0:
        return _non_neg_elev_angl_slant_path_gaseous_att(f_ghz, h1_km, h2_km, phi1_deg, atm,
                                                         rho0_gm3)
    else:
        return _neg_elev_angl_slant_path_gaseous_att(f_ghz, h1_km, h2_km, phi1_deg, atm, rho0_gm3)


def _non_neg_elev_angl_slant_path_gaseous_att(f_ghz: float, h1_km: float, h2_km: float,
                                              phi1_deg: float,
                                              atm: p835_6.ReferenceAtmosphere=
                                                  p835_6.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL,
                                              rho0_gm3: float=7.5) -> tuple[float, float, float]:
    """
    ITU-R P.676-13, Annex 1, Section 2.2.1 (Non-negative apparent elevation angles).

    Calculates the Earth-space slant path gaseous attenuation for an ascending path between a
    location on or near the surface of the Earth and a location above the surface of the Earth or
    in space.

    Args:
        f_ghz (float): Frequency in GHz, with 1 <= f_ghz <= 1000.
        h1_km (float): Height of the first station (km), with 0 <= h1_km < h2_km.
        h2_km (float): Height of the second station (km), with 0 <= h1_km < h2_km.
        phi1_deg (float): The local apparent elevation angle at height h1_km, in degrees, with
            phi1_deg >= 0°. 0°=horizon, +90°=zenith.
        atm (p835_6.ReferenceAtmosphere, optional): A reference atmosphere from ITU-R P.835-6.
            Default value is MEAN_ANNUAL_GLOBAL.
        rho0_gm3 (float, optional): Ground-level water vapour density (g/m3). Only applies when atm
            is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.

    Returns:
        Agas (float): The slant path gaseous attenuation (dB).
        bending (float): The total atmosphering bending along the path (radians).
        deltaL (float): The excess atmospheric path length (km).
    """
    Agas = 0
    bending = 0
    deltaL = 0
    Re = 6371
    r_1 = None
    n_1 = None
    beta_1_deg = 90-phi1_deg
    sin_beta_1 = sin(radians(beta_1_deg))

    h_lower = h1_km
    h_upper = h2_km
    (i_lower, i_upper) = _layer_indices(h_lower, h_upper)
    for i in range(i_lower, i_upper, 1):
        h_i_bot = _layer_bottom_height(i, i_lower, i_upper, h_lower, h_upper)
        delta_i = _layer_thickness(i, i_lower, i_upper, h_lower, h_upper)
        h_i_mid = h_i_bot+(delta_i/2)
        n_i = refractive_index(h_i_mid, atm, rho0_gm3)
        r_i = Re + h_i_bot
        if r_1 is None or n_1 is None:
            r_1 = r_i
            n_1 = n_i
        beta_i_rad = asin(((n_1*r_1)/(n_i*r_i))*sin_beta_1)
        cos_beta_i = cos(beta_i_rad)
        a_i = (-r_i*cos_beta_i)+sqrt((r_i*r_i*cos_beta_i*cos_beta_i)+(2*r_i*delta_i)+
                                     (delta_i*delta_i))
        T = p835_6.temperature(h_i_mid, atm)
        P = p835_6.pressure(h_i_mid, atm)
        rho = p835_6.water_vapour_density(h_i_mid, atm, rho0_gm3)
        e = rho*T/216.7 # water vapour pressure, in hPa
        Pdry = P - e # eq. (5) of P.453-14
        y_i = gaseous_attenuation(f_ghz=f_ghz,
                                  # examples from CG-3M3J-13-ValEx-Rev8.3.0.xlsx use dry pressure
                                  p_hpa=Pdry, t_k=T,  rho_gm3=rho)
        Agas += a_i*y_i

        # Calculation of the atmospheric bending along the path
        if i != i_upper-1:
            h_ip1_bot = h_i_bot + delta_i
            delta_ip1 = _layer_thickness(i+1, i_lower, i_upper, h_lower, h_upper)
            h_ip1_mid = h_ip1_bot+(delta_ip1/2)
            n_ip1 = refractive_index(h_ip1_mid, atm, rho0_gm3)
            r_ip1 = r_i + delta_i
            beta_ip1_rad = asin(((n_1*r_1)/(n_ip1*r_ip1))*sin_beta_1)
            alpha_i_rad = asin(((n_1*r_1)/(n_i*r_ip1))*sin_beta_1)
            bending += beta_ip1_rad-alpha_i_rad # ITU-R P.676-13, Section 2.2.4 of Annex 1

        # Calculation of the excess atmospheric path length
        deltaL += a_i*(n_i-1) # ITU-R P.676-13, Section 2.2.5 of Annex 1

    return (Agas, bending, deltaL)


def _neg_elev_angl_slant_path_gaseous_att(f_ghz: float, h1_km: float, h2_km: float,
                                          phi1_deg: float,
                                          atm: p835_6.ReferenceAtmosphere=
                                              p835_6.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL,
                                          rho0_gm3: float=7.5) -> tuple[float, float, float]:
    """
    ITU-R P.676-13, Annex 1, Section 2.2.2 (Negative apparent elevation angles).

    Calculates the Earth-space slant path gaseous attenuation for an ascending path between a
    location on or near the surface of the Earth and a location above the surface of the Earth or
    in space.

    Args:
        f_ghz (float): Frequency in GHz, with 1 <= f_ghz <= 1000.
        h1_km (float): Height of the first station (km), with 0 <= h1_km < h2_km.
        h2_km (float): Height of the second station (km), with 0 <= h1_km < h2_km.
        phi1_deg (float): The local apparent elevation angle at height h1_km, in degrees, with
            phi1_deg < 0°. 0°=horizon, -90°=nadir.
        atm (p835_6.ReferenceAtmosphere, optional): A reference atmosphere from ITU-R P.835-6.
            Default value is MEAN_ANNUAL_GLOBAL.
        rho0_gm3 (float, optional): Ground-level water vapour density (g/m3). Only applies when atm
            is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.

    Returns:
        Agas (float): The slant path gaseous attenuation (dB).
        bending (float): The total atmosphering bending along the path (radians).
        deltaL (float): The excess atmospheric path length (km).
    """
    Re = 6371
    beta_1_deg = 90-phi1_deg
    sin_beta_1 = sin(radians(beta_1_deg))
    n_h1 = refractive_index(h1_km, atm, rho0_gm3)

    hG_low = 0
    hG_high = h2_km
    hG = ((hG_high-hG_low)/2)+hG_low
    for _ in range (1, 24):
        n_hG = refractive_index(hG, atm, rho0_gm3)
        gazing_test = (n_hG*(Re+hG))-(n_h1*(Re+h1_km)*sin_beta_1)
        if gazing_test > 0:
            hG_high = hG
        else:
            hG_low = hG
        hG = ((hG_high-hG_low)/2)+hG_low

    Agas1, bending1, deltaL1 = _non_neg_elev_angl_slant_path_gaseous_att(f_ghz, hG, h1_km, 0,
                                                                         atm, rho0_gm3)
    Agas2, bending2, deltaL2 = _non_neg_elev_angl_slant_path_gaseous_att(f_ghz, hG, h2_km, 0,
                                                                         atm, rho0_gm3)
    return (Agas1+Agas2, bending1+bending2, deltaL1+deltaL2)


def space_based_station_apparent_elev_angle(he_km: float, hs_km: float, phie_deg: float,
                                            atm: p835_6.ReferenceAtmosphere=
                                                p835_6.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL,
                                            rho0_gm3: float=7.5) -> float:
    """
    ITU-R P.676-13, Annex 1, Section 2.2.3.

    Calculates the apparent elevation angle at the space-based station based on the apparent
    elevation angle at the Earth-based station.

    "The gaseous attenuation for a space-Earth path, where the apparent elevation angle at the space
    station is [phis_deg], is identical to the gaseous attenuation for the reciprocal Earth-space
    path, where the apparent elevation angle at the earth station is [phie_deg]".
    
    Args:
        he_km (float): Height of the Earth-based station (km).
        hs_km (float): Height of the space-based station (km).
        phie_deg (float): Apparent elevation angle at the Earth-based station (degrees).
            0°=horizon, +90°=zenith, -90°=nadir.
        atm (p835_6.ReferenceAtmosphere, optional): A reference atmosphere from ITU-R P.835-6.
            Default value is MEAN_ANNUAL_GLOBAL.
        rho0_gm3 (float, optional): Ground-level water vapour density (g/m3). Only applies when atm
            is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.

    Returns:
        phis_deg (float): Apparent elevation angle at the space-based station (degrees).
    """
    Re = 6371
    phie_rad = radians(phie_deg)
    rs = Re+hs_km
    ns = refractive_index(hs_km, atm, rho0_gm3)
    re = Re+he_km
    ne = refractive_index(he_km, atm, rho0_gm3)
    phis_rad = -acos(((re*ne)/(rs*ns))*cos(phie_rad))
    phis_deg = degrees(phis_rad)
    return phis_deg


def earth_based_station_apparent_elev_angle(he_km: float, hs_km: float, phis_deg: float,
                                            atm: p835_6.ReferenceAtmosphere=
                                                p835_6.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL,
                                            rho0_gm3: float=7.5) -> float:
    """
    ITU-R P.676-13, Annex 1, Section 2.2.3.

    Calculates the apparent elevation angle at the Earth-based station based on the apparent
    elevation angle at the space-based station.

    "The gaseous attenuation for a space-Earth path, where the apparent elevation angle at the space
    station is [phis_deg], is identical to the gaseous attenuation for the reciprocal Earth-space
    path, where the apparent elevation angle at the earth station is [phie_deg]".
    
    Args:
        he_km (float): Height of the Earth-based station (km).
        hs_km (float): Height of the space-based station (km).
        phis_deg (float): Apparent elevation angle at the space-based station (degrees).
            0°=horizon, +90°=zenith, -90°=nadir.
        atm (p835_6.ReferenceAtmosphere, optional): A reference atmosphere from ITU-R P.835-6.
            Default value is MEAN_ANNUAL_GLOBAL.
        rho0_gm3 (float, optional): Ground-level water vapour density (g/m3). Only applies when atm
            is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.

    Returns:
        phie_deg (float): Reciprocal apparent elevation angle at the Earth-based station (degrees).
    """
    Re = 6371
    phis_rad = radians(phis_deg)
    rs = Re+hs_km
    ns = refractive_index(hs_km, atm, rho0_gm3)
    re = Re+he_km
    ne = refractive_index(he_km, atm, rho0_gm3)
    phie_rad = acos(((rs*ns)/(re*ne))*cos(phis_rad))
    phie_deg = degrees(phie_rad)
    return phie_deg


def intercepts_earth(he_km: float, hs_km: float, phis_deg: float,
                     atm: p835_6.ReferenceAtmosphere=
                         p835_6.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL,
                     rho0_gm3: float=7.5) -> bool:
    """
    ITU-R P.676-13, Annex 1, Section 2.2.3.

    Evaluates whether a space-Earth path intercepts the Earth.

    Args:
        he_km (float): Height of the Earth-based station (km).
        hs_km (float): Height of the space-based station (km).
        phis_deg (float): Apparent elevation angle at the space-based station (degrees).
            0°=horizon, +90°=zenith, -90°=nadir.
        atm (p835_6.ReferenceAtmosphere, optional): A reference atmosphere from ITU-R P.835-6.
            Default value is MEAN_ANNUAL_GLOBAL.
        rho0_gm3 (float, optional): Ground-level water vapour density (g/m3). Only applies when atm
            is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.

    Returns:
        bool: True if the space-Earth path intercepts the Earth, False otherwise.
    """
    Re = 6371
    phi_s_rad = radians(phis_deg)
    rs = Re+hs_km
    ns = refractive_index(hs_km, atm, rho0_gm3)
    re = Re+he_km
    ne = refractive_index(he_km, atm, rho0_gm3)
    if ((rs*ns)/(re*ne))*cos(phi_s_rad) > 1:
        return False
    else:
        return True


def phase_dispersion(f_ghz: float, p_hpa: float=1013.25, t_k: float=288.15,
                     rho_gm3: float=7.5) -> float:
    """
    ITU-R P.676-13, Annex 1, Section 3.

    Calculates the gaseous phase dispersion (deg/km).

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000.
        p_hpa (float, optional): Atmospheric pressure (hPa). Defaults to 1013.25.
        t_k (float, optional): Temperature (K). Defaults to 288.15.
        rho_gm3 (float, optional): Water vapour density (g/m3). Defaults to 7.5.

    Returns:
        phi (float): The gaseous phase dispersion (deg/km).
    """
    Np_oxygen = _Np_oxygen(f_ghz, p_hpa, t_k, rho_gm3)
    Np_water_vapour = _Np_water_vapour(f_ghz, p_hpa, t_k, rho_gm3)
    phi = -1.2008*f_ghz*(Np_oxygen+Np_water_vapour) # eq. (24)
    return phi


def _Np_oxygen(f_ghz: float, p_hpa: float, t_k: float, rho_gm3: float) -> float:
    """
    ITU-R P.676-13, Annex 1, Section 3.
    
    N'Oxygen.

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000.
        p_hpa (float): Atmospheric pressure (hPa).
        t_k (float): Temperature (K).
        rho_gm3 (float): Water vapour density (g/m3).

    Returns:
        float: Real part of the complex refractivity attributable to oxygen.
    """
    TABLE_1 = _p676_13_shared['TABLE_1']
    NUM_LINES = 44
    f = f_ghz
    P = p_hpa
    theta = 300.0/t_k
    e = rho_gm3*t_k/216.7
    NpO = 0.0
    prod1 = 1.0E-7*P*theta*theta*theta
    prod2 = 1.1*e*theta
    prod3 = 1.0E-4*(P+e)*pow(theta,0.8)
    for i in range(0, NUM_LINES, 1):
        #fi = TABLE_1[i][0]
        #a = TABLE_1[i]
        fi, a1, a2, a3, a4, a5, a6 = TABLE_1[i*7 : (i*7)+7]
        Si = a1 * prod1 * exp(a2*(1.0-theta)) # eq. (3) for oxygen
        df = a3*1.0E-4*((P*pow(theta,0.8-a4))+prod2) # eq. (6a) for oxygen
        df = sqrt((df*df)+2.25E-6) # eq. (6b) for oxygen
        delta = (a5+(a6*theta))*prod3 # eq. (7) for oxygen
        # eq. (25c)
        Fpi = (f/fi)*( (((fi-f)+(delta*df))/(((fi-f)*(fi-f))+(df*df))) -
                       (((fi+f)+(delta*df))/(((fi+f)*(fi+f))+(df*df))) )
        NpO += Si*Fpi # eq. (25a)
    d = 5.6E-4*(P+e)*pow(theta, 0.8) # eq. (9)
    NpD = (-6.14E-5*P*theta*theta*f*f)/((f*f)+(d*d)) # eq. (25d)
    NpO += NpD # eq. (25a)
    return NpO


def _Np_water_vapour(f_ghz: float, p_hpa: float, t_k: float, rho_gm3: float) -> float:
    """
    ITU-R P.676-13, Annex 1, Section 3.
    
    N'Water Vapour.

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000.
        p_hpa (float): Atmospheric pressure (hPa).
        t_k (float): Temperature (K).
        rho_gm3 (float): Water vapour density (g/m3).

    Returns:
        float: Real part of the complex refractivity attributable to water vapour.
    """
    TABLE_2 = _p676_13_shared['TABLE_2']
    NUM_LINES = 35
    f = f_ghz
    theta = 300.0/t_k
    e = rho_gm3*t_k/216.7
    NpWV = 0.0
    prod1 = 1.0E-1*e*pow(theta, 3.5)
    for i in range(0, NUM_LINES, 1):
        fi, b1, b2, b3, b4, b5, b6 = TABLE_2[i*7 : (i*7)+7]
        Si = b1 * prod1 * exp(b2*(1.0-theta)) # eq. (3) for water vapour
        df = b3*1.0E-4*((p_hpa*pow(theta,b4))+(b5*e*pow(theta,b6))) # eq. (6a) water vapour
        df = 0.535*df + sqrt((0.217*df*df)+(2.1316E-12*fi*fi/theta)) # eq. (6b) for water vapour
        # eq. (25c) with delta=0 (eq. (7))
        Fpi = (f/fi)*( ((fi-f)/(((fi-f)*(fi-f))+(df*df))) - ((fi+f)/(((fi+f)*(fi+f))+(df*df))) )
        NpWV += Si*Fpi # eq. (25b)
    return NpWV


def _tb(f_ghz: float, tj: float) -> float:
    """ITU-R P.676-13, Annex 1, Sections 4."""
    TB = 0.048*f_ghz/(exp(0.048*f_ghz/tj)-1) # eq. (26)
    return TB


def downwelling_microwave_brightness_temperature(f_ghz: float, phi1_deg: float,
                                                 h1_km: float=0, hk_km=100.1,
                                                 atm: p835_6.ReferenceAtmosphere=
                                                    p835_6.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL,
                                                 rho0_gm3: float=7.5) -> float:
    """
    ITU-R P.676-13, Annex 1, Section 4.1.

    The downwelling atmospheric microwave brightness temperature (K).
    
    Args:
        f_ghz (float): Frequency in GHz, with 1 <= f_ghz <= 1000.
        phi1_deg (float): The local apparent elevation angle at height h1_km (degrees), 
            with phi1_deg >= 0. 0°=horizon, +90°=zenith.
        h1_km (float, optional): Height of atmospheric layer 1 (km). Default value is 0.
        hk_km (float, optional): Height of atmospheric layer k (km). Default value is 100.1.
        atm (p835_6.ReferenceAtmosphere, optional): A reference atmosphere from ITU-R P.835-6.
            Default value is MEAN_ANNUAL_GLOBAL.
        rho0_gm3 (float, optional): Ground-level water vapour density (g/m3). Only applies when atm
            is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.

    Returns:
        TB_downwelling (float): The downwelling atmospheric microwave brightness temperature (K).
    """
    Re = 6371
    r_1 = None
    n_1 = None
    beta_1_deg = 90-phi1_deg
    sin_beta_1 = sin(radians(beta_1_deg))

    # step 1
    TB_dw = _tb(f_ghz, 2.73)

    h_lower = h1_km
    h_upper = hk_km
    (i_lower, i_upper) = _layer_indices(h_lower, h_upper)
    for i in range(i_lower, i_upper, 1):
        j = i_upper-i

        # step 2
        TB_dw_last = TB_dw

        # step 3
        h_j_bot = _layer_bottom_height(j, i_lower, i_upper, h_lower, h_upper)
        delta_j = _layer_thickness(j, i_lower, i_upper, h_lower, h_upper)
        h_j_mid = h_j_bot+(delta_j/2)
        Tj = p835_6.temperature(h_j_mid, atm)
        TB = _tb(f_ghz, Tj)

        # step 4
        n_j = refractive_index(h_j_mid, atm, rho0_gm3)
        r_j = Re + h_j_bot
        if r_1 is None or n_1 is None:
            r_1 = r_j
            n_1 = n_j
        beta_j_rad = asin(((n_1*r_1)/(n_j*r_j))*sin_beta_1)
        cos_beta_j = cos(beta_j_rad)
        a_j = (-r_j*cos_beta_j)+sqrt((r_j*r_j*cos_beta_j*cos_beta_j)+(2*r_j*delta_j)+
                                     (delta_j*delta_j))
        P = p835_6.pressure(h_j_mid, atm)
        rho = p835_6.water_vapour_density(h_j_mid, atm, rho0_gm3)
        e = rho*Tj/216.7 # water vapour pressure, in hPa
        Pdry = P - e # eq. (5) of P.453-14
        y_j = gaseous_attenuation(f_ghz=f_ghz, p_hpa=Pdry, t_k=Tj, rho_gm3=rho)

        # step 4
        Lj = pow(10, (-a_j*y_j)/10)

        # step 5
        TB_dw = (TB_dw_last*Lj) + ((1-Lj)*TB)

    return TB_dw


def upwelling_microwave_brightness_temperature(f_ghz: float, phi1_deg: float,
                                               h1_km: float=0, hk_km=100.1,
                                               atm: p835_6.ReferenceAtmosphere=
                                                   p835_6.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL,
                                               rho0_gm3: float=7.5, emissivity: float=0.95,
                                               t_earth_k: float=290) -> float:
    """
    ITU-R P.676-13, Annex 1, Section 4.2.

    The upwelling atmospheric microwave brightness temperature (K).
    
    Args:
        f_ghz (float): Frequency in GHz, with 1 <= f_ghz <= 1000.
        phi1_deg (float): The local apparent elevation angle at height h1_km (degrees), 
            with phi1_deg >= 0. 0°=horizon, +90°=zenith.
        h1_km (float, optional): Height of atmospheric layer 1 (km). Default value is 0.
        hk_km (float, optional): Height of atmospheric layer k (km). Default value is 100.1.
        atm (p835_6.ReferenceAtmosphere, optional): A reference atmosphere from ITU-R P.835-6.
            Default value is MEAN_ANNUAL_GLOBAL.
        rho0_gm3 (float, optional): Ground-level water vapour density (g/m3). Only applies when atm
            is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.
        emissivity (float, optional): Emissivity of the Earth's surface. Default value is 0.95.
        t_earth_k (float, optional): Temperature of the Earth's surface (K). Default value is 290.

    Returns:
        TB_upwelling (float): The upwelling atmospheric microwave brightness temperature (K).
    """
    # Note: In ITU-R P.676-13, it seems there is an error at equations (28a) and (28c). The -1
    # value is placed outside of the denominator, contrary to eq.(26). Using eq. (28a) and (28c)
    # as is yield results that are very different than those shown in FIGURE 9. However when using
    # -1 within the denominator like in eq.(26), results matches those in FIRGURE 9.

    Re = 6371
    r_1 = None
    n_1 = None
    beta_1_deg = 90-phi1_deg
    sin_beta_1 = sin(radians(beta_1_deg))

    # step 1
    reflectivity = 1 - emissivity
    TB_dw = downwelling_microwave_brightness_temperature(f_ghz, phi1_deg, h1_km, hk_km, atm,
                                                         rho0_gm3)
    TB_uw = (emissivity*_tb(f_ghz, t_earth_k)) + (reflectivity*TB_dw)

    h_lower = h1_km
    h_upper = hk_km
    (j_lower, j_upper) = _layer_indices(h_lower, h_upper)
    for j in range(j_lower, j_upper, 1):
        # step 2
        TB_uw_last = TB_uw

        # step 3
        h_j_bot = _layer_bottom_height(j, j_lower, j_upper, h_lower, h_upper)
        delta_j = _layer_thickness(j, j_lower, j_upper, h_lower, h_upper)
        h_j_mid = h_j_bot+(delta_j/2)
        Tj = p835_6.temperature(h_j_mid, atm)
        TB = _tb(f_ghz, Tj)

        # step 4
        n_j = refractive_index(h_j_mid, atm, rho0_gm3)
        r_j = Re + h_j_bot
        if r_1 is None or n_1 is None:
            r_1 = r_j
            n_1 = n_j
        beta_j_rad = asin(((n_1*r_1)/(n_j*r_j))*sin_beta_1)
        cos_beta_j = cos(beta_j_rad)
        a_j = (-r_j*cos_beta_j)+sqrt((r_j*r_j*cos_beta_j*cos_beta_j)+(2*r_j*delta_j)+
                                     (delta_j*delta_j))
        P = p835_6.pressure(h_j_mid, atm)
        rho = p835_6.water_vapour_density(h_j_mid, atm, rho0_gm3)
        e = rho*Tj/216.7 # water vapour pressure, in hPa
        Pdry = P - e # eq. (5) of P.453-14
        y_j = gaseous_attenuation(f_ghz=f_ghz, p_hpa=Pdry, t_k=Tj, rho_gm3=rho)

        # step 4
        Lj = pow(10, (-a_j*y_j)/10)

        # step 5
        TB_uw = (TB_uw_last*Lj) + ((1-Lj)*TB)

    return TB_uw


def slant_path_instant_oxygen_gaseous_att(f_ghz: float, theta_deg: float, ps_hpa: float,
                                          ts_k: float, rhows_gm3: float) -> float:
    """
    ITU-R P.676-13, Annex 2, Section 1.1.

    Gets the predicted slant path instantaneous gaseous attenuation attributable to oxygen (dB).
    The prediction method is applicable to paths between the surface of the Earth and space for
    elevation angles of 5 degrees and above and for frequencies between 1 and 350 GHz.

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 350.
        theta_deg (float): Elevation angle (degrees), with 5 <= theta_deg <= 90.
        ps_hpa (float): Instantaneous total (barometric) surface pressure (hPa) at the desired
            location.
        ts_k (float): Instantaneous surface temperature (K) at the desired location.
        rhows_gm3 (float): Instantaneous surface water vapour density (g/m3) at the desired
            location.

    Returns:
        Ao (float): The predicted slant path instantaneous gaseous attenuation attributable to
            oxygen (dB).
    """
    es = rhows_gm3*ts_k/216.7
    ps = ps_hpa - es
    yo = dry_air_gaseous_attenuation(f_ghz=f_ghz, p_hpa=ps, t_k=ts_k, rho_gm3=rhows_gm3)
    ao, bo, co, do = _part1_coeffs(f_ghz)
    ho = ao + bo*ts_k + co*ps_hpa + do*rhows_gm3
    Ao = yo*ho/sin(radians(theta_deg))
    return Ao


def _slant_path_statistical_oxygen_gaseous_att(f_ghz: float, theta_deg: float, mean_ps_hpa: float,
                                               mean_ts_k: float, mean_rhows_gm3: float,
                                               psp_hpa: float, tsp_k: float, rhowsp_gm3: float
                                               ) -> float:
    """
    ITU-R P.676-13, Annex 2, Section 1.2.

    Gets the predicted slant path statistical gaseous attenuation attributable to oxygen (dB).
    The prediction method is applicable to paths between the surface of the Earth and space for
    elevation angles of 5 degrees and above and for frequencies between 1 and 350 GHz.

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 350.
        theta_deg (float): Elevation angle (degrees), with 5 <= theta_deg <= 90.
        mean_ps_hpa (float): Mean total (barometric) surface pressure (hPa) at the desired
            location.
        mean_ts_k (float): Mean surface temperature (K) at the desired location.
        mean_rhows_gm3 (float): Mean surface water vapour density (g/m3) at the desired location.
        psp_hpa (float): Total (barometric) surface pressure at the exceedance probability p, in
            hPa, at the desired location.
        tsp_k (float): Surface temperature at the exceedance probability p, in K, at the desired
            location.
        rhowsp_gm3 (float): Surface water vapour density at the exceedance probability p, in g/m3,
            at the desired location.

    Returns:
        Ao (float): The predicted slant path statistical gaseous attenuation attributable to
            oxygen (dB).
    """
    m_es = mean_rhows_gm3*mean_ts_k/216.7
    m_ps = mean_ps_hpa - m_es
    yo = dry_air_gaseous_attenuation(f_ghz=f_ghz, p_hpa=m_ps, t_k=mean_ts_k, rho_gm3=mean_rhows_gm3)
    ao, bo, co, do = _part1_coeffs(f_ghz)
    ho = ao + bo*tsp_k + co*psp_hpa + do*rhowsp_gm3
    Ao = yo*ho/sin(radians(theta_deg))
    return Ao


def slant_path_statistical_oxygen_gaseous_att(f_ghz: float, theta_deg: float, p_percent: float,
                                              lat: float, lon: float, month: int|None=None,
                                              h_mamsl: float|None=None) -> float:
    """
    ITU-R P.676-13, Annex 2, Section 1.2.

    Gets the predicted slant path statistical gaseous attenuation attributable to oxygen (dB).
    The prediction method is applicable to paths between the surface of the Earth and space for
    elevation angles of 5 degrees and above and for frequencies between 1 and 350 GHz.

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 350.
        theta_deg (float): Elevation angle (degrees), with 5 <= theta_deg <= 90.
        p_percent (float): Exceedance probability (CCDF) of interest, in %, with 0.01 <= p <= 99
            for annual statistics and with 0.1 <= p <= 99 for monthly statistics.
        lat (float): Latitude of the desired location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (degrees), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511-3. Default value is None.

    Returns:
        Ao (float): The predicted slant path statistical gaseous attenuation attributable to
            oxygen (dB).
    """
    psp_hpa = p2145_0.surface_total_pressure(p_percent, lat, lon, month, h_mamsl)
    tsp_k = p2145_0.surface_temperature(p_percent, lat, lon, month, h_mamsl)
    rhowsp_gm3 = p2145_0.surface_water_vapour_density(p_percent, lat, lon, month, h_mamsl)
    mean_ps_hpa = p2145_0.mean_surface_total_pressure(lat, lon, month, h_mamsl)
    mean_ts_k = p2145_0.mean_surface_temperature(lat, lon, month, h_mamsl)
    mean_rhows_gm3 = p2145_0.mean_surface_water_vapour_density(lat, lon, month, h_mamsl)
    Ao = _slant_path_statistical_oxygen_gaseous_att(f_ghz, theta_deg, mean_ps_hpa, mean_ts_k,
                                                    mean_rhows_gm3, psp_hpa, tsp_k, rhowsp_gm3)
    return Ao


def slant_path_instant_water_vapour_gaseous_att_1(f_ghz: float, theta_deg: float, ps_hpa: float,
                                                  ts_k: float, rhows_gm3: float) -> float:
    """
    ITU-R P.676-13, Annex 2, Section 2.1.

    Gets the predicted slant path instantaneous gaseous attenuation attributable to water vapour,
    in dB, using method 1. The prediction method is applicable to paths between the surface of the
    Earth and space for elevation angles of 5 degrees and above and for frequencies between 1 and
    350 GHz.
    
    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 350.
        theta_deg (float): Elevation angle (degrees), with 5 <= theta_deg <= 90.
        ps_hpa (float): Instantaneous total (barometric) surface pressure (hPa) at the desired
            location.
        ts_k (float): Instantaneous surface temperature (K) at the desired location.
        rhows_gm3 (float): Instantaneous surface water vapour density (g/m3) at the desired
            location.

    Returns:
        Aw (float): The predicted slant path instantaneous gaseous attenuation attributable to
            water vapour (dB).
    """
    es = rhows_gm3*ts_k/216.7
    ps = ps_hpa - es
    yw = water_vapour_gaseous_attenuation(f_ghz=f_ghz, p_hpa=ps, t_k=ts_k, rho_gm3=rhows_gm3)
    hw = 5.6585E-5*f_ghz + 1.8348
    hw += 2.6846/(((f_ghz-22.235080)**2)+2.7649)
    hw += 5.8905/(((f_ghz-183.310087)**2)+4.9219)
    hw += 2.9810/(((f_ghz-325.152888)**2)+3.0748)
    Aw = yw*hw/sin(radians(theta_deg))
    return Aw


def slant_path_instant_water_vapour_gaseous_att_2(f_ghz: float, theta_deg: float, ps_hpa: float,
                                                  ts_k: float, rhows_gm3: float, vs_kgm2: float
                                                  ) -> float:
    """
    ITU-R P.676-13, Annex 2, Section 2.2.

    Gets the predicted slant path instantaneous gaseous attenuation attributable to water vapour,
    in dB, using method 2. The prediction method is applicable to paths between the surface of the
    Earth and space for elevation angles of 5 degrees and above and for frequencies between 1 and
    350 GHz.
    
    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 350.
        theta_deg (float): Elevation angle (degrees), with 5 <= theta_deg <= 90.
        ps_hpa (float): Instantaneous total (barometric) surface pressure (hPa) at the desired
            location.
        ts_k (float): Instantaneous surface temperature (K) at the desired location.
        rhows_gm3 (float): Instantaneous surface water vapour density (g/m3) at the desired
            location.
        vs_kgm2 (float): Integrated water vapour content (kg/m2 or mm) from the surface of the
            Earth at the desired location.

    Returns:
        Aw (float): The predicted slant path instantaneous gaseous attenuation attributable to
            water vapour (dB).
    """
    aV, bV, cV, dV = _part2_coeffs(f_ghz)
    KV = aV + bV*rhows_gm3 + cV*ts_k + dV*ps_hpa
    Aw = KV*vs_kgm2/sin(radians(theta_deg))
    return Aw


def _slant_path_statistical_water_vapour_gaseous_att(f_ghz: float, theta_deg: float,
                                                     mean_ps_hpa: float, mean_ts_k: float,
                                                     mean_rhows_gm3: float, vsp_kgm2: float
                                                     ) -> float:
    """
    ITU-R P.676-13, Annex 2, Section 2.3.

    Gets the predicted slant path statistical gaseous attenuation attributable to water vapour (dB).
    The prediction method is applicable to paths between the surface of the Earth and space for
    elevation angles of 5 degrees and above and for frequencies between 1 and 350 GHz.

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 350.
        theta_deg (float): Elevation angle (deg), with 5 <= theta_deg <= 90.
        mean_ps_hpa (float): Mean total (barometric) surface pressure (hPa) at the desired location.
        mean_ts_k (float): Mean surface temperature (K) at the desired location.
        mean_rhows_gm3 (float): Mean surface water vapour density (g/m3) at the desired location.
        vsp_kgm2 (float): Integrated water vapour content at the exceedance probability p, in kg/m2
            or mm, from the surface of the Earth at the desired location.

    Returns:
        Aw (float): The predicted slant path statistical gaseous attenuation attributable to water
            vapour (dB).
    """
    aV, bV, cV, dV = _part2_coeffs(f_ghz)
    KV = aV + bV*mean_rhows_gm3 + cV*mean_ts_k + dV*mean_ps_hpa
    Aw = KV*vsp_kgm2/sin(radians(theta_deg))
    return Aw


def slant_path_statistical_water_vapour_gaseous_att(f_ghz: float, theta_deg: float,
                                                    p_percent: float, lat: float, lon: float,
                                                    month: int|None=None, h_mamsl: float|None=None
                                                    ) -> float:
    """
    ITU-R P.676-13, Annex 2, Section 2.3.

    Gets the predicted slant path statistical gaseous attenuation attributable to water vapour (dB).
    The prediction method is applicable to paths between the surface of the Earth and space for
    elevation angles of 5 degrees and above and for frequencies between 1 and 350 GHz.

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 350.
        theta_deg (float): Elevation angle (degrees), with 5 <= theta_deg <= 90.
        p_percent (float): Exceedance probability (CCDF) of interest, in %, with 0.01 <= p <= 99
            for annual statistics and with 0.1 <= p <= 99 for monthly statistics.
        lat (float): Latitude of the desired location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (degrees), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511-3. Default value is None.

    Returns:
        Aw (float): The predicted slant path statistical gaseous attenuation attributable to water
            vapour (dB).
    """
    vsp_kgm2 = p2145_0.integrated_water_vapour_content(p_percent, lat, lon, month, h_mamsl)
    mean_ps_hpa = p2145_0.mean_surface_total_pressure(lat, lon, month, h_mamsl)
    mean_ts_k = p2145_0.mean_surface_temperature(lat, lon, month, h_mamsl)
    mean_rhows_gm3 = p2145_0.mean_surface_water_vapour_density(lat, lon, month, h_mamsl)
    Aw = _slant_path_statistical_water_vapour_gaseous_att(f_ghz, theta_deg, mean_ps_hpa, mean_ts_k,
                                                          mean_rhows_gm3, vsp_kgm2)
    return Aw


def slant_path_instant_gaseous_attenuation(f_ghz: float, theta_deg: float, ps_hpa: float,
                                           ts_k: float, rhows_gm3: float, vs_kgm2: float|None=None
                                           ) -> float:
    """
    ITU-R P.676-13, Annex 2, Sections 1.1 and 2.1.

    Gets the predicted slant path instantaneous gaseous attenuation attributable to both oxygen
    and water vapour (dB). The prediction method is applicable to paths between the surface of the
    Earth and space for elevation angles of 5 degrees and above and for frequencies between 1 and
    350 GHz.

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 350.
        theta_deg (float): Elevation angle (degrees), with 5 <= theta_deg <= 90.
        ps_hpa (float): Instantaneous total (barometric) surface pressure (hPa) at the desired
            location.
        ts_k (float): Instantaneous surface temperature (K) at the desired location.
        rhows_gm3 (float): Instantaneous surface water vapour density (g/m3) at the desired
            location.
        vs_kgm2 (float or None, optional): Integrated water vapour content (kg/m2 or mm) from the
            surface of the Earth at the desired location. When set to None, the prediction method
            from Annex 2, Section 2.1 is used, otherwise the prediction method from Annex 2,
            Section 2.2 is used. Default value is None.

    Returns:
        A_total (float): The predicted slant path instantaneous gaseous attenuation attributable to
            both oxygen and water vapour (dB).
    """
    Ao = slant_path_instant_oxygen_gaseous_att(f_ghz, theta_deg, ps_hpa, ts_k, rhows_gm3)
    if vs_kgm2 is None:
        Aw = slant_path_instant_water_vapour_gaseous_att_1(f_ghz, theta_deg, ps_hpa, ts_k,
                                                           rhows_gm3)
    else:
        Aw = slant_path_instant_water_vapour_gaseous_att_2(f_ghz, theta_deg, ps_hpa, ts_k,
                                                           rhows_gm3, vs_kgm2)
    return Ao+Aw


def slant_path_statistical_gaseous_attenuation(f_ghz: float, theta_deg: float, p_percent: float,
                                               lat: float, lon: float, month: int|None=None,
                                               h_mamsl: float|None=None) -> float:
    """
    ITU-R P.676-13, Annex 2, Sections 1.2 and 2.3.

    Gets the predicted slant path statistical gaseous attenuation attributable to both oxygen and
    water vapour (dB). The prediction method is applicable to paths between the surface of the
    Earth and space for elevation angles of 5 degrees and above and for frequencies between 1 and
    350 GHz.

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 350.
        theta_deg (float): Elevation angle (degrees), with 5 <= theta_deg <= 90.
        p_percent (float): Exceedance probability (CCDF) of interest, in %, with 0.01 <= p <= 99
            for annual statistics and with 0.1 <= p <= 99 for monthly statistics.
        lat (float): Latitude of the desired location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (degrees), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511-3. Default value is None.

    Returns:
        A_total (float): The predicted slant path statistical gaseous attenuation attributable to
            both oxygen and water vapour (dB).
    """
    Ao = slant_path_statistical_oxygen_gaseous_att(f_ghz, theta_deg, p_percent, lat, lon, month,
                                                   h_mamsl)
    Aw = slant_path_statistical_water_vapour_gaseous_att(f_ghz, theta_deg, p_percent, lat, lon,
                                                         month, h_mamsl)
    return Ao+Aw


def _weibull_approximation(f_ghz: float, theta_deg: float, p_percent: float, mean_ps_hpa: float,
                           mean_ts_k: float, mean_rhows_gm3: float, lambdavs: float, kvs: float
                           ) -> float:
    """
    ITU-R P.676-13, Annex 2, Section 2.4.

    Gets the Weibull approximation to the predicted slant path statistical gaseous attenuation
    attributable to water vapour (dB).

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 350.
        theta_deg (float): Elevation angle (degrees), with 5 <= theta_deg <= 90.
        p_percent (float): Exceedance probability (CCDF) of interest, in %.
        mean_ps_hpa (float): Mean total (barometric) surface pressure (hPa) at the desired
            location.
        mean_ts_k (float): Mean surface temperature (K) at the desired location.
        mean_rhows_gm3 (float): Mean surface water vapour density (g/m3) at the desired location.
        lambdavs (float): Surface Weibull water vapour scale parameter at the desired location.
        kvs (float): Surface Weibull water vapour shape parameter at the desired location.
    
    Returns:
        Aw (float): The Weibull approximation to the predicted slant path statistical gaseous
            attenuation attributable to water vapour (dB).
    """
    aV, bV, cV, dV = _part2_coeffs(f_ghz)
    KV = aV + bV*mean_rhows_gm3 + cV*mean_ts_k + dV*mean_ps_hpa
    Aw = lambdavs*KV*pow(-log(p_percent/100), 1/kvs)/sin(radians(theta_deg))
    return Aw


def weibull_approximation(f_ghz: float, theta_deg: float, p_percent: float,
                             lat: float, lon: float, h_mamsl: float|None=None) -> float:
    """
    ITU-R P.676-13, Annex 2, Section 2.4.

    Gets the Weibull approximation to the predicted slant path statistical gaseous attenuation
    attributable to water vapour (dB). This approximation is based on annual statistics.

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 350.
        theta_deg (float): Elevation angle (degrees), with 5 <= theta_deg <= 90.
        p_percent (float): Exceedance probability (CCDF) of interest, in %.
        lat (float): Latitude of the desired location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (degrees), with -180 <= lon <= 180.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511-3. Default value is None.

    Returns:
        Aw (float): The Weibull approximation to the predicted slant path statistical gaseous
            attenuation attributable to water vapour (dB).
    """
    mean_ps_hpa = p2145_0.mean_surface_total_pressure(lat, lon, None, h_mamsl)
    mean_ts_k = p2145_0.mean_surface_temperature(lat, lon, None, h_mamsl)
    mean_rhows_gm3 = p2145_0.mean_surface_water_vapour_density(lat, lon, None, h_mamsl)
    kvs, lambdavs = p2145_0.weibull_parameters(lat, lon, h_mamsl)
    Aw = _weibull_approximation(f_ghz, theta_deg, p_percent, mean_ps_hpa, mean_ts_k,
                                mean_rhows_gm3, lambdavs, kvs)
    return Aw


def _part1_coeffs(f_ghz: float) -> tuple[float, float, float, float]:
    """ITU-R P.676-13, Annex 2."""
    min_freq = 1
    freq_interval = 0.5
    row_size = 5
    num_rows = 700
    row = int((f_ghz - min_freq) / freq_interval)
    if f_ghz >= 118.75: # there is an extra row at 118.75 GHz
        row += 1
    row = max(row, 0)
    row = min(row, num_rows-2)
    index0 = row*row_size
    index1 = (row+1)*row_size
    PART1 = _thread_safe_get_annex2_coeffs_part1_array()
    f0, a0, b0, c0, d0 = PART1[index0 : index0+row_size]
    f1, a1, b1, c1, d1 = PART1[index1 : index1+row_size]
    a = (a0*(f1-f_ghz) + a1*(f_ghz-f0)) / (f1-f0)
    b = (b0*(f1-f_ghz) + b1*(f_ghz-f0)) / (f1-f0)
    c = (c0*(f1-f_ghz) + c1*(f_ghz-f0)) / (f1-f0)
    d = (d0*(f1-f_ghz) + d1*(f_ghz-f0)) / (f1-f0)
    return (a, b, c, d)


def _part2_coeffs(f_ghz: float) -> tuple[float, float, float, float]:
    """ITU-R P.676-13, Annex 2."""
    min_freq = 1
    freq_interval = 0.5
    row_size = 5
    num_rows = 699
    row = int((f_ghz - min_freq) / freq_interval)
    row = max(row, 0)
    row = min(row, num_rows-2)
    index0 = row*row_size
    index1 = (row+1)*row_size
    PART2 = _thread_safe_get_annex2_coeffs_part2_array()
    f0, a0, b0, c0, d0 = PART2[index0 : index0+row_size]
    f1, a1, b1, c1, d1 = PART2[index1 : index1+row_size]
    a = (a0*(f1-f_ghz) + a1*(f_ghz-f0)) / (f1-f0)
    b = (b0*(f1-f_ghz) + b1*(f_ghz-f0)) / (f1-f0)
    c = (c0*(f1-f_ghz) + c1*(f_ghz-f0)) / (f1-f0)
    d = (d0*(f1-f_ghz) + d1*(f_ghz-f0)) / (f1-f0)
    return (a, b, c, d)


def _load_annex2_coeffs_part1() -> array:
    pathname = join(_du.install_dir(), _p676_13_shared['DATA_DIR'], 'R11010000020001TXTM.txt')
    part1 = p1144_13.load_digital_map(pathname)
    return part1


def _load_annex2_coeffs_part2() -> array:
    pathname = join(_du.install_dir(), _p676_13_shared['DATA_DIR'], 'R11010000020002TXTM.txt')
    part2 = p1144_13.load_digital_map(pathname)
    return part2


def _thread_safe_get_annex2_coeffs_part1_array() -> array:
    arr = _p676_13_shared['annex2_coeffs_part1_array']
    if arr is not None:
        return arr
    with _p676_13_shared['annex2_coeffs_part1_lock']:
        arr = _p676_13_shared['annex2_coeffs_part1_array']
        if arr is None:
            try:
                arr = _load_annex2_coeffs_part1()
            except FileNotFoundError:
                _download_rec_data()
                arr = _load_annex2_coeffs_part1()
            _p676_13_shared['annex2_coeffs_part1_array'] = arr
    return arr


def _thread_safe_get_annex2_coeffs_part2_array() -> array:
    arr = _p676_13_shared['annex2_coeffs_part2_array']
    if arr is not None:
        return arr
    with _p676_13_shared['annex2_coeffs_part2_lock']:
        arr = _p676_13_shared['annex2_coeffs_part2_array']
        if arr is None:
            try:
                arr = _load_annex2_coeffs_part2()
            except FileNotFoundError:
                _download_rec_data()
                arr = _load_annex2_coeffs_part2()
            _p676_13_shared['annex2_coeffs_part2_array'] = arr
    return arr


def _download_rec_data() -> None:
    data_dir = _p676_13_shared['DATA_DIR']
    full_path_data_dir = join(_du.install_dir(), data_dir)
    filenames = ['R11010000020001TXTM.txt', 'R11010000020002TXTM.txt']
    lock = FileLock(_du.get_lockfile_pathname(data_dir))
    with lock:
        if _du.files_all_exist(full_path_data_dir, filenames) is False:
            url = 'https://www.itu.int/dms_pub/itu-r/oth/11/01/R11010000020001TXTM.txt'
            _du.download(url, full_path_data_dir)
            url = 'https://www.itu.int/dms_pub/itu-r/oth/11/01/R11010000020002TXTM.txt'
            _du.download(url, full_path_data_dir)
            _du.print_notice()
        else:
            _du.print_already_installed(full_path_data_dir, filenames)


_p676_13_shared = {
    'DATA_DIR': 'p676_13',

    'annex2_coeffs_part1_lock': Lock(),
    'annex2_coeffs_part1_array': None,

    'annex2_coeffs_part2_lock': Lock(),
    'annex2_coeffs_part2_array': None,

    'TABLE_1': (
        50.474214,0.975,9.651,6.690,0.0,2.566,6.850,
        50.987745,2.529,8.653,7.170,0.0,2.246,6.800,
        51.503360,6.193,7.709,7.640,0.0,1.947,6.729,
        52.021429,14.320,6.819,8.110,0.0,1.667,6.640,
        52.542418,31.240,5.983,8.580,0.0,1.388,6.526,
        53.066934,64.290,5.201,9.060,0.0,1.349,6.206,
        53.595775,124.600,4.474,9.550,0.0,2.227,5.085,
        54.130025,227.300,3.800,9.960,0.0,3.170,3.750,
        54.671180,389.700,3.182,10.370,0.0,3.558,2.654,
        55.221384,627.100,2.618,10.890,0.0,2.560,2.952,
        55.783815,945.300,2.109,11.340,0.0,-1.172,6.135,
        56.264774,543.400,0.014,17.030,0.0,3.525,-0.978,
        56.363399,1331.800,1.654,11.890,0.0,-2.378,6.547,
        56.968211,1746.600,1.255,12.230,0.0,-3.545,6.451,
        57.612486,2120.100,0.910,12.620,0.0,-5.416,6.056,
        58.323877,2363.700,0.621,12.950,0.0,-1.932,0.436,
        58.446588,1442.100,0.083,14.910,0.0,6.768,-1.273,
        59.164204,2379.900,0.387,13.530,0.0,-6.561,2.309,
        59.590983,2090.700,0.207,14.080,0.0,6.957,-0.776,
        60.306056,2103.400,0.207,14.150,0.0,-6.395,0.699,
        60.434778,2438.000,0.386,13.390,0.0,6.342,-2.825,
        61.150562,2479.500,0.621,12.920,0.0,1.014,-0.584,
        61.800158,2275.900,0.910,12.630,0.0,5.014,-6.619,
        62.411220,1915.400,1.255,12.170,0.0,3.029,-6.759,
        62.486253,1503.000,0.083,15.130,0.0,-4.499,0.844,
        62.997984,1490.200,1.654,11.740,0.0,1.856,-6.675,
        63.568526,1078.000,2.108,11.340,0.0,0.658,-6.139,
        64.127775,728.700,2.617,10.880,0.0,-3.036,-2.895,
        64.678910,461.300,3.181,10.380,0.0,-3.968,-2.590,
        65.224078,274.000,3.800,9.960,0.0,-3.528,-3.680,
        65.764779,153.000,4.473,9.550,0.0,-2.548,-5.002,
        66.302096,80.400,5.200,9.060,0.0,-1.660,-6.091,
        66.836834,39.800,5.982,8.580,0.0,-1.680,-6.393,
        67.369601,18.560,6.818,8.110,0.0,-1.956,-6.475,
        67.900868,8.172,7.708,7.640,0.0,-2.216,-6.545,
        68.431006,3.397,8.652,7.170,0.0,-2.492,-6.600,
        68.960312,1.334,9.650,6.690,0.0,-2.773,-6.650,
        118.750334,940.300,0.010,16.640,0.0,-0.439,0.079,
        368.498246,67.400,0.048,16.400,0.0,0.000,0.000,
        424.763020,637.700,0.044,16.400,0.0,0.000,0.000,
        487.249273,237.400,0.049,16.000,0.0,0.000,0.000,
        715.392902,98.100,0.145,16.000,0.0,0.000,0.000,
        773.839490,572.300,0.141,16.200,0.0,0.000,0.000,
        834.145546,183.100,0.145,14.700,0.0,0.000,0.000
    ),

    'TABLE_2': (
        22.235080,.1079,2.144,26.38,.76,5.087,1.00,
        67.803960,.0011,8.732,28.58,.69,4.930,.82,
        119.995940,.0007,8.353,29.48,.70,4.780,.79,
        183.310087,2.273,.668,29.06,.77,5.022,.85,
        321.225630,.0470,6.179,24.04,.67,4.398,.54,
        325.152888,1.514,1.541,28.23,.64,4.893,.74,
        336.227764,.0010,9.825,26.93,.69,4.740,.61,
        380.197353,11.67,1.048,28.11,.54,5.063,.89,
        390.134508,.0045,7.347,21.52,.63,4.810,.55,
        437.346667,.0632,5.048,18.45,.60,4.230,.48,
        439.150807,.9098,3.595,20.07,.63,4.483,.52,
        443.018343,.1920,5.048,15.55,.60,5.083,.50,
        448.001085,10.41,1.405,25.64,.66,5.028,.67,
        470.888999,.3254,3.597,21.34,.66,4.506,.65,
        474.689092,1.260,2.379,23.20,.65,4.804,.64,
        488.490108,.2529,2.852,25.86,.69,5.201,.72,
        503.568532,.0372,6.731,16.12,.61,3.980,.43,
        504.482692,.0124,6.731,16.12,.61,4.010,.45,
        547.676440,.9785,.158,26.00,.70,4.500,1.00,
        552.020960,.1840,.158,26.00,.70,4.500,1.00,
        556.935985,497.0,.159,30.86,.69,4.552,1.00,
        620.700807,5.015,2.391,24.38,.71,4.856,.68,
        645.766085,.0067,8.633,18.00,.60,4.000,.50,
        658.005280,.2732,7.816,32.10,.69,4.140,1.00,
        752.033113,243.4,.396,30.86,.68,4.352,.84,
        841.051732,.0134,8.177,15.90,.33,5.760,.45,
        859.965698,.1325,8.055,30.60,.68,4.090,.84,
        899.303175,.0547,7.914,29.85,.68,4.530,.90,
        902.611085,.0386,8.429,28.65,.70,5.100,.95,
        906.205957,.1836,5.110,24.08,.70,4.700,.53,
        916.171582,8.400,1.441,26.73,.70,5.150,.78,
        923.112692,.0079,10.293,29.00,.70,5.000,.80,
        970.315022,9.009,1.919,25.50,.64,4.940,.67,
        987.926764,134.6,.257,29.85,.68,4.550,.90,
        1780.000000,17506.,.952,196.3,2.00,24.15,5.00
    )
}
