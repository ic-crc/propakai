# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.2145-0, dynamic shared object version (i.e. using a compiled binary).

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite this software
    package along with the underlying ITU-R standard:

    * **ITU-R Standard:** International Telecommunication Union (2022).
      *Recommendation ITU-R P.2145-0: Digital maps related to the calculation of gaseous attenuation
      and related effects*. Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.2145/en

Note: Monthly Digital Maps Usage
    Unlike the Python implementation (`p2145_0`), this module does not automatically
    download monthly data when missing. Use `download_monthly_data()` to fetch it when needed.
"""

import ctypes as ct
from propakai import _bin_utils as _bu
from propakai.p2145_0 import _download_annual_rec_data, _download_monthly_rec_data


__all__ = ['surface_total_pressure',
           'surface_temperature',
           'surface_water_vapour_density',
           'integrated_water_vapour_content',
           'mean_surface_total_pressure',
           'mean_surface_temperature',
           'mean_surface_water_vapour_density',
           'mean_integrated_water_vapour_content',
           'std_dev_surface_total_pressure',
           'std_dev_surface_temperature',
           'std_dev_surface_water_vapour_density',
           'std_dev_integrated_water_vapour_content',
           'weibull_parameters',
           'download_monthly_data']


def surface_total_pressure(p_percent: float, lat: float, lon: float, month: int|None=None,
                           h_mamsl: float|None=None) -> float:
    """
    ITU-R P.2145-0, Section 2.1 of Annex.

    Gets the surface total (barometric) pressure (hPa) for the specified exceedence probabiliby
    p_percent (CCDF - complementary cumulative distribution function) at the specified location on
    the surface of the Earth.
    
    Args:
        p_percent (float): Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent
            <= 99 for annual statistics and with 0.1 <= p_percent <= 99 for monthly statistics.
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511. Default value is None.

    Returns:
        P (float): The surface total (barometric) pressure (hPa) for the specified exceedence
            probabiliby p_percent (CCDF) at the specified location on the surface of the Earth.
    """
    cdll = _p2145_0_dso_shared['cdll']
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return cdll.P2145_0_SurfaceTotalPressure(p_percent, lat, lon, month, h_mamsl)


def surface_temperature(p_percent: float, lat: float, lon: float, month: int|None=None,
                        h_mamsl: float|None=None) -> float:
    """
    ITU-R P.2145-0, Section 2.1 of Annex.

    Gets the surface temperature (K) for the specified exceedence probabiliby p_percent (CCDF - 
    complementary cumulative distribution function) at the specified location on the surface of the
    Earth.
    
    Args:
        p_percent (float): Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent
            <= 99 for annual statistics and with 0.1 <= p_percent <= 99 for monthly statistics.
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511. Default value is None.

    Returns:
        T (float): The surface temperature (K) for the specified exceedence probabiliby p_percent
            (CCDF) at the specified location on the surface of the Earth.
    """
    cdll = _p2145_0_dso_shared['cdll']
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return cdll.P2145_0_SurfaceTemperature(p_percent, lat, lon, month, h_mamsl)


def surface_water_vapour_density(p_percent: float, lat: float, lon: float, month: int|None=None,
                                 h_mamsl: float|None=None) -> float:
    """
    ITU-R P.2145-0, Section 2.1 of Annex.

    Gets the surface water vapour density (g/m3) for the specified exceedence probabiliby p_percent
    (CCDF - complementary cumulative distribution function) at the specified location on the
    surface of the Earth.
    
    Args:
        p_percent (float): Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent
            <= 99 for annual statistics and with 0.1 <= p_percent <= 99 for monthly statistics.
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511. Default value is None.

    Returns:
        rho (float): The surface water vapour density (g/m3) for the specified exceedence
            probabiliby p_percent (CCDF) at the specified location on the surface of the Earth.
    """
    cdll = _p2145_0_dso_shared['cdll']
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return cdll.P2145_0_SurfaceWaterVapourDensity(p_percent, lat, lon, month, h_mamsl)


def integrated_water_vapour_content(p_percent: float, lat: float, lon: float, month: int|None=None,
                                    h_mamsl: float|None=None) -> float:
    """
    ITU-R P.2145-0, Section 2.1 of Annex.

    Gets the integrated water vapour content (kg/m2) for the specified exceedence probabiliby
    p_percent (CCDF - complementary cumulative distribution function) at the specified location on
    the surface of the Earth.
    
    Args:
        p_percent (float): Exceedance probability (CCDF) of interest, in %, with 0.01 <= p_percent
            <= 99 for annual statistics and with 0.1 <= p_percent <= 99 for monthly statistics.
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511. Default value is None.

    Returns:
        V (float): The integrated water vapour content (kg/m2) for the specified exceedence
            probabiliby p_percent (CCDF) at the specified location on the surface of the Earth.
    """
    cdll = _p2145_0_dso_shared['cdll']
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return cdll.P2145_0_IntegratedWaterVapourContent(p_percent, lat, lon, month, h_mamsl)


def mean_surface_total_pressure(lat: float, lon: float, month: int|None=None,
                                h_mamsl: float|None=None) -> float:
    """
    ITU-R P.2145-0, Section 2.2 of Annex.
    
    Gets the mean of the surface total (barometric) pressure (hPa) at the specified location on the 
    surface of the Earth.

    Args:
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511. Default value is None.

    Returns:
        float: The mean of the surface total (barometric) pressure (hPa) at the specified location
            on the surface of the Earth.
    """
    cdll = _p2145_0_dso_shared['cdll']
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return cdll.P2145_0_MeanSurfaceTotalPressure(lat, lon, month, h_mamsl)


def mean_surface_temperature(lat: float, lon: float, month: int|None=None, h_mamsl: float|None=None
                             ) -> float:
    """
    ITU-R P.2145-0, Section 2.2 of Annex.

    Gets the mean of the surface temperature (K) at the specified location on the surface of the
    Earth.

    Args:
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511. Default value is None.

    Returns:
        float: The mean of the surface temperature (K) at the specified location on the surface
            of the Earth.
    """
    cdll = _p2145_0_dso_shared['cdll']
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return cdll.P2145_0_MeanSurfaceTemperature(lat, lon, month, h_mamsl)


def mean_surface_water_vapour_density(lat: float, lon: float, month: int|None=None,
                                      h_mamsl: float|None=None) -> float:
    """
    ITU-R P.2145-0, Section 2.2 of Annex.

    Gets the mean of the surface water vapour density (g/m3) at the specified location on the
    surface of the Earth.

    Args:
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511. Default value is None.

    Returns:
        float: The mean of the surface water vapour density (g/m3) at the specified location on
            the surface of the Earth.
    """
    cdll = _p2145_0_dso_shared['cdll']
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return cdll.P2145_0_MeanSurfaceWaterVapourDensity(lat, lon, month, h_mamsl)


def mean_integrated_water_vapour_content(lat: float, lon: float, month: int|None=None,
                                         h_mamsl: float|None=None) -> float:
    """
    ITU-R P.2145-0, Section 2.2 of Annex.

    Gets the mean of the integrated water vapour content (kg/m2) at the specified location on the 
    surface of the Earth.

    Args:
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511. Default value is None.

    Returns:
        float: The mean of the integrated water vapour content (kg/m2) at the specified location
            on the surface of the Earth.
    """
    cdll = _p2145_0_dso_shared['cdll']
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return cdll.P2145_0_MeanIntegratedWaterVapourContent(lat, lon, month, h_mamsl)


def std_dev_surface_total_pressure(lat: float, lon: float, month: int|None=None,
                                   h_mamsl: float|None=None) -> float:
    """
    ITU-R P.2145-0, Section 2.2 of Annex.

    Gets the standard deviation of the surface total (barometric) pressure (hPa) at the specified
    location on the surface of the Earth.

    Args:
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511. Default value is None.

    Returns:
        float: The standard deviation of the surface total (barometric) pressure (hPa) at the
            specified location on the surface of the Earth.
    """
    cdll = _p2145_0_dso_shared['cdll']
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return cdll.P2145_0_StdDevSurfaceTotalPressure(lat, lon, month, h_mamsl)


def std_dev_surface_temperature(lat: float, lon: float, month: int|None=None,
                                h_mamsl: float|None=None) -> float:
    """
    ITU-R P.2145-0, Section 2.2 of Annex.

    Gets the standard deviation of the surface temperature (K) at the specified location on the
    surface of the Earth.

    Args:
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511. Default value is None.

    Returns:
        float: The standard deviation of the surface temperature (K) at the specified location on
            the surface of the Earth.
    """
    cdll = _p2145_0_dso_shared['cdll']
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return cdll.P2145_0_StdDevSurfaceTemperature(lat, lon, month, h_mamsl)


def std_dev_surface_water_vapour_density(lat: float, lon: float, month: int|None=None,
                                         h_mamsl: float|None=None) -> float:
    """
    ITU-R P.2145-0, Section 2.2 of Annex.

    Gets the standard deviation of the surface water vapour density (g/m3) at the specified
    location on the surface of the Earth.

    Args:
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511. Default value is None.

    Returns:
        float: The standard deviation of the surface water vapour density (g/m3) at the specified
            location on the surface of the Earth.
    """
    cdll = _p2145_0_dso_shared['cdll']
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return cdll.P2145_0_StdDevSurfaceWaterVapourDensity(lat, lon, month, h_mamsl)


def std_dev_integrated_water_vapour_content(lat: float, lon: float, month: int|None=None,
                                            h_mamsl: float|None=None) -> float:
    """
    ITU-R P.2145-0, Section 2.2 of Annex.

    Gets the standard deviation of the integrated water vapour content (kg/m2) at the specified
    location on the surface of the Earth.

    Args:
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        month (int or None, optional): Month to get the statistics for (1=Jan, ..., 12=Dec). Use
            None for annual statistics. Default value is None.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511. Default value is None.

    Returns:
        float: The standard deviation of the integrated water vapour content (kg/m2) at the
            specified location on the surface of the Earth.
    """
    cdll = _p2145_0_dso_shared['cdll']
    if month is None:
        month = -1
    if h_mamsl is None:
        h_mamsl = float('nan')
    return cdll.P2145_0_StdDevIntegratedWaterVapourContent(lat, lon, month, h_mamsl)


def weibull_parameters(lat: float, lon: float, h_mamsl: float|None=None) -> tuple[float, float]:
    """
    ITU-R P.2145-0, Section 2.2 of Annex.

    Gets the Weibull integrated water vapour content shape and scale parameters at the specified
    location on the surface of the Earth.

    Args:
        lat (float): Latitude of the desired location (deg), with -90 <= lat <= 90.
        lon (float): Longitude of the desired location (deg), with -180 <= lon <= 180.
        h_mamsl (float or None, optional): Height of the desired location (meters above mean sea
            level). When set to None, the height is automatically obtained from Recommendation
            ITU-R P.1511. Default value is None.

    Returns:
        k_VS (float): The Weibull integrated water vapour content shape parameter.
        lambda_VS (float): The Weibull integrated water vapour content scale parameter.
    """
    cdll = _p2145_0_dso_shared['cdll']
    if h_mamsl is None:
        h_mamsl = float('nan')
    kV = cdll.P2145_0_WeibullShapeParameter(lat, lon, h_mamsl)
    labmdaV = cdll.P2145_0_WeibullScaleParameter(lat, lon, h_mamsl)
    return (kV, labmdaV)


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
    _download_annual_rec_data(warn_if_already_installed=False) # From p2145_0.py
    return lib


def _set_args_and_return_ctypes(lib):
    lib.P2145_0_SurfaceTotalPressure.argtypes = [ct.c_double, ct.c_double, ct.c_double, ct.c_int,
                                                 ct.c_double]
    lib.P2145_0_SurfaceTotalPressure.restype = ct.c_double

    lib.P2145_0_SurfaceTemperature.argtypes = [ct.c_double, ct.c_double, ct.c_double, ct.c_int,
                                               ct.c_double]
    lib.P2145_0_SurfaceTemperature.restype = ct.c_double

    lib.P2145_0_SurfaceWaterVapourDensity.argtypes = [ct.c_double, ct.c_double, ct.c_double,
                                                      ct.c_int,ct.c_double]
    lib.P2145_0_SurfaceWaterVapourDensity.restype = ct.c_double

    lib.P2145_0_IntegratedWaterVapourContent.argtypes = [ct.c_double, ct.c_double, ct.c_double,
                                                         ct.c_int, ct.c_double]
    lib.P2145_0_IntegratedWaterVapourContent.restype = ct.c_double

    lib.P2145_0_MeanSurfaceTotalPressure.argtypes = [ct.c_double, ct.c_double, ct.c_int,
                                                     ct.c_double]
    lib.P2145_0_MeanSurfaceTotalPressure.restype = ct.c_double

    lib.P2145_0_MeanSurfaceTemperature.argtypes = [ct.c_double, ct.c_double, ct.c_int, ct.c_double]
    lib.P2145_0_MeanSurfaceTemperature.restype = ct.c_double

    lib.P2145_0_MeanSurfaceWaterVapourDensity.argtypes = [ct.c_double, ct.c_double, ct.c_int,
                                                          ct.c_double]
    lib.P2145_0_MeanSurfaceWaterVapourDensity.restype = ct.c_double

    lib.P2145_0_MeanIntegratedWaterVapourContent.argtypes = [ct.c_double, ct.c_double, ct.c_int,
                                                             ct.c_double]
    lib.P2145_0_MeanIntegratedWaterVapourContent.restype = ct.c_double

    lib.P2145_0_StdDevSurfaceTotalPressure.argtypes = [ct.c_double, ct.c_double, ct.c_int,
                                                       ct.c_double]
    lib.P2145_0_StdDevSurfaceTotalPressure.restype = ct.c_double

    lib.P2145_0_StdDevSurfaceTemperature.argtypes = [ct.c_double, ct.c_double, ct.c_int,
                                                     ct.c_double]
    lib.P2145_0_StdDevSurfaceTemperature.restype = ct.c_double

    lib.P2145_0_StdDevSurfaceWaterVapourDensity.argtypes = [ct.c_double, ct.c_double, ct.c_int,
                                                            ct.c_double]
    lib.P2145_0_StdDevSurfaceWaterVapourDensity.restype = ct.c_double

    lib.P2145_0_StdDevIntegratedWaterVapourContent.argtypes = [ct.c_double, ct.c_double, ct.c_int,
                                                               ct.c_double]
    lib.P2145_0_StdDevIntegratedWaterVapourContent.restype = ct.c_double

    lib.P2145_0_WeibullShapeParameter.argtypes = [ct.c_double, ct.c_double, ct.c_double]
    lib.P2145_0_WeibullShapeParameter.restype = ct.c_double

    lib.P2145_0_WeibullScaleParameter.argtypes = [ct.c_double, ct.c_double, ct.c_double]
    lib.P2145_0_WeibullScaleParameter.restype = ct.c_double


_p2145_0_dso_shared = {
    'cdll': _init_dynamic_library()
}
