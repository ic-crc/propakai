# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.1511-3.

P.1511 : Topography for Earth-space propagation modelling.

https://www.itu.int/rec/R-REC-P.1511/en
"""

from os.path import join
from math import radians, degrees, sqrt, sin, cos, atan2, atan, tan
from threading import Lock
from array import array
from filelock import FileLock
from propakai import _download_utils as _du
from propakai import p1144_13


__all__ = ['topographic_height',
           'WGS84_ELLIPSOID_SEMI_MAJOR_AXIS_KM',
           'WGS84_ELLIPSOID_FLATTENING_FACTOR',
           'AVG_EARTH_RADIUS_KM',
           'geocentric_earth_radius',
           'geodetic_to_geocentric_latitude',
           'geocentric_to_geodetic_latitude',
           'geoid_undulation',
           'geodetic_to_aer']


def topographic_height(lat: float, lon: float) -> float:
    """
    ITU-R P.1511-3, Annex 1, Section 1.1.

    Gets the topographic height of the surface of the Earth above mean sea level (m).

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        float: The topographic height of the surface of the Earth above mean sea level (m).
    """
    # lat from +90.125 to -90.125, lon from -180.125 to +180.125
    lat_interval = 1/12
    lon_interval = 1/12
    num_rows = 2164 # (180.250/(1/12))+1
    row_size = 4324 # (360.250/(1/12))+1

    r = (90.125 - lat) / lat_interval
    c = (180.125 + lon) / lon_interval
    arr = _thread_safe_get_topo_array()
    return p1144_13.bicubic_interpolation(arr, num_rows, row_size, r, c)


# ITU-R P.1511-3, Annex 1, Section 2.1.
WGS84_ELLIPSOID_SEMI_MAJOR_AXIS_KM: float = 6378.137
"""Semi-majar axis of WGS84 reference ellipsoid (km)."""

WGS84_ELLIPSOID_FLATTENING_FACTOR: float = 1/298.257223563
"""Flattening factor of WGS84 reference ellipsoid."""

AVG_EARTH_RADIUS_KM: float = 6371.0
"""Average Earth radius (km)."""


def geocentric_earth_radius(geodetic_lat: float) -> float:
    """
    ITU-R P.1511-3, Annex 1, Section 2.1.

    Computes the geocentric Earth radius (km) at the specified geodetic latitude.

    Args:
        geodetic_lat (float): Geodetic latitude (degrees).

    Returns:
        R (float): Geocentric Earth radius (km) at the specified geodetic latitude.
    """
    a = WGS84_ELLIPSOID_SEMI_MAJOR_AXIS_KM
    f = WGS84_ELLIPSOID_FLATTENING_FACTOR
    b = a*(1-f)
    cos_lat = cos(radians(geodetic_lat))
    sin_lat = sin(radians(geodetic_lat))
    num = a*a*a*a*cos_lat*cos_lat + b*b*b*b*sin_lat*sin_lat
    denom = a*a*cos_lat*cos_lat + b*b*sin_lat*sin_lat
    r_km = sqrt(num/denom)
    return r_km


def geodetic_to_geocentric_latitude(geodetic_lat: float) -> float:
    """
    ITU-R P.1511-3, Annex 1, Section 2.1.

    For a location on the surface of the WGS 84 reference ellipsoid, converts a geodetic latitude
    to a geocentric latitude.

    Args:
        geodetic_lat (float): Geodetic latitude (degrees).

    Returns:
        float: Geocentric latitude (degrees).
    """
    f = WGS84_ELLIPSOID_FLATTENING_FACTOR
    geocentric_lat_rad = atan((1-f)*(1-f)*tan(radians(geodetic_lat)))
    return degrees(geocentric_lat_rad)


def geocentric_to_geodetic_latitude(geocentric_lat: float) -> float:
    """
    ITU-R P.1511-3, Annex 1, Section 2.1.

    For a location on the surface of the WGS 84 reference ellipsoid, converts a geocentric latitude
    to a geodetic latitude.

    Args:
        geocentric_lat (float): Geocentric latitude (degrees).

    Returns:
        float: Geodetic latitude (degrees).
    """
    f = WGS84_ELLIPSOID_FLATTENING_FACTOR
    geodetic_lat_rad = atan(tan(radians(geocentric_lat))/((1-f)*(1-f)))
    return degrees(geodetic_lat_rad)


def geoid_undulation(lat: float, lon: float) -> float:
    """
    ITU-R P.1511-3, Annex 1, Section 2.2.

    The height difference between the WGS 84 geoid and the WGS 84 ellipsoid is the geoid
    undulation, defined by the 2008 version of the U.S. National Geospatial-Intelligence Agency
    (NGA) Earth Gravitational Model, EGM2008.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        h_EGM2008 (float): The geoid undulation (m).
    """
    # lat from +90.166667 to -90.166667, lon from -180.166667 to +180.166667
    lat_interval = 1/12
    lon_interval = 1/12
    num_rows = 2165 # (180.33333/(1/12))+1
    row_size = 4325 # (360.33333/(1/12))+1

    r = (90+(1/6) - lat) / lat_interval
    c = (180+(1/6) + lon) / lon_interval
    arr = _thread_safe_get_egm2008_array()
    return p1144_13.bicubic_interpolation(arr, num_rows, row_size, r, c)


def geodetic_to_aer(latg: float, long: float, hg_km: float,
                    lats: float, lons: float, hs_km: float
                    ) -> tuple[float, float, float]:
    """
    ITU-R P.1511-3, Annex 1, Section 3.

    Free-space look angles and free-space slant range between two stations in geodetic coordinates
    (AER: azimuth-elevation-range).

    Args:
        latg (float): Origin geodetic latitude (degrees), with -90 <= lat <= 90.
        long (float): Origin longitude (degrees), with -180 <= lon <= 180.
        hg_km (float): Origin height above mean sea level (e.g. above the WGS 84 reference
            ellipsoid) (km).
        lats (float): Target geodetic latitude (degrees), with -90 <= lat <= 90.
        lons (float): Target longitude (degrees), with -180 <= lon <= 180.
        hs_km (float): Target height above mean sea level (e.g. above the WGS 84 reference
            ellipsoid) (km).
    
    Returns:
        a (float): Free-space geodetic azimuth angle from the origin location to the target
            location, measured clockwise from geodetic north (degrees).
        v (float): Free-space geodetic elevation (i.e. the vertical) angle from the origin
            location to the target location (degrees).
        R (float): Free-space slant range between the origin location and target location (km).
    """
    a = WGS84_ELLIPSOID_SEMI_MAJOR_AXIS_KM
    f = WGS84_ELLIPSOID_FLATTENING_FACTOR

    # Step 1
    sin_latg = sin(radians(latg))
    cos_latg = cos(radians(latg))
    sin_long = sin(radians(long))
    cos_long = cos(radians(long))
    sin_lats = sin(radians(lats))
    cos_lats = cos(radians(lats))
    sin_lons = sin(radians(lons))
    cos_lons = cos(radians(lons))
    ng = a/sqrt(1-(2*f-f*f)*sin_latg*sin_latg)
    ns = a/sqrt(1-(2*f-f*f)*sin_lats*sin_lats)
    xg = (ng+hg_km)*cos_latg*cos_long
    yg = (ng+hg_km)*cos_latg*sin_long
    zg = (ng*(1-f)*(1-f)+hg_km)*sin_latg
    xs = (ns+hs_km)*cos_lats*cos_lons
    ys = (ns+hs_km)*cos_lats*sin_lons
    zs = (ns*(1-f)*(1-f)+hs_km)*sin_lats
    x = xs-xg
    y = ys-yg
    z = zs-zg

    # Step 2
    e = -sin_long*x + cos_long*y
    n = -sin_latg*cos_long*x + -sin_latg*sin_long*y + cos_latg*z
    u = cos_latg*cos_long*x + cos_latg*sin_long*y + sin_latg*z

    # Step 3
    v_deg = degrees(atan2(u, sqrt(e*e+n*n)))
    alpha_deg = degrees(atan2(e, n))
    if alpha_deg < 0:
        alpha_deg += 360
    r_km = sqrt(x*x + y*y + z*z)

    return (alpha_deg, v_deg, r_km)


def _thread_safe_get_topo_array() -> array:
    return _thread_safe_get_digital_map_array('topo_lock', 'topo_array', 'TOPO.dat')


def _thread_safe_get_egm2008_array() -> array:
    return _thread_safe_get_digital_map_array('egm2008_lock', 'egm2008_array', 'EGM2008.txt')


def _thread_safe_get_digital_map_array(lock_key: str, array_key: str, filename: str) -> array:
    arr = _p1511_3_shared[array_key]
    if arr is not None:
        return arr
    with _p1511_3_shared[lock_key]:
        arr = _p1511_3_shared[array_key] # re-read under lock
        if arr is None:
            try:
                arr = _load_digital_map(filename)
            except FileNotFoundError:
                _download_rec_data()
                arr = _load_digital_map(filename)
            _p1511_3_shared[array_key] = arr # only assign when load completed successfully
    return arr


def _load_digital_map(filename: str) -> array:
    return p1144_13.load_digital_map(join(_du.install_dir(), _p1511_3_shared['DATA_DIR'],
                                          filename))


def _download_rec_data() -> None:
    data_dir = _p1511_3_shared['DATA_DIR']
    full_path_data_dir = join(_du.install_dir(), data_dir)
    filenames = ['TOPO.dat', 'EGM2008.txt']
    lock = FileLock(_du.get_lockfile_pathname(data_dir))
    with lock:
        if _du.files_all_exist(full_path_data_dir, filenames) is False:
            url = 'https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.1511-3-202408-I!!ZIP-E.zip'
            zip_pathname1 = _du.download(url, full_path_data_dir)
            zip_pathname2 = _du.extract_files(zip_pathname1, ['R-REC-P1511-3-1.zip'],
                                              create_dirs=True, delete_zip_archive=False)[0]
            _du.extract_files(zip_pathname2, ['TOPO.dat'], create_dirs=True,
                              delete_zip_archive=True)
            zip_pathname3 = _du.extract_files(zip_pathname1, ['R-REC-P1511-3-2.zip'],
                                              create_dirs=True, delete_zip_archive=True)[0]
            _du.extract_files(zip_pathname3, ['EGM2008.txt'], create_dirs=True,
                              delete_zip_archive=True)
            _du.print_notice()
        else:
            _du.print_already_installed(full_path_data_dir, filenames)


_p1511_3_shared = {
    'DATA_DIR': 'p1511_3',
    'topo_lock': Lock(),
    'topo_array': None,
    'egm2008_lock': Lock(),
    'egm2008_array': None
}
