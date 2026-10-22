# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Additional topography related functionalities in support for using ITU-R P. recommendations.

The topography module requires **rasterio** (for GeoRasterDirectoryReader), **geopandas** and
**shapely** (for radio climatic zone functions) to be installed. If they are not already, you may
do so with:
```bash
python -m pip install rasterio geopandas shapely
```
"""

import os
from array import array
from math import floor, isnan, atan, degrees
from enum import Enum
from .. import types
from .. import p2001_6 as p2001
from ..geo_catalog import gc_idwm


__all__ = ['distance_profile_km',
           'distance_profile_m',
           'lat_lon_profile',
           'radio_climatic_zone3_profile',
           'radio_climatic_zone4_profile',
           'is_line_of_sight',
           'horizon_elevation_angles',
           'GeoRasterDirectoryReader']


class _DistUnit(Enum):
    METER     = 1
    KILOMETER = 2


def distance_profile_km(lat0: float, lon0: float, lat1: float, lon1: float, res_m: float,
                        min_num_pts: int=3, max_num_pts: int|None=None) -> array:
    """
    Generates a great-circle distance profile (km) of evenly spaced points between two specified
    geographical locations on the surface of the Earth.

    Args:
        lat0 (float): Latitude of first point (degrees), with -90 <= lat0 <= 90.
        lon0 (float): Longitude of first point (degrees), with -180 <= lon0 <= 180.
        lat1 (float): Latitude of second point (degrees), with -90 <= lat1 <= 90.
        lon1 (float): Longitude of second point (degrees), with -180 <= lon1 <= 180.
        res_m (float): Desired resolution (meters), with res_m > 0. The distance profile will be
            spaced by approximately res_m meters between points.
        min_num_pts (int, optional): Minimum number of points in the returned profile, with
            min_num_pts >= 2. Default is 3.
        max_num_pts (int|None, optional): Maximum number of points allowed in the profile, with
            max_num_pts >= min_num_pts. No limit when set to None. Default is None.

    Returns:
        profile_km (array): An array of type 'd' containing the great-circle distances (km) of
            evenly spaced points between the two specified coordinates.
    """
    return _distance_profile(lat0, lon0, lat1, lon1, res_m, min_num_pts, max_num_pts,
                             _DistUnit.KILOMETER)


def distance_profile_m(lat0: float, lon0: float, lat1: float, lon1: float, res_m: float,
                       min_num_pts: int=3, max_num_pts: int|None=None) -> array:
    """
    Generates a great-circle distance profile (m) of evenly spaced points between two specified
    geographical locations on the surface of the Earth.

    Args:
        lat0 (float): Latitude of first point (degrees), with -90 <= lat0 <= 90.
        lon0 (float): Longitude of first point (degrees), with -180 <= lon0 <= 180.
        lat1 (float): Latitude of second point (degrees), with -90 <= lat1 <= 90.
        lon1 (float): Longitude of second point (degrees), with -180 <= lon1 <= 180.
        res_m (float): Desired resolution (meters), with res_m > 0. The distance profile will be
            spaced by approximately res_m meters between points.
        min_num_pts (int, optional): Minimum number of points in the returned profile, with
            min_num_pts >= 2. Default is 3.
        max_num_pts (int|None, optional): Maximum number of points allowed in the profile, with
            max_num_pts >= min_num_pts. No limit when set to None. Default is None.

    Returns:
        profile_m (array): An array of type 'd' containing the great-circle distances (m) of evenly
            spaced points between the two specified coordinates.
    """
    return _distance_profile(lat0, lon0, lat1, lon1, res_m, min_num_pts, max_num_pts,
                             _DistUnit.METER)


def _distance_profile(lat0: float, lon0: float, lat1: float, lon1: float, res_m: float,
                     min_num_pts: int, max_num_pts: int|None, units:_DistUnit) -> array:
    if res_m <= 0:
        raise ValueError('res_m is out of range.')
    if min_num_pts < 2:
        raise ValueError('min_num_pts is out of range.')
    path_length_km = p2001.path_length(lat0, lon0, lat1, lon1)
    num_pts = 1 + int((path_length_km*1000/res_m) + 1)
    num_pts = max(min_num_pts, num_pts)
    if max_num_pts is not None:
        if max_num_pts < min_num_pts:
            raise ValueError('max_num_pts is out of range.')
        num_pts = min(max_num_pts, num_pts)
    step_km = path_length_km / (num_pts - 1)
    if units == _DistUnit.KILOMETER:
        return array('d', [i*step_km for i in range(num_pts)])
    elif units == _DistUnit.METER:
        return array('d', [i*step_km*1000 for i in range(num_pts)])
    else:
        raise ValueError('Invalid value for units.')


def lat_lon_profile(lat0: float, lon0: float, lat1: float, lon1: float, res_m: float,
                    min_num_pts: int=3, max_num_pts: int|None=None) -> list[tuple[float, float]]:
    """
    Generates a latitude/longitude profile (degrees) of evenly spaced points using a great-circle
    distance algorithm, between two specified geographical locations on the surface of the Earth.

    Note: Calling `distance_profile()` and `lat_lon_profile()` with the same input parameters
    yields profiles for the same corresponding points.

    Args:
        lat0 (float): Latitude of first point (degrees), with -90 <= lat0 <= 90.
        lon0 (float): Longitude of first point (degrees), with -180 <= lon0 <= 180.
        lat1 (float): Latitude of second point (degrees), with -90 <= lat1 <= 90.
        lon1 (float): Longitude of second point (degrees), with -180 <= lon1 <= 180.
        res_m (float): Desired resolution (meters), with res_m > 0. The lat/lon profile will be
            spaced by approximately res_m meters between points.
        min_num_pts (int, optional): Minimum number of points in the returned profile, with
            min_num_pts >= 2. Default is 3.
        max_num_pts (int|None, optional): Maximum number of points allowed in the profile, with
            max_num_pts >= min_num_pts. No limit when set to None. Default is None.

    Returns:
        profile (list[tuple[float, float]]): A list of (latitude, longitude) tuples of evenly
            spaced points between the two specified coordinates.
    """
    dist_profile_km = distance_profile_km(lat0, lon0, lat1, lon1, res_m, min_num_pts, max_num_pts)
    lat_lon_list = []
    for d_km in dist_profile_km:
        lat_lon_tuple = p2001.intermediate_path_point(lat0, lon0, lat1, lon1, d_km)
        lat_lon_list.append(lat_lon_tuple)
    return lat_lon_list


def radio_climatic_zone3_profile(coords: list[tuple[float, float]]) -> array:
    """
    Generates a radio-climatic zone profile for a list of geographic coordinates.  
    The zone is represented as an integer with 3 possible values:  
    1 (SEA), 3 (COASTAL_LAND), 4 (INLAND).

    Args:
        coords (list[tuple[float, float]]): List of (latitude, longitude) tuples, in degrees, for
            which to determine the radio-climatic zone.
            
    Returns:
        profile (array): An array of type 'i' containing the radio-climatic zone integer values
            corresponding to each input coordinate.
    """
    int_array = array('i', [0] * len(coords))
    for i, lat_lon_tuple in enumerate(coords):
        zone3 = gc_idwm.radio_climatic_zone3(lat=lat_lon_tuple[0], lon=lat_lon_tuple[1]).value
        int_array[i] = zone3
    return int_array


def radio_climatic_zone4_profile(coords: list[tuple[float, float]]) -> array:
    """
    Generates a radio-climatic zone profile for a list of geographic coordinates.  
    The zone is represented as an integer with 4 possible values:  
    1 (B_COLD_SEA), 2 (C_WARM_SEA), 3 (A1_COASTAL_LAND), 4 (A2_INLAND).

    Args:
        coords (list[tuple[float, float]]): List of (latitude, longitude) tuples, in degrees, for
            which to determine the radio-climatic zone.
            
    Returns:
        profile (array): An array of type 'i' containing the radio-climatic zone integer values
            corresponding to each input coordinate.
    """
    int_array = array('i', [0] * len(coords))
    for i, lat_lon_tuple in enumerate(coords):
        zone4 = gc_idwm.radio_climatic_zone4(lat=lat_lon_tuple[0], lon=lat_lon_tuple[1]).value
        int_array[i] = zone4
    return int_array


def _elev_angle_from_p2001(h_from_mamsl, h_to_mamsl, dist_km, ae_km) -> float:
    """
    Returns the elevation angle (mrad) relative to the horizontal.
    ITU-R P.2001-6, Annex, Section 3.7.
    """
    return ((h_to_mamsl-h_from_mamsl)/dist_km)-(500*dist_km/ae_km) # eq. (16) without max


def _elev_angle_from_p1812(h_from_mamsl, h_to_mamsl, dist_km, ae_km) -> float:
    """
    Returns the elevation angle (mrad) relative to the horizontal, using equation from
    ITU-R P.1812-7, Annex 1, Section 4.
    """
    return 1000.0*atan(((h_to_mamsl-h_from_mamsl)/(1000.0*dist_km))-(dist_km/(2.0*ae_km)))


def is_line_of_sight(latt: float, lont: float, ht_mamsl: float,
                     latr: float, lonr: float, hr_mamsl: float,
                     dp_km: types.FloatArray, hp_mamsl: types.FloatArray) -> bool:
    """
    Determines whether a path is line-of-sight or non-line-of-sight under median refractivity
    conditions.

    Args:
        latt (float): Latitude of transmitter (degrees), with -90 <= lat <= 90.
        lont (float): Longitude of transmitter (degrees), with -180 <= lon <= 180.
        ht_mamsl (float): Transmitter height (meters above mean sea level).
        latr (float): Latitude of receiver (degrees), with -90 <= lat <= 90.
        lonr (float): Longitude of receiver (degrees), with -180 <= lon <= 180.
        hr_mamsl (float): Receiver height (meters above mean sea level).
        dp_km (types.FloatArray): Great-circle distance from transmitter (km) profile.
        hp_mamsl (types.FloatArray): Terrain height profile (meters above mean sea level) from the
            transmitter to the receiver. hp_mamsl and dp_km must have the same number of items.
    
    Returns:
        is_los (bool): True when the path is line-of-sight, False otherwise.
    """
    # Alogorithm mainly based on ITU-R P.2001-6, Annex, Section 3.7.
    path_length_km = dp_km[-1]
    Re_km = 6371 # average Earth radius (km)
    n = len(dp_km)
    mid_path_lat, mid_path_lon = p2001.intermediate_path_point(latt, lont, latr, lonr,
                                                               path_length_km/2.0)
    ae_km = 157*Re_km/(157+p2001._N_d1km50(mid_path_lat, mid_path_lon))
    theta_tr = _elev_angle_from_p2001(ht_mamsl, hr_mamsl, path_length_km, ae_km)
    theta_tim = -1E20
    for i in range(1, n-1):
        theta_tim_i = _elev_angle_from_p2001(ht_mamsl, hp_mamsl[i], dp_km[i], ae_km)
        theta_tim = max(theta_tim, theta_tim_i)
    # NOTE: Using _elev_angle_from_p2001() or _elev_angle_from_p1812() yields the same LOS/NLOS
    #       result since the angle comparison is consistent.
    return theta_tim < theta_tr


def horizon_elevation_angles(latt: float, lont: float, ht_mamsl: float,
                             latr: float, lonr: float, hr_mamsl: float,
                             dp_km: types.FloatArray, hp_mamsl: types.FloatArray
                             ) -> tuple[float, float]:
    """
    Calculates the transmitter and receiver horizon elevation angles (degrees) under median
    refractivity conditions.

    Args:
        latt (float): Latitude of transmitter (degrees), with -90 <= lat <= 90.
        lont (float): Longitude of transmitter (degrees), with -180 <= lon <= 180.
        ht_mamsl (float): Transmitter height (meters above mean sea level).
        latr (float): Latitude of receiver (degrees), with -90 <= lat <= 90.
        lonr (float): Longitude of receiver (degrees), with -180 <= lon <= 180.
        hr_mamsl (float): Receiver height (meters above mean sea level).
        dp_km (types.FloatArray): Great-circle distance from transmitter (km) profile.
        hp_mamsl (types.FloatArray): Terrain height profile (meters above mean sea level) from the
            transmitter to the receiver. hp_mamsl and dp_km must have the same number of items.
    
    Returns:
        theta_t (float): Transmitter horizon elevation angle relative to its local horizontal
            (degrees). 0°=horizon, +90°=zenith, -90°=nadir.
        theta_r (float): Receiver horizon elevation angle relative to its local horizontal
            (degrees). 0°=horizon, +90°=zenith, -90°=nadir.
    """
    # Algoritghm mainly based on ITU-R P.2001-6, Annex, Section 3.7.

    # NOTE: Alternately, use _elev_angle to strictly stick with the P.2001-6 recommendation. Using
    #       elevation angle equation from P.1812 yields accurate results even at short distances
    #       not covered by the P.2001-6 recommendation.
    elev_angle_func = _elev_angle_from_p1812

    path_length_km = dp_km[-1]
    Re_km = 6371
    n = len(dp_km)
    mid_path_lat, mid_path_lon = p2001.intermediate_path_point(latt, lont, latr, lonr,
                                                               path_length_km/2.0)
    ae_km = 157*Re_km/(157+p2001._N_d1km50(mid_path_lat, mid_path_lon))
    theta_t = elev_angle_func(ht_mamsl, hr_mamsl, path_length_km, ae_km)
    theta_r = elev_angle_func(hr_mamsl, ht_mamsl, path_length_km, ae_km)
    for i in range(1, n-1):
        theta_t_i = elev_angle_func(ht_mamsl, hp_mamsl[i], dp_km[i], ae_km)
        theta_r_i = elev_angle_func(hr_mamsl, hp_mamsl[i], path_length_km-dp_km[i], ae_km)
        theta_t = max(theta_t, theta_t_i)
        theta_r = max(theta_r, theta_r_i)
    theta_t_deg = degrees(theta_t/1000) # convert from mrad to degrees
    theta_r_deg = degrees(theta_r/1000)
    return (theta_t_deg, theta_r_deg)


class GeoRasterDirectoryReader:
    """
    This class facilitates reading geospatial raster files—such as those containing terrain
    elevation, surface elevation, or clutter classification data—for a terrain profile or area that
    may span the geographical boundaries of multiple files.

    Note: When multiple files in the input directory cover the same geographic area, it is undefined
    which file will be selected; any one could be used.
    """

    def __init__(self, directory: str, recursive: bool=True, extensions: list[str]|None=None):
        """
        Initialize GeoRasterDirectoryReader.

        Args:
            directory (str): Directory containing geospatial raster files, typically of the same
                product.
            recursive (bool, optional): Whether to include subdirectories. Default is True.
            extensions (list[str]|None, optional): List of file extensions (e.g. ['.tif']). When
                specified, only files with the given extension(s) are considered. Default is None
                (i.e. all files considered).
        """
        self._directory = directory
        self._recursive = recursive
        self._extensions = extensions
        self._raster_infos = self._init_raster_infos(directory, recursive, extensions)


    def read_floats(self, coords: list[tuple[float, float]], bilinear_interpol: bool,
                    no_data_value: float= 0, band: int=1, low_memory: bool=False,
                    data_type: str='d') -> array:
        """
        Get data from geospatial raster files at the specified geographical coordinates.
        The result is returned as an array of floating-point values (default type is 'd').

        Args:
            coords (list[tuple[float, float]]): List of (latitude, longitude) tuples in degrees.
            bilinear_interpol (bool): Whether to apply bilinear interpolation using the four
                surrounding pixels. If False, nearest neighbor interpolation is used.
            no_data_value (float, optional): Value used in the returned array when no data
                could be obtained at a particular location. Default is 0.
            band (int, optional): The raster band to use when reading files. Default is 1.
            low_memory (bool, optional): If True, minimizes memory usage when reading files. If
                False, sections or entire files may be batch read and temporarily kept in memory,
                which improves performance for typical use cases but may degrade performance when
                'coords' values are geographically sparse. If sufficient memory is not available,
                the function automatically falls back to low_memory mode. Default is False.
            data_type (str, optional): Floating-point data type for the returned array, either 'd'
                or 'f'. Default is 'd'.

        Returns:
            flt_arr (array): An array (default type 'd') containing the extracted data values.
        """
        values = self._read_data(coords, bilinear_interpol, no_data_value, band, low_memory)
        if data_type in ['d', 'f']:
            flt_pt_array = array(data_type, values)
        else:
            raise ValueError('Invalid value for data_type.')
        return flt_pt_array


    def read_ints(self, coords: list[tuple[float, float]], bilinear_interpol: bool=False,
                  no_data_value: int= -1, band: int=1, low_memory: bool=False,
                  data_type: str='i') -> array:
        """
        Get data from geospatial raster files at the specified geographical coordinates.
        The result is returned as an array of integer values (default type is 'i').

        Args:
            coords (list[tuple[float, float]]): List of (latitude, longitude) tuples in degrees.
            bilinear_interpol (bool, optional): Whether to apply bilinear interpolation using the
                four surrounding pixels. If False, nearest neighbor interpolation is used. Default
                is False. Be careful not to bilinearly interpolate clutter classification data or
                other non-interpolable data.
            no_data_value (float, optional): Value used in the returned array when no data
                could be obtained at a particular location. Default is -1.
            band (int, optional): The raster band to use when reading files. Default is 1.
            low_memory (bool, optional): If True, minimizes memory usage when reading files. If
                False, sections or entire files may be batch read and temporarily kept in memory,
                which improves performance for typical use cases but may degrade performance when
                'coords' values are geographically sparse. If sufficient memory is not available,
                the function automatically falls back to low_memory mode. Default is False.
            data_type (str, optional): Integer data type for the returned array, one of 'b', 'B',
                'h', 'H', 'i', 'I', 'l', 'L', 'q', 'Q'. Default is 'i'. Raise an OverflowError
                exception when the extracted data cannot be represented by the specifed data_type.

        Returns:
            int_arr (array): An array (default type 'i') containing the extracted data values.
        """
        values = self._read_data(coords, bilinear_interpol, no_data_value, band, low_memory)
        if data_type in ['i','I','b','B','h','H','l','L','q','Q']:
            integer_array = array(data_type, [int(x) for x in values])
        else:
            raise ValueError('Invalid value for data_type.')
        return integer_array


    def _read_data(self, coords: list[tuple[float, float]], bilinear_interpol: bool,
                   no_data_value: float|int, band: int, low_memory: bool) -> list:
        """
        Get data from geospatial raster files at the specified geographical coordinates.
        The result is returned as a list.

        Args:
            coords (list[tuple[float, float]]): List of (latitude, longitude) tuples in degrees.
            bilinear_interpol (bool): Whether to apply bilinear interpolation using the four
                surrounding pixels. If False, nearest neighbor interpolation is used.
            no_data_value (float|int): Value used in the returned array when no data could be
                obtained at a particular location.
            band (int): The raster band to use when reading files.
            low_memory (bool): If True, minimizes memory usage when reading files. If
                False, sections or entire files may be batch read and temporarily kept in memory,
                which improves performance for typical use cases but may degrade performance when
                'coords' values are geographically sparse. If sufficient memory is not available,
                the function automatically falls back to low_memory mode. Default is False.

        Returns:
            list: A list containing the extracted data values.
        """
        needed_files = self._get_needed_files(coords)

        if len(needed_files) == 0:
            return [no_data_value]*len(coords)

        results = []
        for filepath in needed_files:
            if low_memory is True:
                file_results = self._read_raster_file(filepath, coords, bilinear_interpol, band)
            else:
                try:
                    file_results = self._read_raster_file_in_memory_window(filepath, coords,
                                                                           bilinear_interpol, band)
                except MemoryError:
                    file_results = self._read_raster_file(filepath, coords, bilinear_interpol, band)
            results.append(file_results)

        # merge result lists (one per file read) into a single list
        merged = []
        for items in zip(*results):
            value = None
            for item in items:
                if item is not None:
                    value = item
                    break
            merged.append(value)

        # replace any None value with no_data_value
        final_list = [no_data_value if x is None else x for x in merged]

        return final_list


    def _init_raster_infos(self, directory: str, recursive: bool, extensions: list[str]|None
                           ) -> list:
        """
        Get a list dictionaries (one per geospatial raster file), each containing a filepath and
        its geographical boundaries in EPSG:4536.

        Args:
            directory (str): Directory containing geospatial raster files.
            recursive (bool): Whether to include subdirectories
            extensions (list[str]|None): List of file extensions (e.g. ['.tif']). When specified,
                only files with the given extension(s) are considered.

        Returns:
            list: List of dictionaries with 'file' and 'bounds' (left, bottom, right, top) keys.
        """
        import rasterio
        from rasterio.warp import transform_bounds

        raster_infos = []
        filepaths = self._get_filepaths(directory, recursive, extensions)

        for f in filepaths:
            try:
                with rasterio.open(f) as src:
                    src_crs = src.crs
                    src_bounds = src.bounds  # (left, bottom, right, top)
                    if src_crs.to_string() != 'EPSG:4326':
                        # Convert bounds to EPSG:4326 (WGS84)
                        wgs_bounds = transform_bounds(src_crs, 'EPSG:4326', *src_bounds,
                                                      densify_pts=8)
                    else:
                        wgs_bounds = src_bounds
                    raster_infos.append({'file': f, 'bounds': wgs_bounds})
            except Exception as e: # pylint: disable=broad-exception-caught
                print(f'GeoRasterDirectoryReader: {e}')

        return raster_infos


    def _get_filepaths(self, directory: str, recursive: bool, extensions: list[str]|None
                       ) -> list[str]:
        """
        Get list of filepaths from the specified directory.
        
        Args:
            directory (str): Full directory path.
            recursive (bool): Whether to include subdirectories
            extensions (list[str]|None): List of file extensions (e.g. ['.tif']). When specified,
                only files with the given extension(s) are included in the returned list.
        
        Returns:
            list[str]: List of filepaths.
        """
        filepaths = []

        if extensions is not None:
            extensions_set = set(ext.lower() for ext in extensions)
        else:
            extensions_set = None

        if recursive:
            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    if extensions_set is not None:
                        _, ext = os.path.splitext(filename)
                        if ext.lower() not in extensions_set:
                            continue
                    full_path = os.path.join(dirpath, filename)
                    filepaths.append(full_path)
        else:
            for filename in os.listdir(directory):
                full_path = os.path.join(directory, filename)
                if os.path.isfile(full_path):
                    if extensions_set is not None:
                        _, ext = os.path.splitext(filename)
                        if ext.lower() not in extensions_set:
                            continue
                    filepaths.append(full_path)

        return filepaths


    def _get_needed_files(self, coords: list[tuple[float, float]]) -> list[str]:
        """
        Using self._raster_infos, get the list of files that covers the spcified geographical
        points.

        Args:
            coords (list[tuple[float, float]]): List of (latitude, longitude) tuples in degrees.

        Returns:
            list[str]: List of filepaths.
        """
        # NOTE: Usage of an R-Tree was investigated for faster response when the directory contains
        # many raster files. However the improvement seemed negligeable compared to the time
        # actually required for reading the data from file(s).
        files_needed = set()
        num_files = len(self._raster_infos)
        for lat, lon in coords:
            for info in self._raster_infos:
                minx, miny, maxx, maxy = info['bounds']
                if (minx <= lon <= maxx) and (miny <= lat <= maxy):
                    files_needed.add(info['file'])
                    if len(files_needed) == num_files:
                        return list(files_needed)
        return list(files_needed)


    def _read_raster_file(self, raster_filepath: str, coords: list[tuple[float, float]],
                          bilinear_interpol: bool, band: int=1) -> list:
        """
        Extract data from a geospatial raster file at the specified geographical locations.

        Args:
            raster_filepath (str): Full path to a geospatial raster file.
            coords (list[tuple[float, float]]): List of (latitude, longitude) tuples in degrees.
            bilinear_interpol (bool): Whether to apply bilinear interpolation using the four
                surrounding pixels. If False, nearest neighbor interpolation is used.
            band (int, optional): The raster band to use when reading the file. Default is 1.

        Returns:
            list: A list containing the extracted data values. When no data be could extracted at a
                specific coordinate (out of bounds or the file itself contains a "no data" value at
                that location), None is used as the result for that particular location.
        """
        import rasterio
        from rasterio.warp import transform

        result = []

        with rasterio.open(raster_filepath) as src:
            # Transform coordinates from EPSG:4326 to the raster's CRS if needed
            lats, lons = zip(*coords)
            if src.crs.to_string() != 'EPSG:4326':
                xs, ys = transform('EPSG:4326', src.crs, lons, lats)
            else:
                xs, ys = lons, lats

            nodata_value = src.nodatavals[band - 1]

            if bilinear_interpol is False: # use nearest neighbor
                points = list(zip(xs, ys))
                # Note: sample() returns "no data" value for points that are out of bounds
                for val in src.sample(points, indexes=band):
                    value = val[0] if hasattr(val, '__len__') else val
                    if self._is_nodata(value, nodata_value):
                        result.append(None)
                    else:
                        result.append(value)
            else: # use bilinear interpolation
                for x, y in zip(xs, ys):
                    # Get floating-point pixel indices for all points
                    # Corner of pixel (0, 0): at (0.0, 0.0)
                    # Center of pixel (0, 0): at (0.5, 0.5)
                    col_f, row_f = ~src.transform * (x, y)

                    row_f -= 0.5
                    col_f -= 0.5
                    irow, icol = int(floor(row_f)), int(floor(col_f))
                    pixel_coords = [
                        (irow,   icol),   # upper left
                        (irow,   icol+1), # upper right
                        (irow+1, icol),   # lower left
                        (irow+1, icol+1)  # lower right
                    ]
                    # Convert pixel indexes to geographical coordinates
                    # xy() returns coordinates at the center of the pixel
                    geo_coords = [src.xy(row, col) for row, col in pixel_coords]

                    sampling_generator = src.sample(geo_coords, indexes=band)

                    # Unpacking from the generator, actually does the reading from disk
                    values = [v[0] if hasattr(v, '__len__') else v for v in sampling_generator]

                    # proceed with the bilinear interpolation if there is no "no data" value
                    if all(not self._is_nodata(v, nodata_value) for v in values):
                        v00, v10, v01, v11 = values
                        dx = col_f - icol
                        dy = row_f - irow
                        val = (v00*(1-dx) + v10*dx)*(1-dy) + (v01*(1-dx) + v11*dx)*dy
                        result.append(val)
                    else:
                        # Possibly on edge of the file boundaries, fallback to nearest neighbor
                        val = next( src.sample([(x, y)], indexes=band) )
                        value = val[0] if hasattr(val, '__len__') else val
                        if self._is_nodata(value, nodata_value):
                            result.append(None)
                        else:
                            result.append(value)
        return result


    def _read_raster_file_in_memory_window(self, raster_filepath: str,
                                           coords: list[tuple[float, float]],
                                           bilinear_interpol: bool, band: int=1) -> list:
        """
        Extract data from a geospatial raster file at the specified geographical locations.

        This function differs from _read_raster_file() by reading once a window area encompassing
        all specified coordinates. The extracted data for that window is stored in memory and the
        corresponding data values for each coordinate is then extracted from memory, avoiding
        multiple file reads. This approach is generally faster but may throw a MemoryError
        exception for large raster files and sparse input coordinates.

        Args:
            raster_filepath (str): Full path to a geospatial raster file.
            coords (list[tuple[float, float]]): List of (latitude, longitude) tuples in degrees.
            bilinear_interpol (bool): Whether to apply bilinear interpolation using the four
                surrounding pixels. If False, nearest neighbor interpolation is used.
            band (int, optional): The raster band to use when reading the file. Default is 1.

        Returns:
            list: A list containing the extracted data values. When no data be could extracted at a
                specific coordinate (out of bounds or the file itself contains a "no data" value at
                that location), None is used as the result for that particular location.
        """
        import rasterio
        from rasterio.warp import transform

        result = []
        with rasterio.open(raster_filepath) as src:
            # Transform coordinates from EPSG:4326 to the raster's CRS if needed
            lats, lons = zip(*coords)
            if src.crs.to_string() != 'EPSG:4326':
                xs, ys = transform('EPSG:4326', src.crs, lons, lats)
            else:
                xs, ys = lons, lats

            # Get floating-point pixel indices for all points
            # Corner of pixel (0, 0): at (0.0, 0.0)
            # Center of pixel (0, 0): at (0.5, 0.5)
            pixel_indices_f = [~src.transform * (x, y) for x, y in zip(xs, ys)] # (col, row)
            pixel_indices_f = [(r, c) for c, r in pixel_indices_f] # (row, col)

            # Filter indices to keep only those inside the file bounds
            valid_pixel_indices_f = []
            is_point_valid = []
            for r, c in pixel_indices_f:
                if (0 <= r < src.height) and (0 <= c < src.width):
                    valid_pixel_indices_f.append((r,c))
                    is_point_valid.append(True)
                else:
                    is_point_valid.append(False)

            rows_f = [r for r, c in valid_pixel_indices_f]
            cols_f = [c for r, c in valid_pixel_indices_f]
            if len(rows_f) == 0:
                return [] # no coords within file's bounds

            # Compute bounding window
            min_row_i = int(floor(min(rows_f)))
            max_row_i = int(floor(max(rows_f)))
            min_col_i = int(floor(min(cols_f)))
            max_col_i = int(floor(max(cols_f)))

            # Extend the window as needed (but stay within raster bounds)
            extra = 0
            if bilinear_interpol is True:
                extra = 1 # need extra pixel for interpolation
            win_min_row_i = max(min_row_i - extra, 0)
            win_max_row_i = min(max_row_i + extra, src.height - 1)
            win_min_col_i = max(min_col_i - extra, 0)
            win_max_col_i = min(max_col_i + extra, src.width - 1)
            window_height_i = win_max_row_i - win_min_row_i + 1
            window_width_i  = win_max_col_i - win_min_col_i + 1
            window = rasterio.windows.Window(win_min_col_i, win_min_row_i,
                                             window_width_i, window_height_i)

            # Read window data into memory (2D numpy array)
            data = src.read(band, window=window)
            nodata_value = src.nodatavals[band - 1]

            # Process each point
            for i, (row_f, col_f) in enumerate(pixel_indices_f):
                if is_point_valid[i] is False:
                    result.append(None) # out of bounds
                    continue

                # Local indices relative to the window
                loc_row_f = row_f - win_min_row_i
                loc_col_f = col_f - win_min_col_i

                fallback_to_nearest = False
                if bilinear_interpol is True:
                    loc_row_f -= 0.5
                    loc_col_f -= 0.5
                    irow = floor(loc_row_f)
                    icol = floor(loc_col_f)
                    dx = loc_col_f - icol
                    dy = loc_row_f - irow

                    # Check for bounds (need 2x2 neighborhood)
                    if (0 <= irow < data.shape[0] - 1) and (0 <= icol < data.shape[1] - 1):
                        v00 = data[irow,   icol  ]
                        v10 = data[irow,   icol+1]
                        v01 = data[irow+1, icol  ]
                        v11 = data[irow+1, icol+1]
                        if any(self._is_nodata(v, nodata_value) for v in (v00, v10, v01, v11)):
                            result.append(None) # hit at least one "no data" pixel
                        else:
                            val = (v00*(1-dx) + v10*dx)*(1-dy) + (v01*(1-dx) + v11*dx)*dy
                            result.append(val)
                    else:
                        # must be on edge of the file boundaries, fallback to nearest neighbor
                        fallback_to_nearest = True

                if bilinear_interpol is False or fallback_to_nearest is True:
                    irow = int(floor(loc_row_f))
                    icol = int(floor(loc_col_f))
                    value = data[irow, icol]
                    if self._is_nodata(value, nodata_value):
                        result.append(None) # hit a "no data" pixel
                    else:
                        result.append(value)
        return result


    def _is_nodata(self, value, nodata_value) -> bool:
        """
        Returns True when value corresponds to the nodata_value, False otherwise.
        """
        if nodata_value is not None:
            if isnan(nodata_value):
                return isnan(value)
            else:
                return bool(value == nodata_value)
        else:
            return False
