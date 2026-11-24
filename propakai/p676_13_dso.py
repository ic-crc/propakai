# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.676-13, dynamic shared object version (i.e. using a compiled binary).

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite this software
    package along with the underlying ITU-R standard:

    * **ITU-R Standard:** International Telecommunication Union (2022).
      *Recommendation ITU-R P.676-13: Attenuation by atmospheric gases and related effects*.
      Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.676/en

Note: Monthly Digital Maps Usage
    Unlike the Python implementation (`p676_13`), this module does not automatically
    download monthly data when missing. Use `download_monthly_data()` to fetch it when needed.
"""

from types import SimpleNamespace
import ctypes as ct
from propakai import _bin_utils as _bu
from propakai import p835_6
from propakai.p1511_3 import _download_rec_data as _download_p1511_data
from propakai.p2145_0 import _download_annual_rec_data as _download_p2145_annual_data
from propakai.p2145_0 import _download_monthly_rec_data as _download_p2145_monthly_data
from propakai.p676_13 import _download_rec_data as _download_p676_coeffs


__all__ = ['gaseous_attenuation',
           'dry_air_gaseous_attenuation',
           'water_vapour_gaseous_attenuation',
           'slant_path_gaseous_attenuation',
           'space_based_station_apparent_elev_angle',
           'earth_based_station_apparent_elev_angle',
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
           'weibull_approximation',
           'download_monthly_data']


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
    return _p676_13_dso_shared.cdll.P676_13_GaseousAttenuation(f_ghz, p_hpa, t_k, rho_gm3)


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
    return _p676_13_dso_shared.cdll.P676_13_DryAirGaseousAttenuation(f_ghz, p_hpa, t_k, rho_gm3)


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
    return _p676_13_dso_shared.cdll.P676_13_WaterVapourGaseousAttenuation(f_ghz, p_hpa, t_k,
                                                                          rho_gm3)


def slant_path_gaseous_attenuation(f_ghz: float, h1_km: float, h2_km: float, phi1_deg: float,
                                   atm: p835_6.ReferenceAtmosphere=
                                       p835_6.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL,
                                   rho0_gm3: float=7.5) -> float:
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
    """
    return _p676_13_dso_shared.cdll.P676_13_SlantPathGaseousAttenuation(f_ghz, h1_km, h2_km,
                                                                phi1_deg, atm.value, rho0_gm3)


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
    return _p676_13_dso_shared.cdll.P676_13_SpaceBasedStationApparentElevAngle(he_km, hs_km,
                                                                phie_deg, atm.value, rho0_gm3)


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
    return _p676_13_dso_shared.cdll.P676_13_EarthBasedStationApparentElevAngle(he_km, hs_km,
                                                                    phis_deg, atm.value, rho0_gm3)


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
    return _p676_13_dso_shared.cdll.P676_13_PhaseDispersion(f_ghz, p_hpa, t_k, rho_gm3)


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
    return _p676_13_dso_shared.cdll.P676_13_DownwellingMicrowaveBrightnessTemperature(f_ghz,
                                                phi1_deg, h1_km, hk_km, atm.value, rho0_gm3)


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
    return _p676_13_dso_shared.cdll.P676_13_UpwellingMicrowaveBrightnessTemperature(f_ghz, phi1_deg,
                                           h1_km, hk_km, atm.value, rho0_gm3, emissivity, t_earth_k)


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
    return _p676_13_dso_shared.cdll.P676_13_SlantPathInstantOxygenGaseousAtt(f_ghz, theta_deg,
                                                                      ps_hpa, ts_k, rhows_gm3)


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
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return _p676_13_dso_shared.cdll.P676_13_SlantPathStatisticalOxygenGaseousAtt(f_ghz, theta_deg,
                                                              p_percent, lat, lon, month, h_mamsl)


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
    return _p676_13_dso_shared.cdll.P676_13_SlantPathInstantWaterVapourGaseousAtt1(f_ghz, theta_deg,
                                                                            ps_hpa, ts_k, rhows_gm3)


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
    return _p676_13_dso_shared.cdll.P676_13_SlantPathInstantWaterVapourGaseousAtt2(f_ghz, theta_deg,
                                                                   ps_hpa, ts_k, rhows_gm3, vs_kgm2)


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
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return _p676_13_dso_shared.cdll.P676_13_SlantPathStatisticalWaterVapourGaseousAtt(f_ghz,
                                             theta_deg, p_percent, lat, lon, month, h_mamsl)


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
    if vs_kgm2 is None:
        vs_kgm2 = float('nan')
    return _p676_13_dso_shared.cdll.P676_13_SlantPathInstantGaseousAttenuation(f_ghz, theta_deg,
                                                                ps_hpa, ts_k, rhows_gm3, vs_kgm2)


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
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return _p676_13_dso_shared.cdll.P676_13_SlantPathStatisticalGaseousAttenuation(f_ghz, theta_deg,
                                                                p_percent, lat, lon, month, h_mamsl)


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
    if h_mamsl is None:
        h_mamsl = float('nan')
    return _p676_13_dso_shared.cdll.P676_13_WeibullApproximation(f_ghz, theta_deg, p_percent, lat,
                                                                 lon, h_mamsl)


def download_monthly_data(month: int, warn_if_already_installed: bool=False) -> None:
    """
    Downloads and installs ITU-R P.2145-0's digital maps for the specified month, unless they are
    already installed.
    
    Args:
        month (int): Month (1=Jan, ..., 12=Dec).
        warn_if_already_installed (bool, optional): Whether to print message when maps are already
            installed for the specified month. Default value is False.
    """
    _download_p2145_monthly_data(month, warn_if_already_installed)


def _init_dynamic_library() -> ct.CDLL:
    lib = _bu.get_dynamic_library('propakai_cpp')
    _set_args_and_return_ctypes(lib)
    _download_p676_coeffs(warn_if_already_installed=False)
    _download_p1511_data(warn_if_already_installed=False)
    _download_p2145_annual_data(warn_if_already_installed=False)
    # leave monthly data to be installed as needed via download_monthly_data()
    return lib


def _set_args_and_return_ctypes(lib):
    lib.P676_13_GaseousAttenuation.argtypes = [ct.c_double, ct.c_double, ct.c_double, ct.c_double]
    lib.P676_13_GaseousAttenuation.restype = ct.c_double

    lib.P676_13_DryAirGaseousAttenuation.argtypes = [ct.c_double, ct.c_double, ct.c_double,
                                                     ct.c_double]
    lib.P676_13_DryAirGaseousAttenuation.restype = ct.c_double

    lib.P676_13_WaterVapourGaseousAttenuation.argtypes = [ct.c_double, ct.c_double, ct.c_double,
                                                          ct.c_double]
    lib.P676_13_WaterVapourGaseousAttenuation.restype = ct.c_double

    lib.P676_13_SlantPathGaseousAttenuation.argtypes = [ct.c_double, ct.c_double, ct.c_double,
                                                        ct.c_double, ct.c_int, ct.c_double]
    lib.P676_13_SlantPathGaseousAttenuation.restype = ct.c_double

    lib.P676_13_SpaceBasedStationApparentElevAngle.argtypes = [ct.c_double, ct.c_double,
                                                               ct.c_double, ct.c_int, ct.c_double]
    lib.P676_13_SpaceBasedStationApparentElevAngle.restype = ct.c_double

    lib.P676_13_EarthBasedStationApparentElevAngle.argtypes = [ct.c_double, ct.c_double,
                                                               ct.c_double, ct.c_int, ct.c_double]
    lib.P676_13_EarthBasedStationApparentElevAngle.restype = ct.c_double

    lib.P676_13_PhaseDispersion.argtypes = [ct.c_double, ct.c_double, ct.c_double, ct.c_double]
    lib.P676_13_PhaseDispersion.restype = ct.c_double

    lib.P676_13_DownwellingMicrowaveBrightnessTemperature.argtypes = [ct.c_double, ct.c_double,
                                                ct.c_double, ct.c_double, ct.c_int, ct.c_double]
    lib.P676_13_DownwellingMicrowaveBrightnessTemperature.restype = ct.c_double

    lib.P676_13_UpwellingMicrowaveBrightnessTemperature.argtypes = [ct.c_double, ct.c_double,
                    ct.c_double, ct.c_double, ct.c_int, ct.c_double, ct.c_double, ct.c_double]
    lib.P676_13_UpwellingMicrowaveBrightnessTemperature.restype = ct.c_double

    lib.P676_13_SlantPathInstantOxygenGaseousAtt.argtypes = [ct.c_double, ct.c_double, ct.c_double,
                                                             ct.c_double, ct.c_double]
    lib.P676_13_SlantPathInstantOxygenGaseousAtt.restype = ct.c_double

    lib.P676_13_SlantPathStatisticalOxygenGaseousAtt.argtypes = [ct.c_double, ct.c_double,
                             ct.c_double, ct.c_double, ct.c_double, ct.c_int, ct.c_double]
    lib.P676_13_SlantPathStatisticalOxygenGaseousAtt.restype = ct.c_double

    lib.P676_13_SlantPathInstantWaterVapourGaseousAtt1.argtypes = [ct.c_double, ct.c_double,
                                                      ct.c_double, ct.c_double, ct.c_double]
    lib.P676_13_SlantPathInstantWaterVapourGaseousAtt1.restype = ct.c_double

    lib.P676_13_SlantPathInstantWaterVapourGaseousAtt2.argtypes = [ct.c_double, ct.c_double,
                                         ct.c_double, ct.c_double, ct.c_double, ct.c_double]
    lib.P676_13_SlantPathInstantWaterVapourGaseousAtt2.restype = ct.c_double

    lib.P676_13_SlantPathStatisticalWaterVapourGaseousAtt.argtypes = [ct.c_double, ct.c_double,
                                  ct.c_double, ct.c_double, ct.c_double, ct.c_int, ct.c_double]
    lib.P676_13_SlantPathStatisticalWaterVapourGaseousAtt.restype = ct.c_double

    lib.P676_13_SlantPathInstantGaseousAttenuation.argtypes = [ct.c_double, ct.c_double,
                                     ct.c_double, ct.c_double, ct.c_double, ct.c_double]
    lib.P676_13_SlantPathInstantGaseousAttenuation.restype = ct.c_double

    lib.P676_13_SlantPathStatisticalGaseousAttenuation.argtypes = [ct.c_double, ct.c_double,
                               ct.c_double, ct.c_double, ct.c_double, ct.c_int, ct.c_double]
    lib.P676_13_SlantPathStatisticalGaseousAttenuation.restype = ct.c_double

    lib.P676_13_WeibullApproximation.argtypes = [ct.c_double, ct.c_double, ct.c_double, ct.c_double,
                                                 ct.c_double, ct.c_double]
    lib.P676_13_WeibullApproximation.restype = ct.c_double


_p676_13_dso_shared = SimpleNamespace(
    cdll = _init_dynamic_library()
)
