# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.1812-8, dynamic shared object version (i.e. using a compiled binary).

P.1812 : A path-specific propagation prediction method for point-to-area terrestrial services in
the frequency range 30 MHz to 6 GHz.

https://www.itu.int/rec/R-REC-P.1812/en
"""

from os.path import join
import ctypes as ct
from filelock import FileLock
from propakai import _bin_utils as _bu
from propakai import _download_utils as _du
from propakai import types
from propakai import _types_utils as _tu
from propakai.p1812_8 import RadioClimaticZone, ClutterCategory


__all__ = ['RadioClimaticZone',
           'ClutterCategory',
           'basic_transmission_loss',
           'field_strength']


def basic_transmission_loss(f_ghz: float, p_percent: float, pl_percent: float, latt: float,
                            lont: float, latr: float, lonr: float, htg_m: float, hrg_m: float,
                            vpol: bool, d_km: types.FloatArray, h_mamsl: types.FloatArray,
                            cc: types.IntArray|None=None, rch_m: types.FloatArray|None=None,
                            sh_mamsl: types.FloatArray|None=None, rcz: types.IntArray|None=None,
                            dct_km: float|None=None, dcr_km: float|None=None,
                            delta_n: float|None=None, n0: float|None=None, wa_m: float=100.0
                            ) -> float:
    """
    The basic transmission loss not exceeded for p_percent time and pl_percent locations.

    Args:
        f_ghz (float): Frequency (GHz), with 0.03 <= f_ghz <= 6.0.
        p_percent (float): Percentage of average year for which the calculated basic transmission
            loss is not exceeded (%), with 1.0 <= p_percent <= 50.0.
        pl_percent (float): Percentage of locations for which the calculated basic transmission
            loss is not exceeded (%), with 1.0 <= pl_percent <= 99.0.
        latt (float): Latitude of transmitter (degrees), with -80 <= latt <= 80.
        lont (float): Longitude of transmitter (degrees), with -180 <= lont <= 180.
        latr (float): Latitude of receiver (degrees), with -80 <= latr <= 80.
        lonr (float): Longitude of receiver (degrees), with -180 <= lonr <= 180.
        htg_m (float): Transmit antenna centre height above ground level (m), with
            1 <= htg_m <= 3000.
        hrg_m (float): Receive antenna centre height above ground level (m), with
            1 <= htr_m <= 3000.
        vpol (bool): True to indicate vertical polarization, False to indicate horizontal
            polarization.
        d_km (types.FloatArray): Distance from transmitter profile of n points (km), with 3 <= n.
        h_mamsl (types.FloatArray): Terrain height profile of n points (m above mean sea level).
        cc (types.IntArray|None, optional): Clutter category profile of n points (1=Water/Sea,
            2=Open/Rural, 3=Suburban, 4=Urban/Trees/Forest, 5=Dense Urban). cc is ignored when
            either rch_m or sh_mamsl is specfied, otherwise Open/Rural is assumed everywhere when
            cc is set to None.
        rch_m (types.FloatArray|None, optional): Representative clutter height (m) profile of n
            points. rch_m is ignored if sh_mamsl is specified.
        sh_mamsl (types.FloatArray|None, optional): Surface height (m above mean sea level) profile
            of n points.
        rcz (types.IntArray|None, optional): Radio climatic zone profile of n points (1=Sea,
            3=Coastal Land, 4=Inland). Inland is assumed everywhere when rcz is set to None.
        dct_km (float|None, optional): Distance of the transmitter from the coast (km), in the
            direction of the other terminal. For a terminal on a ship or sea platform the distance
            is zero. When set to None, dct_km is automatically estimated using the radio climate
            zone (rcz) and distance (d_km) profiles.
        dcr_km (float|None, optional): Distance of the receiver from the coast (km), in the
            direction of the other terminal. For a terminal on a ship or sea platform the distance
            is zero. When set to None, dcr_km is automatically estimated using the radio climate
            zone (rcz) and distance (d_km) profiles.
        delta_n (float|None, optional): Average radio-refractivity lapse-rate through the lowest 1
            km of the atmosphere (N-units/km). When set to None, delta_n is automatically obtained
            using one of the recommendation's digital map at mid-distance between latt/lont and
            latr/lonr.
        n0 (float|None, optional): Sea-level surface refractivity (N-units). When set to None, n0
            is automatically obtained using one of the recommendation's digital map at mid-distance
            between latt/lont and latr/lonr.
        wa_m (float, optional): Prediction resolution (m), the width of the square area over which
            the location variability applies. Default value is 100 m.

    Returns:
        Lb (float): The basic transmission loss (dB) not exceeded for p_percent time and pl_percent
            locations.
    """
    d_ptr, n, _d_backing = _tu.to_c_double_ptr(d_km)
    if n < 3:
        raise ValueError('d_km must have at least 3 elements.')
    h_ptr, _n, _h_backing = _tu.to_c_double_ptr(h_mamsl, n)
    cc_ptr, _n, _cc_backing = _tu.to_c_int_ptr(cc, n)
    rch_ptr, _n, _rch_backing = _tu.to_c_double_ptr(rch_m, n)
    sh_ptr, _n, _sh_backing = _tu.to_c_double_ptr(sh_mamsl, n)
    rcz_ptr, _n, _rcz_backing = _tu.to_c_int_ptr(rcz, n)
    cdll = _p1812_8_dso_shared['cdll']
    AUTOMATIC = cdll.P1812_8_AUTO_CONSTANT()
    if dct_km is None:
        dct_km = AUTOMATIC
    if dcr_km is None:
        dcr_km = AUTOMATIC
    if delta_n is None:
        delta_n = AUTOMATIC
    if n0 is None:
        n0 = AUTOMATIC
    lb_db = cdll.P1812_8_BasicTransmissionloss(
        f_ghz, p_percent, pl_percent, latt, lont, latr, lonr, htg_m, hrg_m, vpol,
        n, d_ptr, h_ptr, cc_ptr, rch_ptr, sh_ptr, rcz_ptr,
        dct_km, dcr_km, delta_n, n0, wa_m
    )
    return lb_db


def field_strength(f_ghz: float, lb_db: float) -> float:
    """
    The field strength exceeded for p_percent time and pl_percent locations.

    Args:
        f_ghz (float): Frequency (GHz), with 0.03 <= f_ghz <= 6.0.
        lb_db (float): Basic transmission loss (dB), obtained from the basic_transmission_loss()
            function.

    Returns:
        Ep (float): The field strength normalized to 1 kW effective radiated power exceeded for
            p_percent time and pl_percent locations (dBuVm).
    """
    cdll = _p1812_8_dso_shared['cdll']
    return cdll.P1812_8_FieldStrength(f_ghz, lb_db)


def _download_rec_data(data_dir: str) -> None:
    full_path_data_dir = join(_du.install_dir(), data_dir)
    filenames = ['DN50.TXT', 'N050.TXT']
    lock = FileLock(_du.get_lockfile_pathname(data_dir))
    with lock:
        if _du.files_all_exist(full_path_data_dir, filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.1812-8-202509-I!!ZIP-E.zip'
            zip_pathname = _du.download(url, full_path_data_dir)
            _du.extract_files(zip_pathname, filenames, create_dirs=True, delete_zip_archive=True)
            _du.print_notice()


def _init_dynamic_library() -> ct.CDLL:
    lib = _bu.get_dynamic_library('propakai_cpp')
    _set_args_and_return_ctypes(lib)
    data_dir = 'p1812_8'
    _download_rec_data(data_dir)
    dn50_pathname = join(_du.install_dir(), data_dir, 'DN50.TXT')
    n050_pathname = join(_du.install_dir(), data_dir, 'N050.TXT')
    if lib.P1812_8_Load_DN50_DigitalMap(dn50_pathname.encode()) is False:
        print('Failed to load DN50.TXT')
    if lib.P1812_8_Load_N050_DigitalMap(n050_pathname.encode()) is False:
        print('Failed to load N050.TXT')
    return lib


def _set_args_and_return_ctypes(lib):
    lib.P1812_8_Load_DN50_DigitalMap.argtypes = [ct.c_char_p]
    lib.P1812_8_Load_DN50_DigitalMap.restype = ct.c_bool

    lib.P1812_8_Load_N050_DigitalMap.argtypes = [ct.c_char_p]
    lib.P1812_8_Load_N050_DigitalMap.restype = ct.c_bool

    lib.P1812_8_AUTO_CONSTANT.argtypes = []
    lib.P1812_8_AUTO_CONSTANT.restype = ct.c_double

    lib.P1812_8_FieldStrength.argtypes = [ct.c_double, ct.c_double]
    lib.P1812_8_FieldStrength.restype = ct.c_double

    lib.P1812_8_BasicTransmissionloss.argtypes = [
        ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double,
        ct.c_double, ct.c_double, ct.c_bool, ct.c_uint, ct.POINTER(ct.c_double),
        ct.POINTER(ct.c_double), ct.POINTER(ct.c_int), ct.POINTER(ct.c_double),
        ct.POINTER(ct.c_double), ct.POINTER(ct.c_int), ct.c_double, ct.c_double, ct.c_double,
        ct.c_double, ct.c_double]
    lib.P1812_8_BasicTransmissionloss.restype = ct.c_double


_p1812_8_dso_shared = {
    'cdll': _init_dynamic_library()
}
