# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.528-5, dynamic shared object version (i.e. using a compiled binary).

Info: Acknowledgment & Source
    This module consists in a Python wrapper around the original C++ implementation developed by
    the Institute for Telecommunication Sciences (ITS) at the National Telecommunications and
    Information Administration (NTIA), U.S. Department of Commerce.

    * **Source Repository:** https://github.com/NTIA/p528

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite the following:

    * **ITU-R Standard:** International Telecommunication Union (2021).
      *Recommendation ITU-R P.528-5: A propagation prediction method for aeronautical mobile and
      radionavigation services using the VHF, UHF and SHF bands*. Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.528/en
    * **Software Reference:** Kozma, W., Jr. *Recommendation ITU-R P.528-5*
      (Version 5.1.0) [Computer software].
      https://doi.org/10.5281/zenodo.5911006
"""

import ctypes as ct
import enum
from math import radians, asin, cos, pi
from propakai import _bin_utils as _bu


__all__ = ['Polarization',
           'PropagationMode',
           'WarningFlag',
           'Results',
           'great_circle_distance',
           'basic_transmission_loss']


class Polarization(enum.Enum):
    """Enumerates polarization types."""
    HORIZONTAL = 0
    VERTICAL   = 1


class PropagationMode(enum.Enum):
    """Enumerates propagation modes"""
    NOT_SET       = 0
    LINE_OF_SIGHT = 1
    DIFFRATION    = 2
    TROPOSCATTER  = 3


class _ReturnCode(enum.Enum):
    """Enumerates return codes as part of basic_transmission_loss() results."""
    SUCCESS                        = 0
    ERROR_VALIDATION__D_KM         = 1
    ERROR_VALIDATION__H_1          = 2
    ERROR_VALIDATION__H_2          = 3
    ERROR_VALIDATION__TERM_GEO     = 4
    ERROR_VALIDATION__F_MHZ_LOW    = 5
    ERROR_VALIDATION__F_MHZ_HIGH   = 6
    ERROR_VALIDATION__PERCENT_LOW  = 7
    ERROR_VALIDATION__PERCENT_HIGH = 8
    ERROR_VALIDATION__POLARIZATION = 9
    ERROR_HEIGHT_AND_DISTANCE      = 10
    SUCCESS_WITH_WARNINGS          = 11


class WarningFlag(enum.IntEnum):
    """
    Warning flag values, as documented at 
    https://github.com/NTIA/p528/blob/master/ERRORS_AND_WARNINGS.md

    - WARNING__NO_WARNINGS: No warning flags.
    - WARNING__DFRAC_TROPO_REGION: Warning that the diffraction and troposcatter model may not be
        physically consistent with each other. Caution should be taken when using the result.
    - WARNING__HEIGHT_LIMIT_H_1: Terminal 1 height above limit defined within in-force
        Recommendation text. Results should not be intepreted as an official prediction of
        Recommendation ITU-R P.528, but instead treated as informative.
    - WARNING__HEIGHT_LIMIT_H_2: Terminal 2 height above limit defined within in-force
        Recommendation text. Results should not be intepreted as an official prediction of
        Recommendation ITU-R P.528, but instead treated as informative.
    """
    WARNING__NO_WARNINGS        = 0x00
    WARNING__DFRAC_TROPO_REGION = 0x01
    WARNING__HEIGHT_LIMIT_H_1   = 0x02
    WARNING__HEIGHT_LIMIT_H_2   = 0x04


class Results:
    """
    Results from the basic_transmission_loss() function.

    Attributes:
        a_db (float): Basic transmission loss (dB).
        warnings (int): Warning flags. See the WarningFlag class definition for more details.
        d_km (float): Great circle path distance (km). Could be slightly different than specified
            in input variable if within LOS region.
        afs_db (float): Free space basic transmission loss (dB).
        aa_db (float): Median atmospheric absorption loss (dB).
        thetah1_rad (float): Elevation angle of the ray at the low terminal (rad).
        propag_mode (PropagationMode): Mode of propagation.
    """
    def __init__(self):
        self.a_db:float = 0
        self.warnings:int = 0
        self.d_km:float = 0
        self.afs_db:float = 0
        self.aa_db:float = 0
        self.thetah1_rad:float = 0
        self.propag_mode:PropagationMode = PropagationMode.NOT_SET


class _Result(ct.Structure):
    _fields_ = [
        ('propagation_mode', ct.c_int),
        ('warnings', ct.c_int),
        ('d__km', ct.c_double),
        ('A__db', ct.c_double),
        ('A_fs__db', ct.c_double),
        ('A_a__db', ct.c_double),
        ('theta_h1__rad', ct.c_double)
    ]


def great_circle_distance(theta_elev_deg: float, hr1_mamsl: float, hr2_mamsl: float) -> float:
    """
    ITU-R P.528-5, Annex 2, Section 1.

    Computes the great-circle distance between two terminals, in km.

    Args:
        theta_elev_deg (float): Free space elevation angle of the low terminal to the high terminal
            (degrees).
        hr1_mamsl (float): Height of the low terminal (meters above mean sea level).
        hr2_mamsl (float): Height of the high terminal (meters above mean sea level).

    Returns:
        d (float): Great-circle distance between the terminals (km).
    """
    theta_elev_rad = radians(theta_elev_deg)
    hr1_km = hr1_mamsl/1000.0
    hr2_km = hr2_mamsl/1000.0
    phi_rad = asin(((6371.0+hr1_km)/(6371.0+hr2_km))*cos(theta_elev_rad)) # Earth central angle
    theta_ca_rad = (pi/2.0) - theta_elev_rad - phi_rad
    d_km = 6371.0*theta_ca_rad
    return d_km


def basic_transmission_loss(f_mhz: float, p_percent: float, d_km: float, hr1_mamsl: float,
                            hr2_mamsl: float, pol: Polarization) -> Results:
    """
    ITU-R P.528-5, Annex 2, Section 3.

    Computes the basic transmission loss, in dB.

    Args:
        f_mhz (float): Frequency (MHz), with 100 <= f_mhz <= 30000.
        p_percent (float): Time percentage (%), with 1 <= p_percent <= 99.
        d_km (float): Great-circle path distance between terminals (km), with 0 <= d_km.
        hr1_mamsl (float): Height of the low terminal (meters above mean sea level),
            with 1.5 <= hr1_mamsl <= 20000.
        hr2_mamsl (float): Height of the high terminal (meters above mean sea level),
            with 1.5 <= hr2_mamsl <= 20000, and with hr1_mamsl <= hr2_mamsl.
        pol (Polarization): Parameter indicating either horizontal or vertical linear
            polarization.

    Returns:
        Results: Object of type Results containing the basic transmission loss value (dB) and
            other intermediate results. See the Results class definition for more details.
    """
    _result = _Result()
    cdll = _p528_5_dso_shared['cdll']
    ret_int = cdll.P528(d_km, hr1_mamsl, hr2_mamsl, f_mhz, pol.value, p_percent, ct.byref(_result))

    ret = _ReturnCode(ret_int)
    if ret != _ReturnCode.SUCCESS and ret != _ReturnCode.SUCCESS_WITH_WARNINGS:
        err_msgs = {
            _ReturnCode.ERROR_VALIDATION__D_KM: 'd_km is out of range.',
            _ReturnCode.ERROR_VALIDATION__H_1: 'hr1_mamsl is out of range.',
            _ReturnCode.ERROR_VALIDATION__H_2: 'hr2_mamsl is out of range.',
            _ReturnCode.ERROR_VALIDATION__TERM_GEO: 'hr2_mamsl must be greater than or equal to ' \
                'hr1_mamsl.',
            _ReturnCode.ERROR_VALIDATION__F_MHZ_LOW: 'f_mhz is out of range (too low).',
            _ReturnCode.ERROR_VALIDATION__F_MHZ_HIGH: 'f_mhz is out of range (too high).',
            _ReturnCode.ERROR_VALIDATION__PERCENT_LOW: 'p_percent is out of range (too low).',
            _ReturnCode.ERROR_VALIDATION__PERCENT_HIGH: 'p_percent is out of range (too high).',
            _ReturnCode.ERROR_VALIDATION__POLARIZATION: 'Invalid value for pol.',
            _ReturnCode.ERROR_HEIGHT_AND_DISTANCE: 'Terminals are occupying the same point in ' \
                'space (they are the same height and 0 km apart).'
        }
        raise ValueError(err_msgs[ret])

    results = Results()
    results.a_db = float(_result.A__db)
    results.warnings = int(_result.warnings)
    results.d_km = float(_result.d__km)
    results.afs_db = float(_result.A_fs__db)
    results.aa_db = float(_result.A_a__db)
    results.thetah1_rad = float(_result.theta_h1__rad)
    results.propag_mode = PropagationMode(int(_result.propagation_mode))

    return results


def _load_p528_5_dynamic_library() -> ct.CDLL:
    lib = _bu.get_dynamic_library('p528_5')
    _set_args_and_return_ctypes(lib)
    return lib


def _set_args_and_return_ctypes(lib):
    lib.P528.argtypes = [ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_int, ct.c_double,
                         ct.POINTER(_Result)]
    lib.P528.restype = ct.c_int


_p528_5_dso_shared = {
    'cdll': _load_p528_5_dynamic_library()
}
