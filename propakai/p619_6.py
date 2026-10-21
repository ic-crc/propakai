# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.619-6.

P.619 : Propagation data required for the evaluation of interference between stations in space and
those on the surface of the Earth.

https://www.itu.int/rec/R-REC-P.619/en
"""

from enum import Enum
from math import pi, cos, sin, tan, radians, degrees, sqrt, atan2, log10, exp, acos
from propakai import p453_14
from propakai import p676_13
from propakai import p834_9
from propakai import p835_6
from propakai import p838_3


__all__ = ['CalculationStatus',
           'free_space_basic_transmission_loss',
           'beam_spreading_loss',
           'straight_line_earth_space_path',
           'apparent_elevation_angle',
           'free_space_elevation_angle',
           'space_earth_path_gaseous_attenuation',
           'earth_space_path_gaseous_attenuation',
           'tropospheric_scintillation_attenuation',
           'ray_heights',
           'unwanted_rain_scattering_power']


class CalculationStatus(Enum):
    """Enumerates calculation statuses. Indicates whether calculations could be completed or not."""
    COMPLETED                 = 1
    OUTSIDE_VICTIMS_BEAMWIDTH = 2
    DUCTING_OR_NO_LOS         = 3


def free_space_basic_transmission_loss(f_ghz: float, d_km: float) -> float:
    """
    ITU-R P.619-6, Annex 1, Section 2.1.

    Calculates the basic transmission loss assuming the complete radio path is in a vacuum with no
    obstruction, in dB.

    Args:
        f_ghz (float): Frequency (GHz).
        d_km (float): Path length (km).

    Returns:
        Lbfs (float): The free space basic transmission loss (dB).
    """
    Lbfs = 92.45 + 20*log10(f_ghz*d_km)
    return Lbfs


def beam_spreading_loss(theta0_deg: float, h_km: float) -> float:
    """
    ITU-R P.619-6, Annex 1, Section 2.4.2.

    Estimates the signal loss due to beam spreading for a wave propagating through the total
    atmosphere in the Earth-space and space-Earth directions (dB). This effect is insignificant for
    elevation angles above 5 degrees.
    
    Args:
        theta0_deg (float): Free-space elevation angle (degrees), with theta0_deg < 10.
        h_km (float): Altitude of the lower point above sea level (km), with h_km <= 5.

    Returns:
        Abs (float): The signal loss due to beam spreading for a wave propagating through the total
            atmosphere in the Earth-space and space-Earth directions (dB).
    """
    return p834_9.beam_spreading_loss(theta0_deg, h_km)


def straight_line_earth_space_path(he_km: float, late: float, lone: float,
                                   hs_km: float, lats: float, lons: float,
                                   ) -> tuple[float, float, float]:
    """
    ITU-R P.619-6, Attachment A to Annex 1.

    Calculates the distance, elevation angle and azimuth of a space station as viewed from an
    earth-based station. It is based on spherical Earth geometry, and ignores the effect of 
    atmospheric refraction.

    Args:
        he_km (float): Altitude of earth-based station (km above sea level).
        late (float): Latitude of earth-based station (degrees), with -90 <= late <= 90.
        lone (float): Longitude of earth-based station (degrees), with -180 <= lone <= 180.
        hs_km (float): Altitude of space station (km above sea level).
        lats (float): Latitude of sub-satellite point (degrees), with -90 <= lats <= 90.
        lons (float): Longitude of sub-satellite point (degrees), with -180 <= lons <= 180.
        
    Returns:
        Dts (float): Straight-line distance between the earth-based station and the space
            station (km).
        theta0_deg (float): Elevation angle of the straight line from the earth-based station to
            the space station (degrees). It is the elevation angle of the ray at the earth-based
            station which would exist in the absence of tropospheric refraction, sometimes referred
            to as the free-space elevation angle. 0°=horizon, +90°=zenith, -90°=nadir.
        azm_deg (float): Azimuth of the space station as viewed from an earth-based station, in
            degrees from true North. 0°=North, 90°=East, 180°=South, 270°=West. The azimuth is
            indeterminate if the elevation angle represents a vertical path.
    """
    # Calculate delta, the difference in longitude between the sub-satellite point and the
    # earth-based station, limited to less than half a circle, positive when the space station is
    # to the east of the earth-based station, in degrees.
    delta_deg = lons-lone
    if delta_deg > 180:
        delta_deg -= 360
    elif delta_deg < -180:
        delta_deg += 360

    phi_t = late
    phi_s = lats

    # Step 1
    Re = 6371 # average Earth radius (km)
    Rs = Re + hs_km
    Rt = Re + he_km

    # Step 2
    delta_rad = radians(delta_deg)
    cos_d     = cos(delta_rad)
    sin_d     = sin(delta_rad)
    cos_phi_s = cos(radians(phi_s))
    cos_phi_t = cos(radians(phi_t))
    sin_phi_s = sin(radians(phi_s))
    sin_phi_t = sin(radians(phi_t))
    X1 = Rs*cos_phi_s*cos_d
    Y1 = Rs*cos_phi_s*sin_d
    Z1 = Rs*sin_phi_s

    # Step 3
    X2 = X1*sin_phi_t - Z1*cos_phi_t
    Y2 = Y1
    Z2 = Z1*sin_phi_t + X1*cos_phi_t - Rt

    # Step 4
    Dts = sqrt(X2*X2 + Y2*Y2 + Z2*Z2)

    # Step 5
    Gts = sqrt(X2*X2 + Y2*Y2)

    # Step 6
    theta0_rad = atan2(Gts, Z2)
    theta0_deg = degrees(theta0_rad)

    # Note: the following line is not in the recommendation, however it seems needed to have the
    #       horizon at 0 deg, zenith at 90 deg and nadir at -90 deg.
    theta0_deg = -theta0_deg + 90

    # Step 7
    psi_rad = atan2(X2, Y2)

    # Step 8
    #psi_deg = 180 - degrees(psi_rad)
    # Note: Slight change from what is in the recommendation so to have azimuth from true North.
    psi_deg = (degrees(psi_rad) + 450) % 360

    return (Dts, theta0_deg, psi_deg)


def apparent_elevation_angle(he_km: float, theta0_deg: float) -> float:
    """
    ITU-R P.619-6, Attachment B to Annex 1.

    Estimates the apparent elevation angle (at Earth-based station) from the free-space elevation
    angle (at Earth-based station).

    Args:
        he_km (float): Altitude of earth-based station (km above sea level), with he_km <= 3.
        theta0_deg (float): Free-space elevation angle (degrees), with -1 <= theta_deg <= 10.
            It is he elevation angle calculated without taking atmospheric refraction into account.

    Returns:
        theta_deg (float): Apparent or actual elevation (degrees). It is the elevation angle
            calculated taking atmospheric refraction into account. This is the optimum elevation
            angle for a high-gain antenna at the earth-based station intended to provide a link to
            the space station.
    """
    Tfs1 = 1.728 + (0.5411*theta0_deg) + (0.03723*theta0_deg*theta0_deg)
    Tfs2 = 0.1815 + (0.06272*theta0_deg) + (0.01380*theta0_deg*theta0_deg)
    Tfs3 = 0.01727 + (0.008288*theta0_deg)
    tau_fs = 1/(Tfs1 + (he_km*Tfs2) + (he_km*he_km*Tfs3))
    theta_deg = theta0_deg + tau_fs
    return theta_deg


def free_space_elevation_angle(he_km: float, theta_deg: float) -> float:
    """
    ITU-R P.619-6, Attachment B to Annex 1.

    Estimates the free-space elevation angle (at Earth-based station) from the apparent elevation
    angle (at Earth-based station).
    
    Args:
        he_km (float): Altitude of earth-based station (km above sea level), with he_km <= 3.
        theta_deg (float): Apparent or actual elevation angle (degrees). It is the elevation angle
            calculated taking atmospheric refraction into account. This is the optimum elevation
            angle for a high-gain antenna at the earth-based station intended to provide a link to
            the space station.
    
    Returns:
        theta0_deg (float): Free-space elevation angle (degrees). It is he elevation angle
            calculated without taking atmospheric refraction into account.
    """
    T1 = 1.314 + (0.6437*theta_deg) + (0.02869*theta_deg*theta_deg)
    T2 = 0.2305 + (0.09428*theta_deg) + (0.01096*theta_deg*theta_deg)
    T3 = 0.008583
    tau = 1/(T1 + (he_km*T2) + (he_km*he_km*T3))
    theta0_deg = theta_deg - tau
    return theta0_deg


def space_earth_path_gaseous_attenuation(f_ghz: float, he_km: float, hs_km: float,
                                         phie_deg: float|None, phis_deg: float,
                                         delta_phie_deg: float|None,
                                         atm: p835_6.ReferenceAtmosphere=
                                            p835_6.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL,
                                         rho0_gm3: float=7.5
                                         ) -> tuple[float, CalculationStatus]:
    """
    ITU-R P.619-6, Attachment C to Annex 1 (C.4).

    Estimates the attenuation due to atmospheric gases along a space-Earth propagation path
    (descending ray). For a space-Earth propagation path, the antenna of the space-based station
    is the transmitting antenna.

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000. Gaseous attenuation can be ignored
            below 1 GHz.
        he_km (float): Height of Earth station (km above mean sea level), with 0 <= he_km < hs_km.
        hs_km (float): Height of space-based station (km above mean sea level),
            with 0 <= he_km < hs_km.
        phie_deg (float or None): Elevation angle of the main beam of the earth based station
            (degrees). If set to None, assumes the incident elevation angle is within the
            half-power beamwidth of the earth station. 0°=horizon, +90°=zenith, -90°=nadir.
        phis_deg (float): Elevation angle of the main beam of the space-based station antenna
            (degrees). 0°=horizon, +90°=zenith, -90°=nadir.
        delta_phie_deg (float or None): Half-power beamwidth of the Earth based station (degrees).
            If set to None, assumes the incident elevation angle is within the half-power beamwidth
            of the earth station.
        atm (p835_6.ReferenceAtmosphere, optional): A reference atmosphere from ITU-R P.835-6.
            Default value is MEAN_ANNUAL_GLOBAL.
        rho0_gm3 (float, optional): Ground-level water vapour density (g/m3). Only applies when atm
            is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.
        
    Returns:
        Ag (float): The total gaseous attenuation along the space-Earth slant path (dB). Returns
            0 (zero) when the attenuation could not be calculated (see status value then for more 
            details).
        status (CalculationStatus): COMPLETED if Ag could be calculated successfully. Otherwise
            the status value indicates the reason for stopping calculations.
    """
    Re = 6371
    n_s = p676_13.refractive_index(hs_km, atm, rho0_gm3)
    n_e = p676_13.refractive_index(he_km, atm, rho0_gm3)
    phi_s_rad = radians(phis_deg)

    if phis_deg != -90 and phie_deg is not None and delta_phie_deg is not None:
        # Step 1
        # Note: The space station main beam is assumed to be directly pointing at the earth station
        #       (taking the effect of atmosphere into account).
        phi_ce_rad = acos(((Re+hs_km)*n_s)/((Re+he_km)*n_e)*cos(phi_s_rad))
        phi_ce_deg = degrees(phi_ce_rad) # incident elevation angle (i.e. the elevation angle at the
                                         # earth station from the incoming beam from the space
                                         # station)

        # Step 2
        # Check if the incoming beam falls within the vertical half-power beamwidth of the earth
        # station.
        is_within_beamwidth = (abs(phi_ce_deg-phie_deg) <= (delta_phie_deg/2))
        if is_within_beamwidth is False:
            return (0, CalculationStatus.OUTSIDE_VICTIMS_BEAMWIDTH)

    # Step 3, 4, 5, 6
    # also see Section 2.2.1 of Annex 1 from ITU-R P.676-13
    Ag = 0
    h_lower = he_km
    h_upper = hs_km
    (i_lower, i_upper) = p676_13._layer_indices(h_lower, h_upper) # pylint: disable=protected-access
    for i in range(i_lower, i_upper, 1):
        h_i_bot = p676_13._layer_bottom_height(i, i_lower, i_upper, h_lower, h_upper) # pylint: disable=protected-access
        delta_i = p676_13._layer_thickness(i, i_lower, i_upper, h_lower, h_upper) # pylint: disable=protected-access
        h_i_mid = h_i_bot+(delta_i/2)
        n_i = p676_13.refractive_index(h_i_mid, atm, rho0_gm3)

        if phis_deg != -90:
            # Step 3
            if cos(phi_s_rad) >= ((Re+h_i_bot)*n_i)/((Re+hs_km)*n_s):
                # see ITU-R P.676-13, Section 2.2.3 of Annex 1 regarding Earth surface intercepts
                return (0, CalculationStatus.DUCTING_OR_NO_LOS)

        r_i = Re + h_i_bot
        r_ip1 = r_i + delta_i
        r_s = Re + hs_km

        # Step 4
        x = (n_s/n_i)*r_s*cos(phi_s_rad)
        l_is = sqrt((r_ip1*r_ip1)-(x*x)) - sqrt((r_i*r_i)-(x*x))

        # Step 5
        T = p835_6.temperature(h_i_mid, atm)
        P = p835_6.pressure(h_i_mid, atm)
        rho = p835_6.water_vapour_density(h_i_mid, atm, rho0_gm3)
        e = rho*T/216.7 # water vapour pressure, in hPa
        Pdry = P - e # eq. (5) of P.453-14
        y_i = p676_13.gaseous_attenuation(f_ghz=f_ghz,
                                          # P.618 examples from CG-3M3J-13-ValEx-Rev8.3.0.xlsx
                                          # use dry pressure
                                          p_hpa=Pdry, t_k=T,  rho_gm3=rho)

        # Step 6
        Ag += l_is*y_i

    return (Ag, CalculationStatus.COMPLETED)


def earth_space_path_gaseous_attenuation(f_ghz: float, he_km: float, hs_km: float,
                                         phie_deg: float, phis_deg: float|None,
                                         delta_phis_deg: float|None,
                                         atm: p835_6.ReferenceAtmosphere=
                                            p835_6.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL,
                                         rho0_gm3: float=7.5
                                         ) -> tuple[float, CalculationStatus]:
    """
    ITU-R P.619-6, Attachment C to Annex 1 (C.5).

    Estimates the attenuation due to atmospheric gases along an Earth-space propagation paths
    (ascending ray). For an Earth-space propagation path, the antenna of the earth based station
    is the transmitting antenna.

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 1000. Gaseous attenuation can be ignored
            below 1 GHz.
        he_km (float): Height of Earth station (km above mean sea level), with 0 <= he_km < hs_km.
        hs_km (float): Height of space-based station (km above mean sea level),
            with 0 <= he_km < hs_km.
        phie_deg (float): Elevation angle of the main beam of the earth based station (degrees).
            0°=horizon, +90°=zenith, -90°=nadir.
        phis_deg (float or None): Elevation angle of the main beam of the space-based station
            antenna (degrees). If set to None, assumes the calculated elevation angle at the space
            station is within its half-power beamwidth. 0°=horizon, +90°=zenith, -90°=nadir.
        delta_phis_deg (float or None): Half-power beamwidth of the space-based station antenna
            (degrees). If set to None, assumes the calculated elevation angle at the space station
            is within its half-power beamwidth.
        atm (p835_6.ReferenceAtmosphere, optional): A reference atmosphere from ITU-R P.835-6.
            Default value is MEAN_ANNUAL_GLOBAL.
        rho0_gm3 (float, optional): Ground-level water vapour density (g/m3). Only applies when atm
            is set to MEAN_ANNUAL_GLOBAL. Default value is 7.5.

    Returns:
        Ag (float): The total gaseous attenuation along the Earth-space slant path (dB). Returns
            0 (zero) when the attenuation could not be calculated (see status value then for more 
            details).
        status (CalculationStatus): COMPLETED if Ag could be calculated successfully. Otherwise
            the status value indicates the reason for stopping calculations.
    """
    if phie_deg >= 0:
        # Case 1: Non-negative elevation angles (phi_e >= 0)
        Re = 6371
        phi_e_rad = radians(phie_deg)
        n_s = p676_13.refractive_index(hs_km, atm, rho0_gm3)
        n_e = p676_13.refractive_index(he_km, atm, rho0_gm3)

        # Step 1
        # Note: The earth station main beam is assumed to be directly pointing at the space station
        #       (taking the effect of atmosphere into account).
        phi_cs_rad = acos((((Re+he_km)*n_e)/((Re+hs_km)*n_s))*cos(phi_e_rad))
        phi_cs_deg = degrees(phi_cs_rad) # incident elevation angle (i.e. the elevation angle, at
                                         # the space station, from the incoming beam from the earth
                                         # station).

        # Step 2
        # Check if the incoming beam falls within the vertical half-power beamwidth of the space
        # station.
        if phie_deg != 90 and phis_deg is not None and delta_phis_deg is not None:
            is_within_beamwidth = (abs(phi_cs_deg-phis_deg) <= (delta_phis_deg/2))
            if is_within_beamwidth is False:
                return (0, CalculationStatus.OUTSIDE_VICTIMS_BEAMWIDTH)

        # Step 3, 4, 5, 6
        # also see Section 2.2.1 of Annex 1 from ITU-R P.676-13
        Ag = 0
        h_lower = he_km
        h_upper = hs_km
        (i_lower, i_upper) = p676_13._layer_indices(h_lower, h_upper) # pylint: disable=protected-access
        for i in range(i_lower, i_upper, 1):
            h_i_bot = p676_13._layer_bottom_height(i, i_lower, i_upper, h_lower, h_upper) # pylint: disable=protected-access
            delta_i = p676_13._layer_thickness(i, i_lower, i_upper, h_lower, h_upper) # pylint: disable=protected-access
            h_i_mid = h_i_bot+(delta_i/2)
            n_i = p676_13.refractive_index(h_i_mid, atm, rho0_gm3)

            if phie_deg != 90:
                # Step 3
                # Note: Seems like there is an error in the recommendation
                #       phi_s should not be used for the line-of-sight between antennas as it is
                #       pointing elev angle of the receive antenna at space. It may not point in
                #       the direction of the radio path.
                #
                # Could use phi_cs instead:
                # if cos(phi_cs_rad) >= ((Re+h_i_bot)*n_i)/((Re+Hs)*n_s):
                # Or, phi_e as proposed by P.B.:
                if cos(phi_e_rad) >= ((Re+h_i_bot)*n_i)/((Re+he_km)*n_e):
                    # see P.676-13, Section 2.2.3 of Annex 1 regarding Earth surface intercepts
                    return (0, CalculationStatus.DUCTING_OR_NO_LOS)

            r_i = Re + h_i_bot
            r_ip1 = r_i + delta_i
            r_e = Re + he_km

            # Step 4
            x = (n_e/n_i)*r_e*cos(phi_e_rad)
            l_ie = sqrt((r_ip1*r_ip1)-(x*x)) - sqrt((r_i*r_i)-(x*x))

            # Step 5
            T = p835_6.temperature(h_i_mid, atm)
            P = p835_6.pressure(h_i_mid, atm)
            rho = p835_6.water_vapour_density(h_i_mid, atm, rho0_gm3)
            e = rho*T/216.7 # water vapour pressure, in hPa
            Pdry = P - e # eq. (5) of P.453-14
            y_i = p676_13.gaseous_attenuation(f_ghz=f_ghz,
                                            # P.618 examples from CG-3M3J-13-ValEx-Rev8.3.0.xlsx
                                            # use dry pressure
                                            p_hpa=Pdry, t_k=T,  rho_gm3=rho)

            # Step 6
            Ag += l_ie*y_i

        return (Ag, CalculationStatus.COMPLETED)
    else:
        # Case 2: Negative elevation angles (phi_e < 0)
        Re = 6371
        phi_e_rad = radians(phie_deg)
        H0 = 0
        H1 = he_km
        Hmin = ((H1-H0)/2)+H0
        for _ in range (1, 24):
            parallelism_test = ( ((Re+Hmin)*p676_13.refractive_index(Hmin, atm, rho0_gm3)) -
                                 ((Re+he_km)*p676_13.refractive_index(he_km, atm, rho0_gm3) *
                                  cos(phi_e_rad)) )
            if parallelism_test > 0:
                H1 = Hmin
            else:
                H0 = Hmin
            Hmin = ((H1-H0)/2)+H0

        Ag1, status1 = earth_space_path_gaseous_attenuation(f_ghz=f_ghz, he_km=Hmin, hs_km=he_km,
                           phie_deg=0, phis_deg=None, delta_phis_deg=None, atm=atm,
                           rho0_gm3=rho0_gm3)

        Ag2, status2 = earth_space_path_gaseous_attenuation(f_ghz=f_ghz, he_km=Hmin, hs_km=hs_km,
                           phie_deg=0, phis_deg=phis_deg, delta_phis_deg=delta_phis_deg, atm=atm,
                           rho0_gm3=rho0_gm3)

        if status1 == CalculationStatus.COMPLETED and status2 == CalculationStatus.COMPLETED:
            return (Ag1+Ag2, CalculationStatus.COMPLETED)
        elif status1 != CalculationStatus.COMPLETED:
            return (0, status1)
        else:
            return (0, status2)


def tropospheric_scintillation_attenuation(f_ghz: float, theta_deg: float, p_percent: float,
                                           lat: float, lon: float, d_m: float, eta: float=0.5,
                                           ga_dbi: float|None=None) -> float:
    """
    ITU-R P.619-6, Attachment D to Annex 1.

    Estimates the tropospheric scintillation attenuation (applies to a single path between one
    transmitter and one receiver).

    Args:
        f_ghz (float): Frequency (GHz), with f_ghz <= 100.
        theta_deg (float): Free-space elevation angle (degrees), with 5 <= theta_deg <= 90.
        p_percent (float): Time percentage, with 0.001 <= p <= 99.999.
        lat (float): Latitude (degrees), with -90 <= lat <= 90. Latitude and longitude values are
            utilized to obtain Nwet, the median value of the wet term of the surface refractivity
            exceeded for the average year, from the digital maps in Recommendation ITU-R P.453-14.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        d_m (float): Physical diameter of the earth-station antenna (meters).
        eta (float, optional): Antenna efficiency; if unknown, 0.5 is a conservative estimate.
            Default value is 0.5.
        ga_dbi (float or None, optional): Antenna gain of the earth-based antenna, in the direction
            of the path (dBi).  If specified, d_m and eta are unused.

    Returns:
        Ast (float): Tropospheric scintillation attenuation not exceeded for p percent time (dB).
            Can be positive (attenuation) or negative (enhancement).
    """
    nwet_ppm = p453_14.median_annual_nwet(lat, lon)
    return _tropospheric_scintillation_attenuation(f_ghz, theta_deg, p_percent, nwet_ppm, d_m, eta,
                                                   ga_dbi)


def _tropospheric_scintillation_attenuation(f_ghz: float, theta_deg: float, p_percent: float,
                                            nwet_ppm: float, d_m: float, eta: float=0.5,
                                            ga_dbi: float|None=None) -> float:
    """
    ITU-R P.619-6, Attachment D to Annex 1.

    Estimates the tropospheric scintillation attenuation (applies to a single path between one
    transmitter and one receiver).

    Args:
        f_ghz (float): Frequency (GHz), with f_ghz <= 100.
        theta_deg (float): Free-space elevation angle (degrees), with 5 <= theta_deg <= 90.
        p_percent (float): Time percentage, with 0.001 <= p <= 99.999.
        nwet_ppm (float): The median value of the wet term of the surface refractivity exceeded for
            the average year (ppm).
        d_m (float): Physical diameter of the earth-station antenna (meters).
        eta (float, optional): Antenna efficiency; if unknown, 0.5 is a conservative estimate.
            Default value is 0.5.
        ga_dbi (float or None, optional): Antenna gain of the earth-based antenna, in the direction
            of the path (dBi).  If specified, d_m and eta are unused.

    Returns:
        Ast (float): Tropospheric scintillation attenuation not exceeded for p percent time (dB).
            Can be positive (attenuation) or negative (enhancement).
    """
    if ga_dbi is not None:
        Deff = 0.3*(10**(0.05*ga_dbi))/(pi*f_ghz)
    else:
        eta = 0.5
        Deff = sqrt(eta)*d_m

    # see ITU-R P.618-14, Annex 1, Section 2.4.1
    sigma_ref = 3.6E-3 + (1E-4*nwet_ppm)
    theta0_rad = radians(theta_deg)
    sin_theta0 = sin(theta0_rad)
    L = 2000/(sqrt((sin_theta0*sin_theta0)+2.35E-4)+sin_theta0)
    x = 1.22*Deff*Deff*(f_ghz/L)
    sqrt_arg = (3.86*pow((x*x)+1,11/12)*sin((11/6)*atan2(1,x)))-(7.08*pow(x,5/6))
    if sqrt_arg < 0:
        return 0
    g_x = sqrt(sqrt_arg)
    sigma_st = sigma_ref*pow(f_ghz,7/12)*g_x/pow(sin_theta0,1.2)

    if p_percent <= 50:
        log_p = log10(p_percent)
        a_ste = 2.672 - (1.258*log_p) - (0.0835*log_p*log_p) - (0.0597*log_p*log_p*log_p)
        Ast = -sigma_st*a_ste
    else:
        log_q = log10(100-p_percent)
        a_stf = 3.0 - (1.71*log_q) + (0.072*log_q*log_q) - (0.061*log_q*log_q*log_q)
        Ast = sigma_st*a_stf

    return Ast


def ray_heights(he_km: float, theta_deg: float, deltad_km: float=1
                ) -> tuple[list[float], list[float]]:
    """
    ITU-R P.619-6, Attachment E to Annex 1.

    Provides a method for tracing a ray launched from an earth-based station, in order to test
    whether it encounters an obstruction. It can be used to compile a profile of ray height
    relative to sea level, which can then be compared with a terrain profile.
    
    Args:
        he_km (float): Altitude of earth-based station (km above sea level).
        theta_deg (float): Apparent elevation angle at the earth-based station (degrees). 
            0°=horizon, +90°=zenith, -90°=nadir.
        deltad_km (float, optional): Increment in horizontal distance over curved Earth (km).

    Returns:
        Dc_list (list[float]): Horizontal distances over curved earth from the earth-based
            station (km).
        Hr_list (list[float]): Ray heights over sea level (km).
    """
    Ht = he_km
    Hr = Ht # ray altitude (km above sea level)
    Dc = 0 # horizontal distance over curved Earth (km)
    epsilon = radians(theta_deg) # ray elevation angle above local horizontal (radians)
    Re = 6371 # average Earth radius (km)

    Dc_list = []
    Hr_list = []

    if theta_deg <= 5:
        while Hr <= 10:
            Dc_list.append(Dc)
            Hr_list.append(Hr)
            delta_eps = deltad_km * ((1/Re) - 4.28715E-5 * exp(-Hr/7.348))
            Hr = Hr + (deltad_km*epsilon)
            epsilon = epsilon + delta_eps
            Dc = Dc + deltad_km
    else:
        tan_theta = tan(radians(theta_deg))
        while Hr <= 10:
            Dc_list.append(Dc)
            Hr_list.append(Hr)
            Dc = Dc + deltad_km
            d = Dc
            Hr = Ht + (d*tan_theta) + ((d*d)/(2*Re))

    return (Dc_list, Hr_list)


def unwanted_rain_scattering_power(r1_m: float, r2_m: float, unwcyl: int, theta_deg: float,
                                   rrain_mmh: float, f_ghz: float, peirp_dbw: float, dtx_km: float,
                                   drx_km: float, el_deg: float, tau_deg: float,
                                   p_hpa: float=1013.25, t_k: float=288.15, rho_gm3: float=7.5
                                   ) -> float:
    """
    ITU-R P.619-6, Attachment F to Annex 1.

    Provides a simple test which estimates the power received due to rain scattering in a common
    volume between two cylindrical antenna beams for [the specifed] rain rate (mm/hr). The test
    estimates the unwanted rain-scattered power received by the victim receiver exceeded for a
    given percentage time p.
    
    Args:
        r1_m (float): Radius of cylinder representing the first antenna beam (meters),
            with r1 <= r2.
        r2_m (float): Radius of cylinder representing the second antenna beam (meters),
            with r1 <= r2.
        unwcyl (int): Cylinder representing the unwanted beam. Should be set to either 1 or 2.
        theta_deg (float): Scatter angle (degrees), with 10 <= theta_deg <= 90. The angle between
            the direction of propagation of the incoming power in one cylinder and the scattered
            power travelling towards the victim receiver.
        rrain_mmh (float): Point rainfall rate in mm/h for a 1 minute integration time exceeded for
            p% time.
        f_ghz (float): Frequency (GHz), with f_ghz <= 100.
        peirp_dbw (float): E.i.r.p. of the unwanted transmitter in dBW.
        dtx_km (float): Distance from the unwanted transmitter to the common volume (km).
        drx_km (float): Distance in km of the interfered-with antenna from the common volume
            represented by the cylinders.
        el_deg (float): The path elevation angle (degrees), for the calculation of regression
            coefficients given by Recommendation ITU-R P.838-3.
        tau_deg (float): The polarization tilt angle relative to the horizontal (degrees), for the
            calculation of regression coefficients given by Recommendation ITU-R P.838-3.
        p_hpa (float, optional): Atmospheric pressure (hPa). Default value is 1013.25.
        t_k (float, optional): Temperature, in Kelvins. Default value is 288.15.
        rho_gm3 (float, optional): Water vapour density (g/m3). Default value is 7.5.

    Returns:
        Ptxs (float): An estimate of the unwanted scattered power, in dBW. A full rain-scatter
            calculation should be conducted if Pint - Ptxs < 20 dB, where Pint is the receiver's
            interference threshold.
    """
    theta_rad = radians(theta_deg)

    # Step 1
    L1 = 2*r2_m/sin(theta_rad)
    L2 = max(L1*cos(theta_rad), 2*r1_m*sin(theta_rad))

    # Step 2
    gamma_g = p676_13.gaseous_attenuation(f_ghz=f_ghz, p_hpa=p_hpa, t_k=t_k, rho_gm3=rho_gm3)
    S = peirp_dbw - (20*log10(dtx_km)) - (gamma_g*dtx_km) - 71.0

    # Step 3
    if unwcyl == 1:
        Pin = S + 10*log10(pi*r1_m*r1_m)
    else:
        Pin = S + 10*log10(pi*r2_m*r2_m)

    # Step 4
    k, alpha = p838_3.coefficients(f_ghz, el_deg, tau_deg)
    gamma_r = k*(rrain_mmh**alpha)
    if unwcyl == 1:
        Pout = Pin - 0.001*gamma_r*L1
    else:
        Pout = Pin - 0.001*gamma_r*L2

    # Step 5
    Pscat = 10*log10(10**(0.1*Pin) - 10**(0.1*Pout))

    # Step 6
    if unwcyl == 1:
        Peirp_s = Pscat
    else:
        Peirp_s = Pscat - 10*log10((r2_m*r2_m*L2)/(r1_m*r1_m*L1))

    # Step 7
    if f_ghz > 10:
        Fnis = 0.001*(rrain_mmh**0.4)*cos(theta_rad)*(2*(f_ghz-10)**1.6 - 2.5*(f_ghz-10)**1.7)
    else:
        Fnis = 0

    # Step 8
    Ptxs = Peirp_s + Fnis - (20*log10(drx_km*f_ghz)) - (gamma_g*drx_km) - 92.4

    return Ptxs
