# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.840-9, dynamic shared object version (i.e. using a compiled binary).

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite this software
    package along with the underlying ITU-R standard:

    * **ITU-R Standard:** International Telecommunication Union (2023).
      *Recommendation ITU-R P.840-9: Attenuation due to clouds and fog*. Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.840/en

Note: Monthly Digital Maps Usage
    Unlike the Python implementation (`p840_9`), this module does not automatically
    download monthly data when missing. Use `download_monthly_data()` to fetch it when needed.
"""

import ctypes as ct
from propakai import _bin_utils as _bu
from propakai.p840_9 import _download_annual_rec_data, _download_monthly_rec_data


__all__ = ['cloud_or_fog_attenuation',
           'cloud_liquid_water_attenuation_coefficient',
           'slant_path_instantaneous_cloud_attenuation',
           'slant_path_statistical_cloud_attenuation',
           'log_normal_approx_to_stat_cloud_attenuation',
           'integrated_cloud_liquid_water_content',
           'mean_integrated_cloud_liquid_water_content',
           'std_dev_integrated_cloud_liquid_water_content',
           'download_monthly_data']


def cloud_or_fog_attenuation(f_ghz, t_k, rhol_gm3) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 1.

    Gets the specific attenuation within a cloud or fog (dB/km).
    
    "At frequencies of the order of 100 GHz and above, attenuation due to fog may be significant".

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 200.
        t_k (float): Liquid water temperature (K).
        rhol_gm3 (float): Liquid water density in the cloud or fog (g/m3). "Typically about 0.05
            g/m3 for medium fog (visibility of the order of 300 m) and 0.5 g/m3 for thick fog
            (visibility of the order of 50 m)."

    Returns:
        gamma_c (float): Specific attenuation (dB/km) within cloud or fog.
    """
    cdll = _p840_9_dso_shared['cdll']
    return cdll.P840_9_CloudOrFogAttenuation(f_ghz, t_k, rhol_gm3)


def cloud_liquid_water_attenuation_coefficient(f_ghz, t_k) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 2.

    Gets the cloud liquid water specific attenuation coefficient (dB/km)/(g/m3).

    Args:
        f_ghz (float): Frequency (GHz), with 1 <= f_ghz <= 200.
        t_k (float): Liquid water temperature (K).
    
    Returns:
        Kl (float): The cloud liquid water specific attenuation coefficient (dB/km)/(g/m3).
    """
    cdll = _p840_9_dso_shared['cdll']
    return cdll.P840_9_CloudLiquidWaterAttenuationCoefficient(f_ghz, t_k)


def slant_path_instantaneous_cloud_attenuation(f_ghz: float, theta_deg: float, l_kgm2: float
                                               ) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 3.1.

    Gets the predicted slant path instantaneous cloud attenuation (dB).

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 200.
        theta_deg (float): Elevation angle (degrees).
        l_kgm2 (float): Integrated cloud liquid water content, in kg/m2 or mm, from the surface
            of the Earth at the desired location.

    Returns:
        Ac (float): The predicted slant path instantaneous cloud attenuation (dB).
    """
    cdll = _p840_9_dso_shared['cdll']
    return cdll.P840_9_SlantPathInstantaneousCloudAttenuation(f_ghz, theta_deg, l_kgm2)


def slant_path_statistical_cloud_attenuation(f_ghz: float, theta_deg: float, p_percent: float,
                                             lat: float, lon: float, month: int|None=None
                                             ) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 3.2.

    Gets the predicted slant path statistical cloud attenuation (dB).

    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 200.
        theta_deg (float): Elevation angle (degrees).
        p_percent (float): Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent
            <= 100 for annual statistics and with 0.1 <= p_percent <= 100 for monthly statistics.
        lat (float): Latitude of the desired location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (degrees), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.

    Returns:
        Ac (float): The predicted slant path statistical cloud attenuation (dB).
    """
    cdll = _p840_9_dso_shared['cdll']
    if month is None:
        month = -1
    return cdll.P840_9_SlantPathStatisticalCloudAttenuation(f_ghz, theta_deg, p_percent, lat, lon,
                                                            month)


def log_normal_approx_to_stat_cloud_attenuation(f_ghz: float, theta_deg: float, p_percent: float,
                                                lat: float, lon: float) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 3.3.

    Gets the log-normal approximation to the predicted slant path statistical cloud
    attenuation (dB). Uses annual statistics.
    
    Args:
        f_ghz (float): Frequency of interest (GHz), with 1 <= f_ghz <= 200.
        theta_deg (float): Elevation angle (degrees).
        p_percent (float): Exceedance probability (CCDF) of interest, in %,
            with 0.01 <= p_percent <= 100.
        lat (float): Latitude of the desired location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (degrees), with -180 <= lon <= 180.

    Returns:
        Ac (float): The log-normal approximation to the predicted slant path statistical cloud
            attenuation (dB).
    """
    cdll = _p840_9_dso_shared['cdll']
    return cdll.P840_9_LogNormalApproxToStatCloudAttenuation(f_ghz, theta_deg, p_percent, lat, lon)


def integrated_cloud_liquid_water_content(p_percent: float, lat: float, lon: float,
                                          month: int|None=None) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 4.

    Gets the integrated cloud liquid water content for the provided exceedance probability, in
    kg/m2, or, equivalently, mm.

    Args:
        p_percent (float): Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent
            <= 100 for annual statistics and with 0.1 <= p_percent <= 100 for monthly statistics.
        lat (float): Latitude of the desired location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (degrees), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.

    Returns:
        L (float): The integrated cloud liquid water content in kg/m2, or, equivalently, mm.
    """
    cdll = _p840_9_dso_shared['cdll']
    if month is None:
        month = -1
    return cdll.P840_9_IntegratedCloudLiquidWaterContent(p_percent, lat, lon, month)


def mean_integrated_cloud_liquid_water_content(lat: float, lon: float, month:int|None=None
                                               ) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 4.

    Gets the mean of the integrated cloud liquid water content.

    Args:
        lat (float): Latitude of the desired location (degrees), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (degrees), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.

    Returns:
        L_mean (float): The mean of the integrated cloud liquid water content.
    """
    cdll = _p840_9_dso_shared['cdll']
    if month is None:
        month = -1
    return cdll.P840_9_MeanIntegratedCloudLiquidWaterContent(lat, lon, month)


def std_dev_integrated_cloud_liquid_water_content(lat: float, lon: float, month:int|None=None
                                                  ) -> float:
    """
    ITU-R P.840-9, Annex 1, Section 4.

    Gets the standard deviation of the integrated cloud liquid water content.

    Args:
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.

    Returns:
        L_std (float): The standard deviation of the integrated cloud liquid water content.
    """
    cdll = _p840_9_dso_shared['cdll']
    if month is None:
        month = -1
    return cdll.P840_9_StdDevIntegratedCloudLiquidWaterContent(lat, lon, month)


def download_monthly_data(month: int, warn_if_already_installed: bool=False) -> None:
    """
    Downloads and installs the recommendation's digital maps for the specified month, unless they
    are already installed.
    
    Args:
        month (int): Month (1=Jan, ..., 12=Dec).
        warn_if_already_installed (bool, optional): Whether to print message when maps are already
            installed for the specified month. Default value is False.
    """
    _download_monthly_rec_data(month, warn_if_already_installed)


def _init_dynamic_library() -> ct.CDLL:
    lib = _bu.get_dynamic_library('propakai_cpp')
    _set_args_and_return_ctypes(lib)
    # make sure annual digital maps are installed
    _download_annual_rec_data(warn_if_already_installed=False)
    return lib


def _set_args_and_return_ctypes(lib):
    lib.P840_9_CloudOrFogAttenuation.argtypes = [ct.c_double, ct.c_double, ct.c_double]
    lib.P840_9_CloudOrFogAttenuation.restype = ct.c_double

    lib.P840_9_CloudLiquidWaterAttenuationCoefficient.argtypes = [ct.c_double, ct.c_double]
    lib.P840_9_CloudLiquidWaterAttenuationCoefficient.restype = ct.c_double

    lib.P840_9_SlantPathInstantaneousCloudAttenuation.argtypes = [ct.c_double, ct.c_double,
                                                                  ct.c_double]
    lib.P840_9_SlantPathInstantaneousCloudAttenuation.restype = ct.c_double

    lib.P840_9_SlantPathStatisticalCloudAttenuation.argtypes = [ct.c_double, ct.c_double,
                                            ct.c_double, ct.c_double, ct.c_double, ct.c_int]
    lib.P840_9_SlantPathStatisticalCloudAttenuation.restype = ct.c_double

    lib.P840_9_LogNormalApproxToStatCloudAttenuation.argtypes = [ct.c_double, ct.c_double,
                                                    ct.c_double, ct.c_double, ct.c_double]
    lib.P840_9_LogNormalApproxToStatCloudAttenuation.restype = ct.c_double

    lib.P840_9_IntegratedCloudLiquidWaterContent.argtypes = [ct.c_double, ct.c_double, ct.c_double,
                                                             ct.c_int]
    lib.P840_9_IntegratedCloudLiquidWaterContent.restype = ct.c_double

    lib.P840_9_MeanIntegratedCloudLiquidWaterContent.argtypes = [ct.c_double, ct.c_double, ct.c_int]
    lib.P840_9_MeanIntegratedCloudLiquidWaterContent.restype = ct.c_double

    lib.P840_9_StdDevIntegratedCloudLiquidWaterContent.argtypes = [ct.c_double, ct.c_double,
                                                                   ct.c_int]
    lib.P840_9_StdDevIntegratedCloudLiquidWaterContent.restype = ct.c_double


_p840_9_dso_shared = {
    'cdll': _init_dynamic_library()
}
