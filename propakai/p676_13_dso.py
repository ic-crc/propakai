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
"""

from types import SimpleNamespace
import ctypes as ct
from propakai import _bin_utils as _bu
from propakai import p835_6


__all__ = ['gaseous_attenuation',
           'dry_air_gaseous_attenuation',
           'water_vapour_gaseous_attenuation',
           'slant_path_gaseous_attenuation']


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
                                                                    phie_deg, atm, rho0_gm3)


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
                                                                    phis_deg, atm, rho0_gm3)


def _init_dynamic_library() -> ct.CDLL:
    lib = _bu.get_dynamic_library('propakai_cpp')
    _set_args_and_return_ctypes(lib)
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


_p676_13_dso_shared = SimpleNamespace(
    cdll = _init_dynamic_library()
)
