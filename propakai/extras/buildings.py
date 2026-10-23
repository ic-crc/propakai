# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Additional buildings related functionalities in support for using ITU-R P. recommendations.

The buildings module requires **shapely**, **pyproj**, **shapefile** and **osmnx** to be installed.
If they are not already, you may do so with:
```bash
python -m pip install shapely pyproj pyshp osmnx
```
"""
from typing import TYPE_CHECKING
import os
import math
from array import array
import collections
from . import topography as topo
from .. import p2001_6 as p2001

if TYPE_CHECKING:
    # imports here are not performed at runtime, only when type-checking
    import shapely


__all__ = ['LatLonBox',
           'Building',
           'from_shapefile',
           'from_open_street_map',
           'to_geojson_file',
           'filter_by_path_intersection',
           'height_profile',
           'p1411_urban_metrics',
           'p1411_residential_metrics']


class LatLonBox:
    """
    Bounding box in geographical coordinates (EPSG 4326 (WGS84) assumed).

    Attributes:
        min_lat (float): minimum latitude of bounding box (degrees).
        min_lon (float): minimum longitude of bounding box (degrees).
        max_lat (float): maximum latitude of bounding box (degrees).
        max_lon (float): maximum longutide of bounding box (degrees).
    """
    def __init__(self, coord0: tuple[float, float], coord1: tuple[float, float]):
        """
        Initialize LatLonBox.

        Args:
            coord0 (tuple[float, float]): First corner of the box, a (latitude, longitude) tuple,
                in degrees.
            coord1 (tuple[float, float]): Second, opposite corner of the box, a
                (latitude, longitude) tuple, in degrees.
        """
        self.min_lat:float = min(coord0[0], coord1[0])
        self.min_lon:float = min(coord0[1], coord1[1])
        self.max_lat:float = max(coord0[0], coord1[0])
        self.max_lon:float = max(coord0[1], coord1[1])


class Building:
    """
    Data class for a building.

    Attributes:
        height_m (float): Height of the building (meters).
        footprint (shapely.Polygon): Coordinates of the building's footprint, in EPSG 4326 (WGS84).
        osmid (int|None): The building's OpenStreetMap ID when applicable, None otherwise.
    """
    def __init__(self, height_m: float, footprint: 'shapely.Polygon', osmid: int|None=None):
        """
        Initialize Building.

        Args:
            height_m (float): Height of the building (meters).
            footprint (shapely.Polygon): Coordinates of the building's footprint, in EPSG 4326
                (WGS84).
            osmid (int|None, optional): The building's OpenStreetMap ID when applicable, use None
                otherwise. Default is None.
        """
        self.height_m: float = height_m
        self.footprint: shapely.Polygon = footprint
        self.osmid: int|None=osmid


def from_shapefile(filepath: str, height_attribute: str, bounds: LatLonBox|None=None,
                   default_height_m: float=3.0) -> list[Building]:
    """
    Extracts building height and footprint data from the specified shapefile. The footprints are
    assumed to be stored using the Polygon shape type (5) within the shapefile.

    Args:
        filepath (str): Absolute or relative path to a shapefile (.shp) containing building heights
            and footprints.
        height_attribute (str): Name of the shapefile attribute that contains building heights.
        bounds (LatLonBox|None, optional): If specified, only buildings within these bounds are
            loaded. If None, the entire shapefile is processed.
        default_height_m (float, optional): Default building height (meters) applied when a value
            cannot be read from the height_attribute. Default is 3.0.

    Returns:
        list[Building]: List of Building objects obtained from the shapefile.
    """
    import shapely
    import pyproj
    import pyproj.crs
    import shapefile

    bldg_list = []

    prj_pathname = os.path.splitext(filepath)[0] + '.prj'
    with open(prj_pathname, encoding='utf-8') as f:
        prj_content = f.read()
        prj_file_crs = pyproj.crs.CRS(prj_content)

    if bounds is not None:
        crs_4326 = pyproj.CRS.from_epsg(4326)
        transformer = pyproj.Transformer.from_crs(crs_from=crs_4326, crs_to=prj_file_crs,
                                                  always_xy=True)
        bbox = transformer.transform_bounds(left=bounds.min_lon, bottom=bounds.min_lat,
                                            right=bounds.max_lon, top=bounds.max_lat)
        bbox = shapefile.BBox(*bbox)
    else:
        bbox = None

    footprint_transformer = None
    crs_4326 = pyproj.CRS.from_epsg(4326)
    if prj_file_crs.equals(crs_4326) is False:
        footprint_transformer = pyproj.Transformer.from_crs(crs_from=prj_file_crs, crs_to=crs_4326,
                                                            always_xy=True)

    sf = shapefile.Reader(filepath)
    #print(sf.fields)
    for shape_rec in sf.iterShapeRecords(bbox=bbox):
        if shape_rec.shape and shape_rec.shape.shapeType == 5: # 5=POLYGON
            if footprint_transformer is not None:
                x_coords, y_coords = list(zip(*(shape_rec.shape.points)))
                new_x_coords, new_y_coords = footprint_transformer.transform(x_coords, y_coords)
                shape_rec.shape.points = list(zip(list(new_x_coords), list(new_y_coords)))

            if len(shape_rec.shape.parts) == 1:
                footprint = shapely.Polygon(shell=shape_rec.shape.points) # type: ignore[arg-type]
            else: # more than one parts
                shell = shape_rec.shape.points[0 : shape_rec.shape.parts[1]]
                holes = []
                for i in range(1, len(shape_rec.shape.parts)-1):
                    holes.append(shape_rec.shape.points[shape_rec.shape.parts[i] : \
                                                        shape_rec.shape.parts[i+1]])
                holes.append(shape_rec.shape.points[shape_rec.shape.parts[-1] : ])
                footprint = shapely.Polygon(shell=shell, holes=holes) # type: ignore[arg-type]

            height_m = default_height_m
            osmid = None
            if shape_rec.record:
                try:
                    height_m = float(shape_rec.record[height_attribute]) # type: ignore[arg-type]
                except Exception as _: # pylint: disable=broad-exception-caught
                    height_m = default_height_m

                try:
                    osmid = int(shape_rec.record['osm_id']) # type: ignore[arg-type]
                except Exception as _: # pylint: disable=broad-exception-caught
                    osmid = None

            bldg = Building(height_m, footprint, osmid)
            bldg_list.append(bldg)

    return bldg_list


def from_open_street_map(bounds: LatLonBox, avg_floor_height_m: float=3.0,
                         default_height_m: float=3.0) -> list[Building]:
    """
    Downloads building footprint data from OpenStreetMap. Building heights are estimated from the
    number of above-ground floors ('building:levels' tag) when present.

    Args:
        bounds (LatLonBox): A bounding box from which to get the building data.
        avg_floor_height_m (float): Average floor height (meters) for estimating building heights.
        default_height_m (float, optional): Default height value (meters) to be applied to any
            building whose height cannot be estimated (i.e. when the 'building:levels' tag is
            missing).

    Returns:
        list[Building]: A list of Building objects obtained from the OpenStreetMap.
    """
    import osmnx
    import pandas as pd
    from shapely import Polygon

    bldg_list = []

    osmnx_major_ver = int(osmnx.__version__.split('.')[0])
    if osmnx_major_ver >= 2:
        # bbox in (left, bottom, right, top) format
        bbox = (bounds.min_lon, bounds.min_lat, bounds.max_lon, bounds.max_lat)
    else:
        # bbox in (north, south, east, west) format
        bbox = (bounds.max_lat, bounds.min_lat, bounds.max_lon, bounds.min_lon)

    try:
        # gets a geopandas.GeoDataFrame
        gdf = osmnx.features.features_from_bbox(bbox=bbox, tags={'building': True})
    except Exception as _: # pylint: disable=broad-exception-caught
        return bldg_list

    footprints = gdf['geometry'].values.tolist() # already in EPSG 4326

    if "building:levels" in gdf:
        # Converts strings to floats, and automatically turns bad strings ("2 floors") into NaN
        num_levels: list[float] = (
            pd.to_numeric(gdf["building:levels"], errors="coerce")
            .astype(float)
            .tolist()
        )
    else:
        num_levels = [float("nan")] * len(footprints)

    indexes = gdf.index.values.tolist()
    _, osmids = list(zip(*indexes))

    for footprint, floor_count, osmid in zip(footprints, num_levels, osmids):
        if math.isnan(floor_count):
            height_m = default_height_m
        else:
            height_m = floor_count*avg_floor_height_m

        #bldg = Building(height_m, footprint, osmid)
        if isinstance(footprint, Polygon):
            bldg = Building(height_m, footprint, osmid)
            bldg_list.append(bldg)
        else:
            print('Building skipped, not a Polygon footprint.')

    return bldg_list


def to_geojson_file(buildings: list[Building], filepath: str) -> None:
    """
    Exports a list of Building objects to a geojson file.

    Args:
        buildings (list[Building]): A list of Building objects, typically obtained from the
            from_shapefile() or from_open_street_map() functions.
        filepath (str): Absolute or relative path to the geojson file to create or overwrite.
    """
    import shapely
    features = []
    for building in buildings:
        json_str = f'{{"type":"Feature","geometry":{shapely.to_geojson(building.footprint)},' \
                   f'"properties":{{"height (m)":"{building.height_m:.1f}",' \
                   f'"osmid":"{building.osmid}"}}}}'
        features.append(json_str)
    joined_features = ','.join(features)
    json_str = f'{{"type":"FeatureCollection","features":[{joined_features}]}}'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(json_str)


def filter_by_path_intersection(buildings: list[Building], path_coords: list[tuple[float, float]]
                                ) -> list[Building]:
    """
    Returns a filtered list of buildings containing only those that intersect with the specified
    path. Buildings are returned in no particular order, with no duplication.

    Args:
        buildings (list[Building]): List of Building objects, usually created by
            `from_shapefile()` or `from_open_street_map()`.
        path_coords (list[tuple[float, float]]): List of (latitude, longitude) tuples in degrees,
            typically obtained from `propakai.extras.topography.lat_lon_profile()`.

    Returns:
        list[Building]: List of Building objects intersecting the path.
    """
    import shapely
    intersect_bldgs = []
    lon_lat_coords = [(lon, lat) for lat, lon in path_coords]
    path_linestring = shapely.LineString(lon_lat_coords)
    for bldg in buildings:
        if path_linestring.intersects(bldg.footprint) is True:
            if bldg not in intersect_bldgs:
                intersect_bldgs.append(bldg)
    return intersect_bldgs


def height_profile(buildings: list[Building], coords: list[tuple[float, float]]) -> array:
    """
    Generates a building height profile (m) along a sequence of coordinates. Locations without a
    building return a height of 0.

    Args:
        buildings (list[Building]): List of Building objects, usually created by
            `from_shapefile()` or `from_open_street_map()`.
        coords (list[tuple[float, float]]): List of (latitude, longitude) tuples, in degrees,
            for which to obtain building heights. Typically obtained from
            `propakai.extras.topography.lat_lon_profile()`.

    Returns:
        array: An array of type 'd' (double-precision floats), containing the building
            heights (in meters) for each input coordinate.
    """
    import shapely
    intersect_bldgs = filter_by_path_intersection(buildings, coords)
    bldg_heights = array('d', [0] * len(coords))
    for i, (lat, lon) in enumerate(coords):
        pt = shapely.Point(lon, lat)
        for bldg in intersect_bldgs:
            if bldg.footprint.contains(pt) is True:
                bldg_heights[i] = bldg.height_m
                break
    return bldg_heights


def p1411_urban_metrics(buildings: list[Building], latt: float, lont: float,
                         latr: float, lonr: float, res_m: float=1.0, path_ext_m: float=100.0
                         ) -> tuple[float, float|None, float|None, float, float|None]:
    """
    Computes building-related metrics for a direct transmitter-to-receiver path, suitable as input
    to site-specific, over roof-tops urban/suburban propagation models (ITU-R P.1411).
    See ITU-R P.1411-13, FIGURE 2 for further details.

    Args:
        buildings (list[Building]): List of Building objects, typically from
            `from_shapefile()` or `from_open_street_map()`.
        latt (float): Transmitter latitude (degrees), with -90 <= latt <= 90.
        lont (float): Transmitter longitude (degrees), with -180 <= lont <= 180.
        latr (float): Receiver latitude (degrees), with -90 <= latr <= 90.
        lonr (float): Receiver longitude (degrees), with -180 <= lonr <= 180.
        res_m (float, optional): Path sampling resolution (meters) for the presence of buildings.
            Default is 1.0.
        path_ext_m (float, optional): Extra distance (meters) past the receiver used
            to assess street width and building separation. Default is 100.0.
            
    Returns:
        d_m (float): Path length (great-circle distance) from the transmitter to the receiver
            (meters).
        hr_m (float|None): Average height of buildings along the path (meters). None if no
            building is found along the path.
        b_m (float|None): Average building separation distance along the path (meters). None if
            fewer than 2 buildings are found along the path.
        l_m (float): Length of the path covered by buildings (meters). Zero when no building is
            found along the path.
        w_m (float|None): Street width at the receiver location (meters), which is the distance
            between the two closest buildings encompassing the receiver. None if two such buildings
            cannot be found along the path.
    """
    d_m = p2001.path_length(latt, lont, latr, lonr)*1000.0
    lat_ext, lon_ext = p2001.intermediate_path_point(latt, lont, latr, lonr,
                                                     dist_km=(d_m+path_ext_m)/1000.0)

    bldg_dtx_ext_list: list[_BldgDistsToTx] = _bldg_distances_to_tx(buildings, latt, lont,
                                                                    lat_ext, lon_ext, res_m)

    # min/max distances (m) to tx for each building along the tx-rx path (without the extension)
    bldg_dtx_list: list[_BldgDistsToTx] = [bd for bd in bldg_dtx_ext_list if bd.max_dist_m < d_m]

    # Calculates hr_m, the average height of buildings (tx-rx path)
    hr_m = None
    if len(bldg_dtx_list) > 0:
        bldg_height_sum = sum(bldg.height_m for bldg in bldg_dtx_list)
        hr_m = bldg_height_sum / len(bldg_dtx_list)

    # Calculates l_m, the length of the path covered by buildings (tx-rx path)
    l_m = 0.0
    if len(bldg_dtx_list) > 0:
        l_m = bldg_dtx_list[-1].max_dist_m - bldg_dtx_list[0].min_dist_m

    rx_prev_bldg_dtx = None # first building "before" the rx
    if len(bldg_dtx_list) > 0:
        rx_prev_bldg_dtx = bldg_dtx_list[-1]

    rx_next_bldg_dtx = None # first building "after" the rx
    for bd in bldg_dtx_ext_list:
        if bd.min_dist_m > d_m:
            rx_next_bldg_dtx = bd
            break

    # Add first building "after" the rx, if any
    if rx_next_bldg_dtx is not None:
        bldg_dtx_list.append(rx_next_bldg_dtx)

    # Calculates b_m, the average building separation distance (tx-rx path + 1 bldg after the rx)
    b_m = None
    sep_dist_list = []
    for i in range(1, len(bldg_dtx_list)):
        sep_dist = ((bldg_dtx_list[i].min_dist_m + bldg_dtx_list[i].max_dist_m) / 2.0) -  \
                   ((bldg_dtx_list[i-1].min_dist_m + bldg_dtx_list[i-1].max_dist_m) / 2.0)
        sep_dist_list.append(sep_dist)
    if len(sep_dist_list) > 0:
        b_m = sum(sep_dist_list) / len(sep_dist_list)

    # Calculates w_m, the street width (distance between previous and next buildings from receiver)
    w_m = None
    if rx_prev_bldg_dtx is not None and rx_next_bldg_dtx is not None:
        w_m = rx_next_bldg_dtx.min_dist_m - rx_prev_bldg_dtx.max_dist_m

    return (d_m, hr_m, b_m, l_m, w_m)


def p1411_residential_metrics(buildings: list[Building], latt: float, lont: float, latr: float,
                              lonr: float, res_m: float=1.0
                    ) -> tuple[float, float|None, float|None, float|None, float|None, float|None]:
    """
    Computes building-related metrics for a direct transmitter-to-receiver path, suitable as input
    to site-specific, below roof-top to near street level residential propagation models (ITU-R
    P.1411). See ITU-R P.1411-13, FIGURE 12 for further details.

    Args:
        buildings (list[Building]): List of Building objects, typically from
            `from_shapefile()` or `from_open_street_map()`.
        latt (float): Transmitter latitude (degrees), with -90 <= latt <= 90.
        lont (float): Transmitter longitude (degrees), with -180 <= lont <= 180.
        latr (float): Receiver latitude (degrees), with -90 <= latr <= 90.
        lonr (float): Receiver longitude (degrees), with -180 <= lonr <= 180.
        res_m (float, optional): Path sampling resolution (meters) for the presence of buildings.
            Default is 1.0.
            
    Returns:
        d_m (float): Path length (great-circle distance) from the transmitter to the receiver
            (meters).
        hbtx_m (float|None): Height of nearest building from transmitter in receiver direction
            (meters). None if no building is found along the path.
        hbrx_m (float|None): Height of nearest building from receiver in transmitter direction
            (meters). None if no building is found along the path.
        a_m (float|None): Distance between transmitter and nearest building from transmitter
            (meters). None if no building is found along the path.
        b_m (float|None): Distance between nearest buildings from transmitter and receiver
            (meters). None if no building is found along the path.
        c_m (float|None): Distance between receiver and nearest building from receiver (meters).
            None if no building is found along the path.
    """
    d_m = p2001.path_length(latt, lont, latr, lonr)*1000.0
    bldg_dtx_list: list[_BldgDistsToTx] = _bldg_distances_to_tx(buildings, latt, lont, latr, lonr,
                                                                res_m)

    hbtx_m = None
    hbrx_m = None
    a_m = None
    b_m = None
    c_m = None
    if len(bldg_dtx_list) > 0:
        hbtx_m = bldg_dtx_list[0].height_m
        hbrx_m = bldg_dtx_list[-1].height_m
        a_m = bldg_dtx_list[0].min_dist_m
        c_m = d_m - bldg_dtx_list[-1].max_dist_m
        if len(bldg_dtx_list) == 1:
            b_m = 0.0
        else:
            b_m = d_m - a_m - c_m

    return (d_m, hbtx_m, hbrx_m, a_m, b_m, c_m)


class _BldgDistsToTx:
    def __init__(self, height_m:float, min_dist_m:float, max_dist_m:float):
        self.height_m:float = height_m
        self.min_dist_m:float = min_dist_m # min distance to tx along path (m)
        self.max_dist_m:float = max_dist_m # max distance to tx along path (m)


def _bldg_distances_to_tx(buildings: list[Building], tx_lat: float, tx_lon: float,
                          path_end_lat: float, path_end_lon: float, res_m: float
                          ) -> list[_BldgDistsToTx]:
    import shapely

    coords = topo.lat_lon_profile(tx_lat, tx_lon, path_end_lat, path_end_lon, res_m)
    d_m = p2001.path_length(tx_lat, tx_lon, path_end_lat, path_end_lon)*1000.0
    delta_dist_m = d_m / (len(coords)-1) # precise value as res_m is approximate

    # Get buildings that intersect with the path
    intersect_bldgs = filter_by_path_intersection(buildings, coords)

    # Build profile of encountered buildings along the path (i.e. index of building in
    # intersect_bldgs or -1 where there is no building)
    bldg_index_profile = [-1]*len(coords)
    for coord_index, (lat, lon) in enumerate(coords):
        pt = shapely.Point(lon, lat)
        for bldg_index, bldg in enumerate(intersect_bldgs):
            if bldg.footprint.contains(pt) is True:
                bldg_index_profile[coord_index] = bldg_index
                break

    # Get min/max distances (m) to tx for each building along the path
    bldg_dists_dict = collections.OrderedDict()
    for i, bldg_index in enumerate(bldg_index_profile):
        if bldg_index != -1:
            di_m = i*delta_dist_m

            bldg_dists_dict.setdefault(bldg_index,
                                       _BldgDistsToTx(
                                           height_m=intersect_bldgs[bldg_index].height_m,
                                           min_dist_m=max(0, di_m-(delta_dist_m/2.0)),
                                           max_dist_m=min(d_m, di_m+(delta_dist_m/2.0))
                                       ))
            bldg_dists_dict[bldg_index].max_dist_m = min(d_m, di_m+(delta_dist_m/2.0))
    bldg_dists_list = list(bldg_dists_dict.values()) # in the order that buildings are encountered
                                                     # along the path

    return bldg_dists_list
