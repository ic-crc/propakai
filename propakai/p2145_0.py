# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.2145-0.

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite this software
    package along with the underlying ITU-R standard:

    * **ITU-R Standard:** International Telecommunication Union (2022).
      *Recommendation ITU-R P.2145-0: Digital maps related to the calculation of gaseous attenuation
      and related effects*. Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.2145/en
"""

from os.path import join
from math import exp, log10
from threading import Lock
from array import array
from typing import Callable
from filelock import FileLock
from propakai import _download_utils as _du
from propakai import p1144_13
from propakai import p1511_3


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
           'weibull_parameters']


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
    maps = _get_ccdf_maps(p_percent, month, 'P')
    return _ccdf_interpolation(p_percent, lat, lon, h_mamsl, maps, _exp_scaling_func)


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
    maps = _get_ccdf_maps(p_percent, month, 'T')
    return _ccdf_interpolation(p_percent, lat, lon, h_mamsl, maps, _add_scaling_func)


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
            probabiliby p_percnet (CCDF) at the specified location on the surface of the Earth.
    """
    maps = _get_ccdf_maps(p_percent, month, 'RHO')
    return _ccdf_interpolation(p_percent, lat, lon, h_mamsl, maps, _exp_scaling_func)


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
    maps = _get_ccdf_maps(p_percent, month, 'V')
    return _ccdf_interpolation(p_percent, lat, lon, h_mamsl, maps, _exp_scaling_func)


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
    maps = _get_mean_std_dev_maps(month, 'P')
    return _mean_std_dev_interpolation(lat, lon, h_mamsl, maps.mean_map, maps.sch_map, maps.z_map,
                                       _exp_scaling_func)


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
    maps = _get_mean_std_dev_maps(month, 'T')
    return _mean_std_dev_interpolation(lat, lon, h_mamsl, maps.mean_map, maps.sch_map, maps.z_map,
                                       _add_scaling_func)


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
    maps = _get_mean_std_dev_maps(month, 'RHO')
    return _mean_std_dev_interpolation(lat, lon, h_mamsl, maps.mean_map, maps.sch_map, maps.z_map,
                                       _exp_scaling_func)


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
    maps = _get_mean_std_dev_maps(month, 'V')
    return _mean_std_dev_interpolation(lat, lon, h_mamsl,  maps.mean_map, maps.sch_map, maps.z_map,
                                       _exp_scaling_func)


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
    maps = _get_mean_std_dev_maps(month, 'P')
    return _mean_std_dev_interpolation(lat, lon, h_mamsl, maps.std_dev_map, maps.sch_map,
                                       maps.z_map, _exp_scaling_func)


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
    maps = _get_mean_std_dev_maps(month, 'T')
    return _mean_std_dev_interpolation(lat, lon, h_mamsl, maps.std_dev_map, maps.sch_map,
                                       maps.z_map, _direct_scaling_func)


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
    maps = _get_mean_std_dev_maps(month, 'RHO')
    return _mean_std_dev_interpolation(lat, lon, h_mamsl, maps.std_dev_map, maps.sch_map,
                                       maps.z_map, _exp_scaling_func)


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
    maps = _get_mean_std_dev_maps(month, 'V')
    return _mean_std_dev_interpolation(lat, lon, h_mamsl, maps.std_dev_map, maps.sch_map,
                                       maps.z_map, _exp_scaling_func)


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
        k_VS (float): The Weibull integrated water vapour content shape parameters.
        lambda_VS (float): The Weibull integrated water vapour content scale parameters.
    """
    weibull_dir = 'Weibull_Annual'

    kV_file = join(weibull_dir, 'kV.TXT')
    lambdaV_file = join(weibull_dir, 'lambdaV.TXT')
    sch_file = join(weibull_dir, 'VSCH.TXT')
    z_file = join(weibull_dir, 'Z_ground.TXT')

    sch_dmap = _thread_safe_get_digital_map_array(None, sch_file)
    z_dmap = _thread_safe_get_digital_map_array(None, z_file)

    kV_dmap = _thread_safe_get_digital_map_array(None, kV_file)
    kV = _mean_std_dev_interpolation(lat, lon, h_mamsl, kV_dmap, sch_dmap, z_dmap,
                                     _direct_scaling_func)

    lambdaV_map = _thread_safe_get_digital_map_array(None, lambdaV_file)
    labmdaV = _mean_std_dev_interpolation(lat, lon, h_mamsl, lambdaV_map, sch_dmap, z_dmap,
                                          _exp_scaling_func)

    return (kV, labmdaV)


class _CCDFMaps:
    p_below: float
    p_below_map: array
    p_above: float
    p_above_map: array
    sch_map: array
    z_map: array


class _MeanStdDevMaps:
    mean_map: array
    std_dev_map: array
    sch_map: array
    z_map: array


def _get_ccdf_maps(p_percent: float, month: int|None, param: str) -> _CCDFMaps:
    """
    Args:
        p_percent (float): Exceedance probability (CCDF) of interest, in %.
        month (int or None): Month of the year (1=Jan, ..., 12=Dec). Use None for annual data.
        param (str): Use either 'P', 'T', 'RHO' or 'V'.
    """
    if month is None:
        nominal_percentages = _p2145_0_shared['ANNUAL_P']
        directory = f'{param}_Annual'
    else:
        nominal_percentages = _p2145_0_shared['MONTHLY_P']
        directory = f'{param}_Month{month:02d}'

    for i in range(0, len(nominal_percentages)-1):
        if p_percent >= nominal_percentages[i][0] and p_percent <= nominal_percentages[i+1][0]:
            ccdf_maps = _CCDFMaps()
            ccdf_maps.p_below = nominal_percentages[i][0]
            ccdf_maps.p_above = nominal_percentages[i+1][0]

            p_below_file = join(directory, f'{param}_{nominal_percentages[i][1]}.TXT')
            p_above_file = join(directory, f'{param}_{nominal_percentages[i+1][1]}.TXT')
            if param == 'RHO':
                sch_file = join(directory, 'VSCH.TXT')
            else:
                sch_file = join(directory, f'{param}SCH.TXT')
            z_file = join(directory, 'Z_ground.TXT')

            ccdf_maps.p_below_map = _thread_safe_get_digital_map_array(month, p_below_file)
            ccdf_maps.p_above_map = _thread_safe_get_digital_map_array(month, p_above_file)
            ccdf_maps.sch_map = _thread_safe_get_digital_map_array(month, sch_file)
            ccdf_maps.z_map = _thread_safe_get_digital_map_array(month, z_file)

            return ccdf_maps
    raise ValueError('p_percent is out of range.')


def _get_mean_std_dev_maps(month: int|None, param: str) -> _MeanStdDevMaps:
    """
    Args:
        month (int or None): Month of the year (1=Jan, ..., 12=Dec). Use None for annual data.
        param (str): Use either 'P', 'T', 'RHO' or 'V'.
    """
    if month is None:
        directory = f'{param}_Annual'
    else:
        directory = f'{param}_Month{month:02d}'

    mean_std_dev_maps = _MeanStdDevMaps()

    mean_file = join(directory, f'{param}_mean.TXT')
    mean_std_dev_maps.mean_map = _thread_safe_get_digital_map_array(None, mean_file)

    std_dev_file = join(directory, f'{param}_std.TXT')
    mean_std_dev_maps.std_dev_map = _thread_safe_get_digital_map_array(None, std_dev_file)

    if param == 'RHO':
        sch_file = join(directory, 'VSCH.TXT')
    else:
        sch_file = join(directory, f'{param}SCH.TXT')
    mean_std_dev_maps.sch_map = _thread_safe_get_digital_map_array(None, sch_file)

    z_file = join(directory, 'Z_ground.TXT')
    mean_std_dev_maps.z_map = _thread_safe_get_digital_map_array(None, z_file)

    return mean_std_dev_maps


def _ccdf_interpolation(p_percent: float, lat: float, lon: float,
                        h_mamsl: float|None, maps: _CCDFMaps,
                        scaling_func: Callable[[float, float, float, float], float]
                        ) -> float:
    """
    ITU-R P.2145-0, Section 2.1 of Annex.
    """
    # a)
    alt = h_mamsl
    if alt is None:
        alt = p1511_3.topographic_height(lat, lon) # returns meters
    alt = alt/1000 # convert from m to km

    # lat from -90 to +90, lon from -180 to +180, intervals of 0.25 deg
    num_rows = 721 # (180/0.25)+1
    row_size = 1441 # (360/0.25)+1
    r = (90.0 + lat) / 0.25
    c = (180.0 + lon) / 0.25
    R = int(r)
    R = max(R, 0)
    R = min(R, num_rows-2)
    C = int(c)
    C = max(C, 0)
    C = min(C, row_size-2)

    i0 = R*row_size + C
    i1 = (R+1)*row_size + C
    i2 = R*row_size + (C+1)
    i3 = (R+1)*row_size + (C+1)

    # c)
    Xpa0, Xpa1, Xpa2, Xpa3 = maps.p_above_map[i0], maps.p_above_map[i1], maps.p_above_map[i2], \
                             maps.p_above_map[i3]
    Xpb0, Xpb1, Xpb2, Xpb3 = maps.p_below_map[i0], maps.p_below_map[i1], maps.p_below_map[i2], \
                             maps.p_below_map[i3]

    # d)
    sch0, sch1, sch2, sch3 = maps.sch_map[i0], maps.sch_map[i1], maps.sch_map[i2], maps.sch_map[i3]

    # e)
    alt0, alt1, alt2, alt3 = maps.z_map[i0], maps.z_map[i1], maps.z_map[i2], maps.z_map[i3]

    # f)
    Xa0, Xa1, Xa2, Xa3 = scaling_func(Xpa0, sch0, alt, alt0), scaling_func(Xpa1, sch1, alt, alt1),\
                         scaling_func(Xpa2, sch2, alt, alt2), scaling_func(Xpa3, sch3, alt, alt3)
    Xb0, Xb1, Xb2, Xb3 = scaling_func(Xpb0, sch0, alt, alt0), scaling_func(Xpb1, sch1, alt, alt1),\
                         scaling_func(Xpb2, sch2, alt, alt2), scaling_func(Xpb3, sch3, alt, alt3)

    # g)
    X_above = Xa0*((R+1-r)*(C+1-c)) + Xa1*((r-R)*(C+1-c)) + Xa2*((R+1-r)*(c-C)) + Xa3*((r-R)*(c-C))
    X_below = Xb0*((R+1-r)*(C+1-c)) + Xb1*((r-R)*(C+1-c)) + Xb2*((R+1-r)*(c-C)) + Xb3*((r-R)*(c-C))

    # h)
    X0 = X_below
    X1 = X_above
    p0 = maps.p_below
    p1 = maps.p_above
    X = (X0*log10(p1/p_percent) + X1*log10(p_percent/p0)) / log10(p1/p0)

    return X


def _mean_std_dev_interpolation(lat: float, lon: float, h_mamsl: float|None,
                                main_map: array, sch_map: array, z_map: array,
                                scaling_func: Callable[[float, float, float, float], float]
                                ) -> float:
    """
    ITU-R P.2145-0, Section 2.2 of Annex.
    """
    # a)
    alt = h_mamsl
    if alt is None:
        alt = p1511_3.topographic_height(lat, lon) # returns meters
    alt = alt/1000 # convert from m to km

    # lat from -90 to +90, lon from -180 to +180, intervals of 0.25 deg
    num_rows = 721 # (180/0.25)+1
    row_size = 1441 # (360/0.25)+1
    r = (90.0 + lat) / 0.25
    c = (180.0 + lon) / 0.25
    R = int(r)
    R = max(R, 0)
    R = min(R, num_rows-2)
    C = int(c)
    C = max(C, 0)
    C = min(C, row_size-2)

    i0 = R*row_size + C
    i1 = (R+1)*row_size + C
    i2 = R*row_size + (C+1)
    i3 = (R+1)*row_size + (C+1)

    # b)
    Xp0, Xp1, Xp2, Xp3 = main_map[i0], main_map[i1], main_map[i2], main_map[i3]

    # c)
    sch0, sch1, sch2, sch3 = sch_map[i0], sch_map[i1], sch_map[i2], sch_map[i3]

    # d)
    alt0, alt1, alt2, alt3 = z_map[i0], z_map[i1], z_map[i2], z_map[i3]

    # e)
    X0 = scaling_func(Xp0, sch0, alt, alt0)
    X1 = scaling_func(Xp1, sch1, alt, alt1)
    X2 = scaling_func(Xp2, sch2, alt, alt2)
    X3 = scaling_func(Xp3, sch3, alt, alt3)

    # f)
    X = X0*((R+1-r)*(C+1-c)) + X1*((r-R)*(C+1-c)) + X2*((R+1-r)*(c-C)) + X3*((r-R)*(c-C))

    return X


def _exp_scaling_func(xp: float, sch: float, alt: float, alti: float) -> float:
    return xp*exp(-(alt-alti)/sch)


def _add_scaling_func(xp: float, sch: float, alt: float, alti: float) -> float:
    return xp+(sch*(alt-alti))


def _direct_scaling_func(xp: float, _: float, __: float, ___: float) -> float:
    return xp


def _thread_safe_get_digital_map_array(month: int|None, relname: str) -> array:
    """
    Args:
        month (int or None): From 1 (Jan) to 12 (Dec). Use None for annual data.
        relname (str): Filename with path relative to _download_utils.install_dir()/p2145_0/
    """
    # NOTE: It is not safe to concurrently access a Python dictionary from one thread while it is
    # being modified by another thread, even if you are only reading a specific key/value that is
    # not being directly modified. This is why we always use the lock here.
    with _p2145_0_shared['digital_maps_lock']:
        dmaps = _p2145_0_shared['digital_maps']
        if relname not in dmaps:
            pathname = join(_du.install_dir(), _p2145_0_shared['DATA_DIR'], relname)
            try:
                arr = p1144_13.load_digital_map(pathname)
            except FileNotFoundError:
                if month is None:
                    _download_annual_rec_data()
                else:
                    _download_monthly_rec_data(month)
                arr = p1144_13.load_digital_map(pathname)
            dmaps[relname] = arr
        map_array = dmaps[relname]
    return map_array


def _download_annual_rec_data() -> None:
    data_dir = _p2145_0_shared['DATA_DIR']
    full_path_data_dir = join(_du.install_dir(), data_dir)
    percents = [p[1] for p in _p2145_0_shared['ANNUAL_P']]
    p_filenames = [f'P_{p}.TXT' for p in percents] + \
                  ['P_mean.TXT', 'P_std.TXT', 'PSCH.TXT', 'Z_ground.TXT']
    rho_filenames = [f'RHO_{p}.TXT' for p in percents] + \
                    ['RHO_mean.TXT', 'RHO_std.TXT', 'VSCH.TXT', 'Z_ground.TXT']
    t_filenames = [f'T_{p}.TXT' for p in percents] + \
                  ['T_mean.TXT', 'T_std.TXT', 'TSCH.TXT', 'Z_ground.TXT']
    v_filenames = [f'V_{p}.TXT' for p in percents] + \
                  ['V_mean.TXT', 'V_std.TXT', 'VSCH.TXT', 'Z_ground.TXT']
    p_dir = join(full_path_data_dir, 'P_Annual')
    rho_dir = join(full_path_data_dir, 'RHO_Annual')
    t_dir = join(full_path_data_dir, 'T_Annual')
    v_dir = join(full_path_data_dir, 'V_Annual')

    lock = FileLock(_du.get_lockfile_pathname(f'{data_dir}_annual'))
    with lock:
        if _du.files_all_exist(p_dir, p_filenames) is False or \
        _du.files_all_exist(rho_dir, rho_filenames) is False or \
        _du.files_all_exist(t_dir, t_filenames) is False or \
        _du.files_all_exist(v_dir, v_filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/' \
                  'R-REC-P.2145Part01-0-202208-I!!ZIP-E.zip'
            zip_pathname = _du.download(url, full_path_data_dir)
            _du.extract_files(zip_pathname, ['Attribution&disclaimer.txt'], create_dirs=True,
                              delete_zip_archive=False)
            zip_pathname_list = _du. extract_files(
                                zip_pathname,
                                ['P_Annual.zip', 'RHO_Annual.zip', 'T_Annual.zip', 'V_Annual.zip'],
                                create_dirs=True, delete_zip_archive=True)
            for zip_pathname in zip_pathname_list:
                _du.extract_all(zip_pathname, delete_zip_archive=True, create_new_dir=True)
            _du.print_notice()
        else:
            _du.print_already_installed(p_dir, p_filenames)
            _du.print_already_installed(rho_dir, rho_filenames)
            _du.print_already_installed(t_dir, t_filenames)
            _du.print_already_installed(v_dir, v_filenames)

    # Weibull annual data
    weibull_filenames = ['kV.TXT', 'lambdaV.TXT', 'VSCH.TXT', 'Z_ground.TXT']
    weibull_dir = join(full_path_data_dir, 'Weibull_Annual')
    with lock:
        if _du.files_all_exist(weibull_dir, weibull_filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/' \
                  'R-REC-P.2145Part14-0-202208-I!!ZIP-E.zip'
            zip_pathname1 = _du.download(url, full_path_data_dir)
            zip_pathname2 = _du.extract_files(zip_pathname1, ['Weibull_Annual.zip'],
                                              create_dirs=True, delete_zip_archive=True)[0]
            _du.extract_all(zip_pathname2, delete_zip_archive=True, create_new_dir=True)
            _du.print_notice()
        else:
            _du.print_already_installed(weibull_dir, weibull_filenames)


def _download_monthly_rec_data(month: int) -> None:
    """
    Downloads monthly data files.

    Args:
        month (int): 1 <= month <= 12.
    """
    data_dir = _p2145_0_shared['DATA_DIR']
    full_path_data_dir = join(_du.install_dir(), data_dir)
    percents = [p[1] for p in _p2145_0_shared['MONTHLY_P']]
    month_num_str = f'{month:02d}'
    part_num_str = f'{month+1:02d}'
    p_filenames = [f'P_{p}.TXT' for p in percents] + \
                  ['P_mean.TXT', 'P_std.TXT', 'PSCH.TXT', 'Z_ground.TXT']
    rho_filenames = [f'RHO_{p}.TXT' for p in percents] + \
                    ['RHO_mean.TXT', 'RHO_std.TXT', 'VSCH.TXT', 'Z_ground.TXT']
    t_filenames = [f'T_{p}.TXT' for p in percents] + \
                  ['T_mean.TXT', 'T_std.TXT', 'TSCH.TXT', 'Z_ground.TXT']
    v_filenames = [f'V_{p}.TXT' for p in percents] + \
                  ['V_mean.TXT', 'V_std.TXT', 'VSCH.TXT', 'Z_ground.TXT']
    p_dir = join(full_path_data_dir, f'P_Month{month_num_str}')
    rho_dir = join(full_path_data_dir, f'RHO_Month{month_num_str}')
    t_dir = join(full_path_data_dir, f'T_Month{month_num_str}')
    v_dir = join(full_path_data_dir, f'V_Month{month_num_str}')

    lock = FileLock(_du.get_lockfile_pathname(f'{data_dir}_month{month}'))
    with lock:
        if _du.files_all_exist(p_dir, p_filenames) is False or \
           _du.files_all_exist(rho_dir, rho_filenames) is False or \
           _du.files_all_exist(t_dir, t_filenames) is False or \
           _du.files_all_exist(v_dir, v_filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/' \
                  f'R-REC-P.2145Part{part_num_str}-0-202208-I!!ZIP-E.zip'
            zip_pathname = _du.download(url, full_path_data_dir)
            _du.extract_files(zip_pathname, ['Attribution&disclaimer.txt'], create_dirs=True,
                              delete_zip_archive=False)
            zip_pathname_list = _du.extract_files(zip_pathname,
                                                  [f'P_Month{month_num_str}.zip',
                                                   f'RHO_Month{month_num_str}.zip',
                                                   f'T_Month{month_num_str}.zip',
                                                   f'V_Month{month_num_str}.zip'],
                                                   create_dirs=True, delete_zip_archive=True)
            for zip_pathname in zip_pathname_list:
                _du.extract_all(zip_pathname, delete_zip_archive=True, create_new_dir=True)
            _du.print_notice()
        else:
            _du.print_already_installed(p_dir, p_filenames)
            _du.print_already_installed(rho_dir, rho_filenames)
            _du.print_already_installed(t_dir, t_filenames)
            _du.print_already_installed(v_dir, v_filenames)


_p2145_0_shared = {
    'DATA_DIR': 'p2145_0',

    'ANNUAL_P': ((0.01, '001'), (0.02, '002'), (0.03, '003'), (0.05, '005'), (0.1, '01'),
                 (0.2, '02'), (0.3, '03'), (0.5, '05'), (1, '1'), (2, '2'), (3, '3'), (5, '5'),
                 (10, '10'), (20, '20'), (30, '30'), (50, '50'), (60, '60'), (70, '70'),
                 (80, '80'), (90, '90'), (95, '95'), (99, '99')),

    'MONTHLY_P': ((0.1, '01'), (0.2, '02'), (0.3, '03'), (0.5, '05'), (1, '1'), (2, '2'), (3, '3'),
              (5, '5'), (10, '10'), (20, '20'), (30, '30'), (50, '50'), (60, '60'), (70, '70'),
              (80, '80'), (90, '90'), (95, '95'), (99, '99')),

    'digital_maps_lock': Lock(),

    'digital_maps': {}
}
