# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.368-10, dynamic shared object version (i.e. using a compiled binary).

Info: Acknowledgment & Source
    This module consists in a Python wrapper around the original C++ implementation developed by
    the Institute for Telecommunication Sciences (ITS) at the National Telecommunications and
    Information Administration (NTIA), U.S. Department of Commerce.

    * **Source Repository:**  https://github.com/NTIA/LFMF

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite the following:

    * **ITU-R Standard:** International Telecommunication Union (2022).
      *Recommendation ITU-R P.368-10: Ground-wave propagation prediction method for frequencies
      between 10 kHz and 30 MHz*. Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.368/en
    * **Software Reference:** Kozma, W., Jr., & U.S. Department of Commerce, National
      Telecommunications and Information Administration, Institute for Telecommunication Sciences.
      *Low Frequency / Medium Frequency (LF/MF) Propagation Model*
      (Version 1.1) [Computer software].
      https://github.com/NTIA/LFMF
"""

import ctypes as ct
import enum
from propakai import _bin_utils as _bu


__all__ = ['Polarization',
           'SolutionMethod',
           'GroundType',
           'ground_constants',
           'basic_transmission_loss']


class Polarization(enum.Enum):
    """To use as input for basic_transmission_loss()."""
    HORIZONTAL = 0
    VERTICAL   = 1


class SolutionMethod(enum.Enum):
    """Output values for basic_transmission_loss()."""
    FLAT_EARTH_CURVE = 0
    RESIDUE_SERIES   = 1


class GroundType(enum.Enum):
    """To use as input for ground_constants()."""
    SEA_WATER_LOW_SALINITY     = 1
    SEA_WATER_AVG_SALINITY     = 2
    FRESH_WATER                = 3
    WET_GROUND                 = 4
    MEDIUM_DRY_GROUND          = 5
    DRY_GROUND                 = 6
    VERY_DRY_GROUND            = 7
    FRESH_WATER_ICE_MINUS_1_C  = 8
    FRESH_WATER_ICE_MINUS_10_C = 9


class _Result(ct.Structure):
    _fields_ = [
        ('A_btl__db', ct.c_double),
        ('E_dBuVm', ct.c_double),
        ('P_rx__dbm', ct.c_double),
        ('method', ct.c_int)
    ]


def ground_constants(ground_type: GroundType) -> tuple[float, float]:
    """
    Gets typical conductivity (S/m) and relative permittivity values based on ground type.

    Values based on TABLE 2 from:
    Handbook on Ground Wave Propagation, Edition of 2014, Radiocommunication Bureau.
    http://handle.itu.int/11.1002/pub/809efe7d-en
    
    Args:
        ground_type (GroundType): Ground type.
    
    Returns:
        sigma_sm (float): Conductivity (S/m).
        eps (float): Relative permittivity.
    """
    constants = {
            GroundType.SEA_WATER_LOW_SALINITY:     (1, 80),
            GroundType.SEA_WATER_AVG_SALINITY:     (5, 80),
            GroundType.FRESH_WATER:                (3e-3, 80),
            GroundType.WET_GROUND:                 (1e-2, 30),
            GroundType.MEDIUM_DRY_GROUND:          (1e-3, 15),
            GroundType.DRY_GROUND:                 (3e-4, 7),
            GroundType.VERY_DRY_GROUND:            (1e-4, 3),
            GroundType.FRESH_WATER_ICE_MINUS_1_C:  (3e-5, 3),
            GroundType.FRESH_WATER_ICE_MINUS_10_C: (1e-5, 3)
    }
    return constants[ground_type]


def basic_transmission_loss(f_mhz: float, d_km: float, htx_m: float, hrx_m: float, ptx_w: float,
                            pol: Polarization, ns: float, eps: float, sigma_sm: float
                            ) -> tuple[float, float, float, SolutionMethod]:
    """
    ITU-R P.368-10, Annex 1.

    Predicts ground-wave basic transmission loss, electric field strength and received power over
    a smooth Earth for frequencies between 10 kHz and 30 MHz.

    Args:
        f_mhz (float): Frequency (MHz), with 0.01 <= f_mhz <= 30.
        d_km (float): Path length (km), with 0.001 <= d_km <= 10000.
        htx_m (float): Heigth of the transmitter (m), with 0 <= htx_m <= 50. 
        hrx_m (float): Height of the receiver (m), with 0 <= hrx_m <= 50.
        ptx_w (float): Transmitter power (Watts), with 0 < ptx_w.
        pol (Polarization): Polarization (HORIZONTAL or VERTICAL).
        ns (float): Surface refractivity (N-units), with 250 <= ns <= 400.
        eps (float): Relative permittivity on the surface of the Earth (also known as the
            dielectric constant of ground), with 1 <= eps.
        sigma_sm (float): Conductivity (S/m) on the surface of the Earth, with 0 < sigma_sm.
    
    Returns:
        A_btl__db (float): Basic transmission loss (dB).
        E_dBuVm (float): Electric field strength (dBuV/m).
        P_rx__dbm (float): Received power (dBm).
        method (SolutionMethod): Method used to obtain results (FLAT_EARTH_CURVE or
            RESIDUE_SERIES).
    """
    result = _Result()
    cdll = _p368_10_dso_shared['cdll']
    ret = cdll.LFMF(htx_m, hrx_m, f_mhz, ptx_w, ns, d_km, eps, sigma_sm, pol.value,
                    ct.byref(result))
    if ret != 0:
        err_msgs = {
            32: 'htx_m is out of range.',
            33: 'hrx_m is out of range.',
            34: 'f_mhz is out of range.',
            35: 'ptx_w is out of range.',
            36: 'ns is out of range.',
            37: 'd_km is out of range.',
            38: 'eps is out of range.',
            39: 'sigma_sm is out of range.',
            40: 'Unexpected value for pol.'
        }
        raise ValueError(err_msgs[ret])
    return float(result.A_btl__db), float(result.E_dBuVm), float(result.P_rx__dbm), \
           SolutionMethod(result.method)


def _load_p368_10_dynamic_library() -> ct.CDLL:
    lib = _bu.get_dynamic_library('p368_10')
    _set_args_and_return_ctypes(lib)
    return lib


def _set_args_and_return_ctypes(lib):
    lib.LFMF.argtypes = [ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double,
                         ct.c_double, ct.c_double, ct.c_double, ct.c_int, ct.POINTER(_Result)]
    lib.LFMF.restype = ct.c_int


_p368_10_dso_shared = {
    'cdll': _load_p368_10_dynamic_library()
}
