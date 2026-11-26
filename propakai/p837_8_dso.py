# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.837-8, dynamic shared object version (i.e. using a compiled binary).

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite this software
    package along with the underlying ITU-R standard:

    * **ITU-R Standard:** International Telecommunication Union (2025).
      *Recommendation ITU-R P.837-8: Characteristics of precipitation for propagation modelling*.
      Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.837/en
"""

from types import SimpleNamespace
import ctypes as ct
from propakai import _bin_utils as _bu
from propakai.p837_8 import _download_rec_data


__all__ = ['annual_rainfall_rate_001',
           'total_monthly_mean_rainfall',
           'annual_rainfall_rate',
           'annual_probability_of_rain',
           'monthly_rainfall_rate',
           'monthly_probability_of_rain']


def annual_rainfall_rate_001(lat: float, lon: float) -> float:
    """
    ITU-R P.837-8.
    
    Gets the annual rainfall rate exceeded for 0.01% of an average year (mm/hr).
    This function uses bilinear interpolation on the precalculated R001.txt file.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        R001 (float): The annual rainfall rate exceeded for 0.01% of an average year (mm/hr).
    """
    return _p837_8_dso_shared.cdll.P837_8_AnnualRainfallRate001(lat, lon)


def total_monthly_mean_rainfall(lat: float, lon: float, month: int) -> float:
    """
    ITU-R P.837-8, Annex 1.

    Gets the total monthly mean rainfall (mm).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        MT (float): Total monthly mean rainfall (mm).
    """
    return _p837_8_dso_shared.cdll.P837_8_TotalMonthlyMeanRainfall(lat, lon, month)


def annual_rainfall_rate(p_percent: float, lat: float, lon: float) -> tuple[float, float]:
    """
    ITU-R P.837-8, Annex 1.
    
    Gets the rainfall rate at the desired annual rainfall rate probability of exceedance (mm/hr),
    along with the annual probability of rain (%).

    Args:
        p_percent (float): Annual rainfall rate probability of exceedance (%).
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        Rp (float): Rainfall rate exceeded for the desired annual probability of exceedance,
            p_percent, at the specified location on the surface of the Earth, and for an integration
            time of 1 minute (mm/hr).
        P0_annual (float): Annual probability of rain (%).
    """
    rp_annual = ct.c_double(0.0)
    p0_annual = ct.c_double(0.0)
    _p837_8_dso_shared.cdll.P837_8_AnnualRainfallRate(p_percent, lat, lon,
                                                      ct.byref(rp_annual), ct.byref(p0_annual))
    return (rp_annual.value, p0_annual.value)


def annual_probability_of_rain(lat: float, lon: float) -> float:
    """
    ITU-R P.837-8, Annex 1.
    
    Gets the annual probability of rain (%). Faster than using annual_rainfall_rate() when only the
    probability of rain is wanted.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.

    Returns:
        P0_annual (float): Annual probability of rain (%).
    """
    return _p837_8_dso_shared.cdll.P837_8_AnnualProbabilityOfRain(lat, lon)


def monthly_rainfall_rate(p_percent: float, lat: float, lon: float, month: int
                          ) -> tuple[float, float]:
    """
    ITU-R P.837-8, Annex 1.
    
    Gets the rainfall rate at the desired monthly rainfall rate probability of exceedance (mm/hr),
    along with the monthly probability of rain (%).

    Args:
        p_percent (float): Monthly rainfall rate probability of exceedance (%).
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        Rp_ii (float): Rainfall rate exceeded for the desired monthly probability of exceedance,
            p_percent, at the specified location on the surface of the Earth, and for an
            integration time of 1 minute (mm/hr).
        P0_ii (float): Monthly probability of rain (%).
    """
    rp_monthly = ct.c_double(0.0)
    p0_monthly = ct.c_double(0.0)
    _p837_8_dso_shared.cdll.P837_8_MonthlyRainfallRate(p_percent, lat, lon, month,
                                                       ct.byref(rp_monthly), ct.byref(p0_monthly))
    return (rp_monthly.value, p0_monthly.value)


def monthly_probability_of_rain(lat: float, lon: float, month: int) -> float:
    """
    ITU-R P.837-8, Annex 1.
    
    Gets the monthly probability of rain (%). Faster than using monthly_rainfall_rate() when only
    the probability of rain is wanted.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
        month (int): Month (1=Jan, ..., 12=Dec).

    Returns:
        P0_ii (float): Monthly probability of rain (%).
    """
    return _p837_8_dso_shared.cdll.P837_8_MonthlyProbabilityOfRain(lat, lon, month)


def _init_dynamic_library() -> ct.CDLL:
    lib = _bu.get_dynamic_library('propakai_cpp')
    _set_args_and_return_ctypes(lib)
    _download_rec_data(warn_if_already_installed=False)
    return lib


def _set_args_and_return_ctypes(lib):
    lib.P837_8_AnnualRainfallRate001.argtypes = [ct.c_double, ct.c_double]
    lib.P837_8_AnnualRainfallRate001.restype = ct.c_double

    lib.P837_8_TotalMonthlyMeanRainfall.argtypes = [ct.c_double, ct.c_double, ct.c_int]
    lib.P837_8_TotalMonthlyMeanRainfall.restype = ct.c_double

    lib.P837_8_AnnualRainfallRate.argtypes = [ct.c_double, ct.c_double, ct.c_double,
                                              ct.POINTER(ct.c_double), ct.POINTER(ct.c_double)]
    lib.P837_8_AnnualRainfallRate.restype = None

    lib.P837_8_AnnualProbabilityOfRain.argtypes = [ct.c_double, ct.c_double]
    lib.P837_8_AnnualProbabilityOfRain.restype = ct.c_double

    lib.P837_8_MonthlyRainfallRate.argtypes = [ct.c_double, ct.c_double, ct.c_double, ct.c_int,
                                               ct.POINTER(ct.c_double), ct.POINTER(ct.c_double)]
    lib.P837_8_MonthlyRainfallRate.restype = None

    lib.P837_8_MonthlyProbabilityOfRain.argtypes = [ct.c_double, ct.c_double, ct.c_int]
    lib.P837_8_MonthlyProbabilityOfRain.restype = ct.c_double


_p837_8_dso_shared = SimpleNamespace(
    cdll = _init_dynamic_library()
)
