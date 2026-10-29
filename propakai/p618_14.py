# Copyright (c) 2025 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.618-14.

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite this software
    package along with the underlying ITU-R standard:

    * **ITU-R Standard:** International Telecommunication Union (2023).
      *Recommendation ITU-R P.618-14: Propagation data and prediction methods required for the
      design of Earth-space telecommunication systems*. Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.618/en
"""

from math import sin, cos, radians, sqrt, log10, log, atan2, exp, degrees
from propakai import p453_14
from propakai import p676_13
from propakai import p837_8
from propakai import p838_3
from propakai import p839_4
from propakai import p840_9
from propakai import p1511_3


__all__ = ['rain_attenuation',
           'scintillation_fading',
           'gaseous_attenuation',
           'cloud_attenuation',
           'total_atmospheric_attenuation',
           'mean_radiating_temperature',
           'sky_noise_temperature',
           'hydrometeor_cross_pol_discrimination']


def rain_attenuation(f_ghz: float, theta_deg: float, p_percent: float,
                     lat: float, lon: float, tau_deg: float,
                     hs_km: float|None=None, r001_mmh: float|None=None) -> float:
    """
    ITU-R P.618-14, Annex 1, Section 2.2.1.1.

    Estimates the attenuation due to rain exceeded for p% of an average year (dB).
    
    Args:
        f_ghz (float): Frequency of interest (GHz), with f_ghz <= 55.
        theta_deg (float): Elevation angle of the slant propagation path (degrees).
        p_percent (float): Time percentage, with 0.001 <= p <= 5.
        lat (float): Latitude of the earth station (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the earth station (degrees), with -180 <= lon <= 180.
        tau_deg (float): Polarization tilt angle relative to the horizontal (degrees). Use 45° for
            circular polarization.
        hs_km (float, optional): Height above mean sea level of the earth station (km). When set to
            None, the height is automatically obtained from Recommendation ITU-R P.1511-3. Default
            value is None.
        r001_mmh (float, optional): Point rainfall rate for the location for 0.01% of an average
            year (mm/h). When set to None, the value is automatically obtained from Recommendation
            ITU-R P.837-8 (bi-linear interpolation of pre-computed values in the R001.txt digital
            map). Default value is None.

    Returns:
        AR (float): Attenuation due to rain exceeded for p% of an average year (dB).
    """
    Re = 8500
    if hs_km is None:
        hs_km = p1511_3.topographic_height(lat, lon)/1000
    hs = hs_km
    if r001_mmh is None:
        r001_mmh = p837_8.annual_rainfall_rate_001(lat, lon)
    R001 = r001_mmh
    p = p_percent

    # Step 1
    hR = p839_4.mean_annual_rain_height(lat, lon)

    # Step 2
    if (hR-hs) <= 0:
        return 0
    sin_t = sin(radians(theta_deg))
    if theta_deg >= 5:
        Ls = (hR-hs)/sin_t
    else:
        Ls = (2*(hR-hs))/(sqrt((sin_t*sin_t)+(2*(hR-hs)/Re))+sin_t)

    # Step 3
    cos_t = cos(radians(theta_deg))
    LG = Ls*cos_t

    # Step 4
    if R001 == 0:
        return 0

    # Step 5
    k, alpha = p838_3.coefficients(f_ghz=f_ghz, theta_deg=theta_deg, tau_deg=tau_deg)
    yR = k*pow(R001, alpha)

    # Step 6
    r001 = 1/(1+(0.78*sqrt(LG*yR/f_ghz))-(0.38*(1-exp(-2*LG))))

    # Step 7
    sigma_deg = degrees(atan2(hR-hs, LG*r001))
    if sigma_deg > theta_deg:
        LR = LG*r001/cos_t
    else:
        LR = (hR-hs)/sin_t
    abs_lat = abs(lat)
    if abs_lat < 36:
        X = 36-abs_lat
    else:
        X = 0
    a = 1-exp(-(theta_deg/(1+X)))
    b = sqrt(LR*yR)/(f_ghz*f_ghz)
    v001 = 1/(1+(sqrt(sin_t)*((31*a*b)-0.45)))

    # Step 8
    LE = LR*v001

    # Step 9
    A001 = yR*LE

    # Step 10
    if p >= 1 or abs_lat >= 36:
        Beta = 0
    elif p < 1 and abs_lat < 36 and theta_deg >= 25:
        Beta = -0.005*(abs_lat-36)
    else:
        Beta = (-0.005*(abs_lat-36)) + 1.8 - (4.25*sin_t)

    Ap = A001*pow(p/0.01, -(0.655 + 0.033*log(p) - 0.045*log(A001) - Beta*(1-p)*sin_t))
    return Ap


def scintillation_fading(f_ghz: float, theta_deg: float, p_percent: float, lat: float, lon: float,
                         d_m: float, eta: float=0.5) -> float:
    """
    ITU-R P.618-14, Annex 1, Section 2.4.1.

    Calculates the tropospheric scintillation fading, exceeded for p% of the time (dB).

    Args:
        f_ghz (float): Frequency (GHz), with 4 <= f_ghz <= 55.
        theta_deg (float): Free-space elevation angle (degrees), with 5 <= theta_deg <= 90.
        p_percent (float): Time percentage, with 0.01 < p <= 50.
        lat (float): Latitude (degrees), with -90 <= lat <= 90. Latitude and longitude values are
            utilized to obtain Nwet, the median value of the wet term of the surface refractivity
            exceeded for the average year, from the digital maps in Recommendation ITU-R P.453-14.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        d_m (float): Physical diameter of the earth-station antenna (meters).
        eta (float, optional): Antenna efficiency; if unknown, 0.5 is a conservative estimate.
            Default value is 0.5.
    
    Returns:
        AS (float): Tropospheric scintillation fading, exceeded for p% of the time (dB).
    """
    Nwet = p453_14.median_annual_nwet(lat, lon)
    sigma_ref = 3.6E-3 + (1E-4*Nwet)
    theta_rad = radians(theta_deg)
    sin_theta = sin(theta_rad)
    L = 2000/(sqrt((sin_theta*sin_theta)+2.35E-4)+sin_theta)
    Deff = sqrt(eta)*d_m
    x = 1.22*Deff*Deff*(f_ghz/L)
    sqrt_arg = (3.86*pow((x*x)+1,11/12)*sin((11/6)*atan2(1,x)))-(7.08*pow(x,5/6))
    if sqrt_arg < 0:
        return 0
    g_x = sqrt(sqrt_arg)
    sigma = sigma_ref*pow(f_ghz,7/12)*g_x/pow(sin_theta,1.2)
    log_p = log10(p_percent)
    ap = (-0.061*log_p*log_p*log_p) + (0.072*log_p*log_p) - (1.71*log_p) + 3.0
    Ap = ap*sigma
    return Ap


def gaseous_attenuation(f_ghz: float, theta_deg: float, p_percent: float, lat: float, lon: float,
                        hs_km: float|None=None) -> float:
    """
    ITU-R P.618-14, Annex 1, Section 2.5.

    Gets the gaseous attenuation due to water vapour and oxygen for a fixed probability (dB), as
    estimated by Recommendation ITU-R P.676-13.

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 350.
        theta_deg (float): Elevation angle (degrees), with 5 <= theta_deg <= 90.
        p_percent (float): Exceedance probability (CCDF) of interest, in %, with 0.01 <= p <= 99
            for annual statistics and with 0.1 <= p <= 99 for monthly statistics.
        lat (float): Latitude of the earth station (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the earth station (degrees), with -180 <= lon <= 180.
        hs_km (float, optional): Height above mean sea level of the earth station (km). When set to
            None, the height is automatically obtained from Recommendation ITU-R P.1511-3. Default
            value is None.

    Returns:
        AG (float): The gaseous attenuation due to water vapour and oxygen for a fixed
            probability (dB).
    """
    if hs_km is not None:
        h_mamsl = hs_km*1000
    else:
        h_mamsl = None
    # from Annex 2 of P.676-13, using annual statistics
    AG = p676_13.slant_path_statistical_gaseous_attenuation(f_ghz, theta_deg, p_percent, lat, lon,
                                                            None, h_mamsl)
    return AG


def cloud_attenuation(f_ghz: float, theta_deg: float, p_percent: float, lat: float, lon: float
                      ) -> float:
    """
    ITU-R P.618-14, Annex 1, Section 2.5.

    Gets the attenuation due to clouds for a fixed probability (dB), as estimated by Recommendation
    ITU-R P.840-9.

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 200.
        theta_deg (float): Elevation angle (deg).
        p_percent (float): Exceedance probability (CCDF) of interest, in %, with 0.01 <= p <= 99.
        lat (float): Latitude of the earth station (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the earth station (degrees), with -180 <= lon <= 180.

    Returns:
        AC (float): The attenuation due to clouds for a fixed probability (dB).
    """
    # using annual statistics
    AC = p840_9.slant_path_statistical_cloud_attenuation(f_ghz, theta_deg, p_percent, lat, lon,
                                                         None)
    return AC


def total_atmospheric_attenuation(f_ghz: float, theta_deg: float, p_percent: float, lat: float,
                                  lon: float, tau_deg: float, d_m: float, eta: float=0.5,
                                  hs_km: float|None=None, exclude_scintillation: bool=False,
                                  r001_mmh: float|None=None
                                  ) -> tuple[float, float, float, float, float]:
    """
    ITU-R P.618-14, Annex 1, Section 2.5.

    Estimation of total attenuation due to multiple sources of simultaneously occurring atmospheric
    attenuation (dB). Total attenuation represents the combined effect of rain, gas, clouds and
    scintillation.
    
    Args:
        f_ghz (float): Frequency (GHz), with 4 <= f_ghz <= 55.
        theta_deg (float): Free-space elevation angle (degrees), with 5 <= theta_deg <= 90.
        p_percent (float): Time percentage, with 0.01 < p <= 50.
        lat (float): Latitude of the earth station (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the earth station (degrees), with -180 <= lon <= 180.
        tau_deg (float): Polarization tilt angle relative to the horizontal (degrees). Use 45° for
            circular polarization.
        d_m (float): Physical diameter of the earth-station antenna (meters).
        eta (float, optional): Antenna efficiency; if unknown, 0.5 is a conservative estimate.
            Default value is 0.5.
        hs_km (float, optional): Height above mean sea level of the earth station (km). When set to
            None, the height is automatically obtained from Recommendation ITU-R P.1511-3. Default
            value is None.
        exclude_scintillation (bool, optional): Whether to exclude tropospheric scintillation from
            the total attenuation. Relevant in the context of sky noise temperature calculation.
            When set to True, parameters d_m and eta are unused. Default value is False.
        r001_mmh (float, optional): Point rainfall rate for the location for 0.01% of an average
            year (mm/h). When set to None, the value is automatically obtained from Recommendation
            ITU-R P.837-8 (bi-linear interpolation of pre-computed values in the R001.txt digital
            map). Default value is None.
    
    Returns:
        AT (float): Estimation of total attenuation (dB) due to multiple sources of
            simultaneously occurring atmospheric attenuation (rain, gas, clouds and scintillation).
        AR (float): Attenuation due to rain for a fixed probability (dB).
        AC (float): Attenuation due to clouds for a fixed probability (dB), as estimated by
            Recommendation ITU-R P.840-9.
        AG (float): Gaseous attenuation due to water vapour and oxygen for a fixed probability
            (dB), as estimated by Recommendation ITU-R P.676-13.
        AS (float): Attenuation due to tropospheric scintillation for a fixed probability (dB).
    """
    AG = gaseous_attenuation(f_ghz, theta_deg, max(p_percent, 5.0), lat, lon, hs_km)
    AC = cloud_attenuation(f_ghz, theta_deg, max(p_percent, 5.0), lat, lon)
    if exclude_scintillation is False:
        AS = scintillation_fading(f_ghz, theta_deg, p_percent, lat, lon, d_m, eta)
    else:
        AS = 0

    if p_percent <= 5:
        AR = rain_attenuation(f_ghz, theta_deg, p_percent, lat, lon, tau_deg, hs_km, r001_mmh)
        AT = AG + sqrt(((AR+AC)*(AR+AC))+(AS*AS))
    else:
        AR = 0
        AT = AG + sqrt((AC*AC)+(AS*AS))

    return (AT, AR, AC, AG, AS)


def mean_radiating_temperature(ts_k: float) -> float:
    """
    ITU-R P.618-14, Annex 1, Section 3.

    Estimates the mean radiating temperature (K) from the surface temperature.

    Args:
        ts_k (float): The surface temperature (K).

    Returns:
        Tmr (float): The mean radiating temperature (K).
    """
    Tmr = 37.34 + (0.81*ts_k)
    return Tmr


def sky_noise_temperature(at_db: float, tmr_k: float=275) -> float:
    """
    ITU-R P.618-14, Annex 1, Section 3.

    Estimates the sky noise temperature at a ground station antenna (K).

    Args:
        at_db (float): The total atmospheric attenuation excluding scintillation fading (dB).
        tmr_k (float, optional): The mean radiating temperature (K). Default value is 275.

    Returns:
        Tsky (float): The sky noise temperature at a ground station antenna (K).
    """
    pwA = pow(10, -at_db/10)
    Tsky = (tmr_k*(1-pwA))+(2.7*pwA)
    return Tsky


def hydrometeor_cross_pol_discrimination(f_ghz: float, theta_deg: float, p_percent: float,
                                         tau_deg: float, ap_db: float) -> float:
    """
    ITU-R P.618-14, Annex 1, Section 4.1.

    Gets the hydrometeor-induced cross-polarization discrimination (dB) not exceeded for p% of the
    time.

    Args:
        f_ghz (float): Frequency (GHz), with 6 <= f_GHz <= 55.
        theta_deg (float): Path elevation angle (degrees), with theta_deg <= 60.
        p_percent (float): Time percentage for which the cross-polarization discrimination is not
            exceeded, in %. Must be set to one of the four following values: 1, 0.1, 0.01 and 0.001.
        tau_deg (float): Tilt angle of the linearly polarized electric field vector with respect
            to the horizontal (degrees). For circular polarization use 45°.
        ap_db (float): Rain attenuation (dB) exceeded for the required percentage of time, p, for
            the path in question, commonly called co-polar attenuation (CPA). May be estimated
            using rain_attenuation().
    
    Returns:
        XPDp (float): The hydrometeor-induced cross-polarization discrimination (dB) not exceeded
            for p% of the time.
    """
    # step 1
    if f_ghz >= 6 and f_ghz < 9:
        Cf = 60*log10(f_ghz) - 28.3
    elif f_ghz >= 9 and f_ghz < 36:
        Cf = 26*log10(f_ghz) + 4.1
    elif f_ghz >= 36 and f_ghz <= 55:
        Cf = 35.9*log10(f_ghz) - 11.3
    else:
        raise ValueError('f_ghz is out of range.')

    # step 2
    if f_ghz >= 6 and f_ghz < 9:
        V = 30.8*pow(f_ghz, -0.21)
    elif f_ghz >= 9 and f_ghz < 20:
        V = 12.8*pow(f_ghz, 0.19)
    elif f_ghz >= 20 and f_ghz < 40:
        V = 22.6
    elif f_ghz >= 40 and f_ghz <= 55:
        V = 13.0*pow(f_ghz, 0.15)
    else:
        raise ValueError('f_ghz is out of range.')
    CA = V*log10(ap_db)

    # step 3
    Ctau = -10*log10(1-(0.484*(1+cos(radians(4*tau_deg)))))

    # step 4
    Ctheta = -40*log10(cos(radians(theta_deg)))

    # step 5
    if p_percent == 1:
        sigma = 0
    elif p_percent == 0.1:
        sigma = 5
    elif p_percent == 0.01:
        sigma = 10
    elif p_percent == 0.001:
        sigma = 15
    else:
        raise ValueError('Unexpected value for p_percent.')
    Csigma = 0.0053*sigma*sigma

    # step 6
    XPDrain = Cf - CA + Ctau + Ctheta + Csigma

    # step 7
    Cice = XPDrain*(0.3+(0.1*log10(p_percent)))/2

    # step 8
    XPDp = XPDrain - Cice

    return XPDp
