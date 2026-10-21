# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Additional streets related functionalities, using OpenStreetMap data, in support for using ITU-R P.
recommendations.

The streets module requires **shapely**, **osmnx** to be installed. If they are not already, you
may do so with:
```bash
python -m pip install shapely osmnx
```

Purpose:
  This module aims at determining potential propagation paths for scenarios where antennas are
  below rooftops and the radio path is understood to occur mainly through street canyons. Typical
  usage is the obtention of input data for propagation models such as those found in ITU-R P.1411.

Typical workflow:
  1. Create a new `StreetGraph` object for the area of interest. This will download relevant street
     data from OpenStreetMap. The `StreetGraph` object may then be visualized using its `display()`
     method. 
  2. Use the `compute_street_canyon_radio_paths()` function to compute the shortest path(s) along
     street lines from the transmitter to the receiver station. This function returns one or more
     `StreetCanyonRadioPath` objects. Their `to_geojson_file()` method may be used to visualize
     those paths from a GIS software.
  3. Optionally, simplify `StreetCanyonRadioPath` objects to reduce the number of vertices using
     their `new_simplified()` method. This is usually desirable, as it removes very small street
     sections that make the propagation path unnecessarily complex.
  4. The `distances_to_street_corners()` and `street_corner_angles()` methods and the attributes
     from the `StreetCanyonRadioPath` objects, as well as the `receiver_street_orientation()`
     function, may all be used for input parameters to propagation models such as those found in
     ITU-R P.1411.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from math import degrees, atan2
from .buildings import LatLonBox

if TYPE_CHECKING:
    # imports here are not performed at runtime, only when type-checking
    import shapely


__all__ = ['LatLonBox',
           'StreetGraph',
           'compute_street_canyon_radio_paths',
           'sort_by_street_corner_turns',
           'receiver_street_orientation',
           'StreetCanyonRadioPath']


class StreetGraph:
    """
    Street graph generated from OpenStreetMap (OSM) data. Suitable as input for the
    `compute_street_canyon_radio_paths()` function.
    """
    def __init__(self, bounds: LatLonBox | list[tuple[float,float]], buffer_dist_m: float=250):
        """
        Downloads OpenStreetMap (OSM) data for the specified geographic bounds and constructs a
        street graph using OSMnx.

        Args:
            bounds (LatLonBox | list[tuple[float,float]]): Either a LatLonBox object or a list of
                (latitude, longitude) tuples, in degrees, specifying the area to retrieve OSM data
                for.
            buffer_dist_m (float, optional): Extra buffer distance (meters) to extend the bounds
                before data retrieval. Default is 250 meters.
        """
        import osmnx as ox

        if bounds is LatLonBox:
            min_lat, max_lat = bounds.min_lat, bounds.max_lat
            min_lon, max_lon = bounds.min_lon, bounds.max_lon
        else:
            latitudes, longitudes = zip(*bounds)
            min_lat, max_lat = min(latitudes), max(latitudes)
            min_lon, max_lon = min(longitudes), max(longitudes)

        bbox1 = ox.utils_geo.bbox_from_point(point=(min_lat, min_lon), dist=buffer_dist_m,
                                            project_utm=False, return_crs=False)
        bbox2 = ox.utils_geo.bbox_from_point(point=(max_lat, max_lon), dist=buffer_dist_m,
                                            project_utm=False, return_crs=False)
        osmnx_major_ver = int(ox.__version__.split('.')[0])

        if osmnx_major_ver >= 2:
            # bbox in (left, bottom, right, top) format
            min_lat, min_lon, max_lat, max_lon = min(bbox1[1], bbox2[1]), min(bbox1[0], bbox2[0]), \
                                                max(bbox1[3], bbox2[3]), max(bbox1[2], bbox2[2])
        else:
            # bbox in (north, south, east, west) format
            min_lat, min_lon, max_lat, max_lon = min(bbox1[1], bbox2[1]), min(bbox1[3], bbox2[3]), \
                                                max(bbox1[0], bbox2[0]), max(bbox1[2], bbox2[2])

        self._initialize(min_lat=min_lat, min_lon=min_lon, max_lat=max_lat, max_lon=max_lon)


    def _initialize(self, min_lat: float, min_lon: float, max_lat: float, max_lon: float) -> None:
        """
        Downloads OpenStreetMap (OSM) data for the specified boundaries and creates a graph using
        OSMnx.

        Args:
            min_lat (float): Minimum latitude boundary for the OSM data download (degrees),
                with -90 <= min_lat <= 90.
            min_lon (float): Minimum longitude boundary for the OSM data download (degrees),
                with -180 <= min_lon <= 180.
            max_lat (float): Maximum latitude boundary for the OSM data download (degrees),
                with -90 <= max_lat <= 90.
            max_lon (float): Maximum longitude boundary for the OSM data download (degrees),
                with -180 <= maxLon <= 180.
        """
        import osmnx as ox
        import shapely as shp

        osmnx_major_ver = int(ox.__version__.split('.')[0])
        if osmnx_major_ver >= 2:
            # bbox in (left, bottom, right, top) format
            bbox = (min(min_lon, max_lon), min(min_lat, max_lat),
                    max(min_lon, max_lon), max(min_lat, max_lat))
        else:
            # bbox in (north, south, east, west) format
            bbox = (max(min_lat, max_lat), min(min_lat, max_lat),
                    min(min_lon, max_lon), max(min_lon, max_lon))
        G = ox.graph_from_bbox(bbox=bbox, network_type='drive', simplify=True, retain_all=True,
                            truncate_by_edge=True, custom_filter=None)

        centre_lat = (min_lat+max_lat)/2
        centre_lon = (min_lon+max_lon)/2
        _, crs_utm = ox.projection.project_geometry(shp.Point(centre_lon, centre_lat),
                                                    crs='epsg:4326', to_crs=None, to_latlong=False)
        G_utm = ox.projection.project_graph(G=G, to_crs=crs_utm, to_latlong=False)
        G_utm = ox.convert.to_undirected(G=G_utm) # radiowaves do not follow oneway signs

        gdf_edges = ox.convert.graph_to_gdfs(G=G_utm, nodes=False, edges=True, node_geometry=False,
                                    fill_edge_geometry=True) [['from', 'to', 'length', 'geometry']]
        gdf_nodes = ox.convert.graph_to_gdfs(G=G_utm, nodes=True, edges=False, node_geometry=False,
                                            fill_edge_geometry=False) [['x', 'y']]

        self._osm_graph = G_utm # type networkx.MultiDiGraph
        self._edges = gdf_edges # type geopandas.GeoDataFrame
        self._nodes = gdf_nodes # type geopandas.GeoDataFrame


    def display(self) -> None:
        """
        Displays the street graph.
        """
        import osmnx as ox
        ox.plot_graph(self._osm_graph)


class StreetCanyonRadioPath:
    """
    Class for storing details about a propagation path occurring through street canyons
    (i.e., propagation along street lines). One or more instances may be obtained from
    `compute_street_canyon_radio_paths()`.

    Attributes:
        lat_lon_path (list[tuple[float, float]]): List of n (latitude, longitude) tuples
            constituting the vertices of the propagation path along street segments, from
            transmitter to receiver (degrees, EPSG:4326).
        turn_angles_deg (list[float]): List of n-2 turn angles between street segments in
            lat_lon_path (degrees). The first angle is at lat_lon_path[1], and the last angle is at
            lat_lon_path[-2]. Angle values range from 0 (going straight forward) to 180 (U-turn).
            Note that turn angles are always positive, so there is no differentiation between
            right-hand and left-hand turns at the same angle.
        is_intersection (list[bool]): List of n-2 boolean values indicating whether points between
            street segments in lat_lon_path are street intersections. The first boolean value is at
            lat_lon_path[1], and the last one is at lat_lon_path[-2].
        distances_m (list[float]): List of n-1 street segment distances (meters) in lat_lon_path.
            The first value is the distance between lat_lon_path[0] and lat_lon_path[1]; the last
            value is the distance between lat_lon_path[-2] and lat_lon_path[-1].
        tx_lat_lon (tuple[float, float]): Transmitter's location as a (latitude, longitude) tuple
            (degrees, EPSG:4326). lat_lon_path[0] is the closest point to tx_lat_lon that is
            located on a street segment.
        rx_lat_lon (tuple[float, float]): Receiver's location as a (latitude, longitude) tuple
            (degrees, EPSG:4326). lat_lon_path[-1] is the closest point to rx_lat_lon that is
            located on a street segment.
    """
    def __init__(self):
        self.lat_lon_path: list[tuple[float, float]] = [] # n items
        self.turn_angles_deg: list[float] = [] # n-2 items
        self.is_intersection: list[bool] = [] # n-2 items
        self.distances_m: list[float] = [] # n-1 items
        self.tx_lat_lon: tuple[float, float] = (0, 0)
        self.rx_lat_lon: tuple[float, float] = (0, 0)
        self._projected_coords_path: list[tuple[float, float]] = [] # n items
        self._projected_crs: str = ''


    def to_geojson_file(self, filepath: str) -> None:
        """
        Exports a street canyon radio path to a geojson file.

        Args:
            filepath (str): Absolute or relative path to the geojson file to create or overwrite.
        """
        import shapely as shp
        features = []

        pt_str = shp.to_geojson(shp.Point(self.tx_lat_lon[1], self.tx_lat_lon[0]))
        json = f'{{"type":"Feature","geometry":{pt_str},"properties":{{"name":"transmitter"}}}}'
        features.append(json)

        pt_str =shp.to_geojson(shp.Point(self.rx_lat_lon[1], self.rx_lat_lon[0]))
        json = f'{{"type":"Feature","geometry":{pt_str},"properties":{{"name":"receiver"}}}}'
        features.append(json)

        xy_coords = [tuple([coord[1], coord[0]]) for coord in self.lat_lon_path]
        ls_str = shp.to_geojson(shp.LineString(xy_coords))
        json = f'{{"type":"Feature","geometry":{ls_str}}}'
        features.append(json)

        for i, is_intersection in enumerate(self.is_intersection):
            if is_intersection is True:
                pt_str = shp.to_geojson(shp.Point(self.lat_lon_path[i+1][1],
                                                  self.lat_lon_path[i+1][0]))
                json = f'{{"type":"Feature","geometry":{pt_str},"properties":{{"name":' \
                       f'"intersection","turn angle (deg)":{self.turn_angles_deg[i]:.2f}}}}}'
                features.append(json)

        features_str = ','.join(features)
        json = f'{{"type":"FeatureCollection","features":[{features_str}]}}'

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json)


    def new_simplified(self, tolerance_m: float=12) -> StreetCanyonRadioPath:
        """
        Returns a new, simplified (i.e. reduces the number of vertices) StreetCanyonRadioPath.

        Args:
            tolerance_m (float, optional): Maximum allowed path geometry displacement (meters).
                Default is 12 meters.

        Returns:
            StreetCanyonRadioPath: A new street canyon radio path that is a simplified version of
                the original.
        """
        import shapely as shp
        import osmnx as ox
        # pylint: disable=protected-access
        new_rp = StreetCanyonRadioPath()
        original_ls_m = shp.LineString(self._projected_coords_path)
        simplified_ls_m = shp.simplify(geometry=original_ls_m, tolerance=tolerance_m,
                                       preserve_topology=True)
        simplified_ls_dd, _ = ox.projection.project_geometry(simplified_ls_m,
                                                             crs=self._projected_crs,
                                                             to_crs=None, to_latlong=True)
        new_rp.lat_lon_path = _line_string_to_coord_tuples(simplified_ls_dd, True)
        new_rp._projected_coords_path = _line_string_to_coord_tuples(simplified_ls_m, False)
        new_rp.distances_m = _line_string_distances(simplified_ls_m)
        new_rp.turn_angles_deg = _line_string_turn_angles_deg(simplified_ls_m)
        for i in range(1, len(new_rp._projected_coords_path)-1):
            new_rp.is_intersection.append(_is_intersection(self,
                                                           new_rp._projected_coords_path[i][0],
                                                           new_rp._projected_coords_path[i][1]))
        new_rp.tx_lat_lon = self.tx_lat_lon
        new_rp.rx_lat_lon = self.rx_lat_lon
        new_rp._projected_crs = self._projected_crs
        return new_rp


    def distances_to_street_corners(self, turn_angle_threshold_deg: float=45) -> list[float]:
        """
        Gets a list of travel distances, in meters, to the next street corner (i.e. the next turn
        point at a turn-angle of at least turn_angle_threshold_deg) or to the receiver, along the
        street canyon radio path.

        Examples of return values and their meaning:
            - `[50, 100, 30]`:
                Travel distance from the tx station to the first street corner is 50m.
                Travel distance from the first street corner to the second street corner is 100m.
                Travel distance from the second street corner to the rx station is 30m.
            - `[75]`:
                Travel distance from the tx station to the rx station is 75m (no street corner
                encountered).

        Args:
            turn_angle_threshold_deg (float, optional): Turn-angle threshold used to identify street
                corners (degrees), with 0 <= turn_angle_threshold_deg <= 180. A turn-angle near zero
                means the path is going straight. A turn-angle near 90 represents a right-hand or a
                left-hand turn (the turn-angle will vary depending on how the streets intersect).
                Default is 45 degrees.

        Returns:
            list[float]: List of travel distances, in meters, to the next street corner or to the
                receiver.
        """
        if len(self.distances_m) == 0:
            return [0.0]
        x_m = [self.distances_m[0]]
        for i, turn_angle_deg in enumerate(self.turn_angles_deg):
            if turn_angle_deg >= turn_angle_threshold_deg:
                x_m.append(self.distances_m[i+1])
            else:
                x_m[-1] += self.distances_m[i+1]
        return x_m


    def street_corner_angles(self, turn_angle_threshold_deg: float=45) -> list[float]:
        """
        Rturns the list of street corner angles from a street canyon radio path, that is, the list
        of street corner angles along the path where the turn-angle equals or exceeds the specified
        threshold. Note that the street corner angle corresponds to 180 degrees minus the turn-
        angle.
        
        See FIGURE 3 of ITU-R P.1411-13 for a representation of the street corner angle.

        Args:
            turn_angle_threshold_deg (float, optional): Turn-angle threshold used to identify street
                corners (degrees), with 0 <= turn_angle_threshold_deg <= 180. A turn-angle near zero
                means the path is going straight. A turn-angle near 90 represents a right-hand or a
                left-hand turn (the turn-angle will vary depending on how the streets intersect).
                Default is 45 degrees.
                
        Returns:
            list[float]: Street corner angles, in degrees, found along the path.
        """
        if len(self.distances_m) == 0:
            return []
        street_corner_angles_deg = []
        for turn_angle_deg in self.turn_angles_deg:
            if turn_angle_deg >= turn_angle_threshold_deg:
                street_corner_angles_deg.append(180.0-turn_angle_deg)
        return street_corner_angles_deg


def compute_street_canyon_radio_paths(graph: StreetGraph|None, latt: float, lont: float,
                                      latr: float, lonr: float, num_paths: int
                                      ) -> list[StreetCanyonRadioPath]:
    """
    Computes one or more radio paths along street lines from the transmitter to the receiver 
    location. The returned paths are those with the smallest travel distances.

    Each path is represented as a `StreetCanyonRadioPath`. The attributes and methods of this class
    can provide inputs for propagation models, such as those found in ITU-R P.1411, where antennas
    are below rooftops and the radio path is assumed to occur mainly through street canyons.

    Args:
        graph (StreetGraph|None): StreetGraph for the area of interest, or None. If None, a
            temporary StreetGraph is created based on the transmitter and receiver locations.
        latt (float): Transmitter latitude (degrees), with -90 <= latt <= 90.
        lont (float): Transmitter longitude (degrees), with -180 <= lont <= 180.
        latr (float): Receiver latitude (degrees), with -90 <= latr <= 90.
        lonr (float): Receiver longitude (degrees), with -180 <= lonr <= 180.
        num_paths (int): Maximum number of paths to return, with 1 <= num_paths.

    Returns:
        list[StreetCanyonRadioPath]: Paths found from transmitter to receiver, ordered by shortest
        travel distance. The number of paths will be up to `num_paths`, but may be less if fewer
        paths can be computed.
    """
    # pylint: disable=protected-access
    import osmnx as ox
    import shapely as shp

    if graph is None:
        graph = StreetGraph(bounds=[(latt, lont),(latr, lonr)])

    G_utm = graph._osm_graph # type networkx.MultiDiGraph
    crs_utm = graph._osm_graph.graph['crs']
    tx_utm: shp.Point = ox.projection.project_geometry(shp.Point(lont, latt), crs='epsg:4326',
                                                       to_crs=crs_utm, to_latlong=False)[0]
    rx_utm: shp.Point = ox.projection.project_geometry(shp.Point(lonr, latr), crs='epsg:4326',
                                                       to_crs=crs_utm, to_latlong=False)[0]

    tx_edge: tuple[float, float, float] # (nodeID, nodeID, 0)
    rx_edge: tuple[float, float, float]
    tx_edge = ox.distance.nearest_edges(G=G_utm, X=tx_utm.x, Y=tx_utm.y, return_dist=False)
    rx_edge = ox.distance.nearest_edges(G=G_utm, X=rx_utm.x, Y=rx_utm.y, return_dist=False)

    # place tx and rx "on the road"
    snapped_tx_utm: shp.Point = _nearest_edge_point(graph=graph, point=tx_utm, edge=tx_edge)
    snapped_rx_utm: shp.Point = _nearest_edge_point(graph=graph, point=rx_utm, edge=rx_edge)

    # shortest_paths uses nodes, not random points on an edge (i.e. street), so compute paths
    # using all possible nodeID combinations. Here a path is a list of nodes.
    gen_list = [
      ox.k_shortest_paths(G=G_utm, orig=tx_edge[0], dest=rx_edge[0], k=num_paths, weight='length'),
      ox.k_shortest_paths(G=G_utm, orig=tx_edge[1], dest=rx_edge[0], k=num_paths, weight='length'),
      ox.k_shortest_paths(G=G_utm, orig=tx_edge[0], dest=rx_edge[1], k=num_paths, weight='length'),
      ox.k_shortest_paths(G=G_utm, orig=tx_edge[1], dest=rx_edge[1], k=num_paths, weight='length')
    ]
    temp_path_list = []
    for generator in gen_list:
        for path in generator:
            temp_path_list.append(path)

    path_list =[]
    two_nodes_path_found = False
    for path in temp_path_list:
        path = _ensure_edge_is_first_edge_of_path(path=path, edge=tx_edge)
        path = _ensure_edge_is_last_edge_of_path(path=path, edge=rx_edge)
        if len(path) == 2:
            if two_nodes_path_found is True:
                # when tx and rx are on same edge, avoid having both path [nodeA, nodeB]
                # and [nodeB, nodeA]
                continue
            else:
                two_nodes_path_found = True
        if path not in path_list:
            path_list.append(path)

    rp_list: list[StreetCanyonRadioPath] = []
    for path in path_list:
        rp = StreetCanyonRadioPath()
        ls = shp.LineString()

        if len(path)==2:
            # Case where tx and rx are on same street with no intersection (i.e no node) between
            # the two.
            temp_ls = _edge_line_string(graph=graph, edge=(path[0], path[1], 0))
            ls_a, ls_b = _split_line_string(temp_ls, snapped_tx_utm)
            try:
                ls_c, ls_d = _split_line_string(ls_a, snapped_rx_utm)
            except Exception as _:
                ls_c, ls_d = _split_line_string(ls_b, snapped_rx_utm)
            ls_c_first = shp.Point(ls_c.coords[0])
            ls_c_last = shp.Point(ls_c.coords[-1])
            if snapped_tx_utm == ls_c_first or snapped_tx_utm == ls_c_last:
                ls = ls_c
            else:
                ls = ls_d
            if snapped_tx_utm != shp.Point(ls.coords[0]):
                ls = ls.reverse()
            rp.is_intersection = [False for _ in range(1, len(ls.coords)-1)]
        else:
            first_ls = _edge_line_string(graph=graph, edge=(path[0], path[1], 0))
            _, first_ls = _split_line_string(first_ls, snapped_tx_utm)
            ls = first_ls
            rp.is_intersection = [False for _ in range(1, len(ls.coords)-1)]
            for i in range(1, len(path)-2):
                temp_ls = _edge_line_string(graph=graph, edge=(path[i], path[i+1], 0))
                ls = _merge_line_strings(ls, temp_ls)
                if len(ls.coords)-2 > len(rp.is_intersection):
                    rp.is_intersection.append(True)
                while len(ls.coords)-2 > len(rp.is_intersection):
                    rp.is_intersection.append(False)
            last_ls = _edge_line_string(graph=graph, edge=(path[-2], path[-1], 0))
            last_ls, _ = _split_line_string(last_ls, snapped_rx_utm)
            if last_ls is not None:
                ls = _merge_line_strings(ls, last_ls)
                if len(ls.coords)-2 > len(rp.is_intersection):
                    rp.is_intersection.append(True)
                while len(ls.coords)-2 > len(rp.is_intersection):
                    rp.is_intersection.append(False)

        lonLatLinestring, _ = ox.projection.project_geometry(ls, crs=crs_utm, to_crs=None,
                                                             to_latlong=True)
        rp.lat_lon_path = _line_string_to_coord_tuples(lonLatLinestring, True)
        rp.distances_m = _line_string_distances(ls)
        rp.turn_angles_deg = _line_string_turn_angles_deg(ls)
        rp.tx_lat_lon = (latt, lont)
        rp.rx_lat_lon = (latr, lonr)
        rp._projected_coords_path = _line_string_to_coord_tuples(ls, False)
        rp._projected_crs = crs_utm.srs
        rp_list.append(rp)

    rp_list = sorted(rp_list, key=lambda rp: (sum(rp.distances_m)))
    return rp_list[:num_paths]


def sort_by_street_corner_turns(radio_paths: list[StreetCanyonRadioPath],
                                turn_angle_threshold_deg: float=45) -> list[StreetCanyonRadioPath]:
    """
    Sorts a list of street canyon radio paths in ascending order by the number of turns at street
    corners. If multiple paths have the same number of turns, they are further sorted by ascending 
    travel distance.

    Args:
        radio_paths (list[StreetCanyonRadioPath]): List of street canyon radio paths, typically
            obtained from `compute_street_canyon_radio_paths()`.
        turn_angle_threshold_deg (float, optional): Turn-angle threshold used to identify street
            corners (degrees), with 0 <= turn_angle_threshold_deg <= 180. A turn-angle near zero
            means the path is going straight. A turn-angle near 90 represents a right-hand or a
            left-hand turn (the turn-angle will vary depending on how the streets intersect).
            Default is 45 degrees.
            
    Returns:
        list[StreetCanyonRadioPath]: List of radio paths sorted by increasing number of street-
            corner turns, with ties broken by path length (travel distance).
    """
    def key_func(radio_path):
        dists = radio_path.distances_to_street_corners(turn_angle_threshold_deg)
        return (len(dists), sum(dists))

    sorted_radio_paths = sorted(radio_paths, key=key_func)

    return sorted_radio_paths


def receiver_street_orientation(graph: StreetGraph|None, latt: float, lont: float,
                                latr: float, lonr: float) -> float:
    """
    Calculates the orientation, in degrees, of the street at the receiver location relative to the
    direct line between transmitter and receiver. The returned value ranges from 0 to 90 degrees.

    Args:
        graph (StreetGraph|None): StreetGraph for the area of interest, or None. If None, a
            temporary StreetGraph is created based on the receiver location.
        latt (float): Transmitter latitude (degrees), with -90 <= latt <= 90.
        lont (float): Transmitter longitude (degrees), with -180 <= lont <= 180.
        latr (float): Receiver latitude (degrees), with -90 <= latr <= 90.
        lonr (float): Receiver longitude (degrees), with -180 <= lonr <= 180.

    Returns:
        float: The receiver's street orientation relative to the direct transmitter-receiver path,
            in degrees (0 to 90 inclusive).
    """
    # pylint: disable=protected-access
    import osmnx as ox
    import shapely as shp

    if graph is None:
        graph = StreetGraph(bounds=[(latr, lonr)])

    G_utm  = graph._osm_graph # type networkx.MultiDiGraph
    crs_utm = graph._osm_graph.graph['crs']
    tx_utm: shp.Point = ox.projection.project_geometry(shp.Point(lont, latt), crs='epsg:4326',
                                                       to_crs=crs_utm, to_latlong=False)[0]
    rx_utm: shp.Point = ox.projection.project_geometry(shp.Point(lonr, latr), crs='epsg:4326',
                                                       to_crs=crs_utm, to_latlong=False)[0]

    rx_edge: tuple[float, float, float] # (nodeID, nodeID, 0)
    rx_edge = ox.distance.nearest_edges(G=G_utm, X=rx_utm.x, Y=rx_utm.y, return_dist=False)
    snapped_rx_utm: shp.Point = _nearest_edge_point(graph=graph, point=rx_utm, edge=rx_edge)

    ls: shp.LineString = _edge_line_string(graph=graph, edge=rx_edge)
    ls1, ls2 = _split_line_string(linestring=ls, splitter_point=snapped_rx_utm)

    if ls1 is not None:
        ls1_coords = list(ls1.coords)
        street_point = ls1_coords[-2]
        dist_m = ox.distance.euclidean(snapped_rx_utm.y, snapped_rx_utm.x, street_point[1],
                                       street_point[0])
        if dist_m == 0:
            street_point = None
    if street_point is None and ls2 is not None:
        ls2_coords = list(ls2.coords)
        street_point = ls2_coords[1]
        dist_m = ox.distance.euclidean(snapped_rx_utm.y, snapped_rx_utm.x, street_point[1],
                                       street_point[0])
        if dist_m == 0:
            raise RuntimeError('Failed to calculate rx street orientation.')

    rx_street_orientation_deg = _turn_angle_deg(x1=tx_utm.x, y1=tx_utm.y,
                                                x2=snapped_rx_utm.x, y2=snapped_rx_utm.y,
                                                x3=street_point[0], y3=street_point[1])
    if rx_street_orientation_deg > 90:
        rx_street_orientation_deg = 180 - rx_street_orientation_deg

    return rx_street_orientation_deg


def _ensure_edge_is_first_edge_of_path(path: list[int], edge: tuple[float, float, float]
                                       ) -> list[int]:
    if len(path)==1:
        node = path[0]
        if node==edge[0]:
            path.insert(0, edge[1])
        elif node==edge[1]:
            path.insert(0, edge[0])
        else:
            raise RuntimeError('Encountered unexpected node id.')
    elif len(path) >= 2:
        first_node = path[0]
        second_node = path[1]
        if (
            (first_node==edge[0] and second_node==edge[1]) or
            (first_node==edge[1] and second_node==edge[0])
        ):
            pass # edge is already first edge of path
        else:
            if first_node==edge[0]:
                path.insert(0, edge[1])
            elif first_node==edge[1]:
                path.insert(0, edge[0])
            else:
                raise RuntimeError('Encountered unexpected node id.')
    else:
        raise RuntimeError('Encountered unexpected path length.')
    return path


def _ensure_edge_is_last_edge_of_path(path: list[int], edge: tuple[float, float, float]
                                      ) -> list[int]:
    if len(path)==1:
        node = path[0]
        if node==edge[0]:
            path.append(edge[1])
        elif node==edge[1]:
            path.append(edge[0])
        else:
            raise RuntimeError('Encountered unexpected node id.')
    elif len(path) >= 2:
        last_node = path[-1]
        second_last_node = path[-2]
        if (
            (last_node==edge[0] and second_last_node==edge[1]) or
            (last_node==edge[1] and second_last_node==edge[0])
        ):
            pass # edge is already last edge of path
        else:
            if last_node==edge[0]:
                path.append(edge[1])
            elif last_node==edge[1]:
                path.append(edge[0])
            else:
                raise RuntimeError('Encountered unexpected node id.')
    else:
        raise RuntimeError('Encountered unexpected path length.')
    return path


def _nearest_edge_node(graph: StreetGraph, point: 'shapely.Point', edge: tuple[float, float, float]
                       ) -> int:
    import osmnx as ox
    pt_node1 = _node_point(graph=graph, node=edge[0])
    pt_node2 = _node_point(graph=graph, node=edge[1])
    dist1_m = ox.distance.euclidean(point.y, point.x, pt_node1.y, pt_node1.x)
    dist2_m = ox.distance.euclidean(point.y, point.x, pt_node2.y, pt_node2.x)
    if dist1_m < dist2_m:
        return edge[0]
    else:
        return edge[1]


def _nearest_edge_point(graph: StreetGraph, point: 'shapely.Point', edge: tuple[float, float, float]
                        ) -> 'shapely.Point':
    import shapely
    ls: shapely.LineString = _edge_line_string(graph=graph, edge=edge)
    pt = shapely.ops.nearest_points(ls, point)[0]
    return pt


def _node_point(graph: StreetGraph, node: int) -> 'shapely.Point':
    # pylint: disable=protected-access
    import shapely
    query_result = graph._nodes.query(f'osmid=={node}')
    coords = query_result.iloc[0, [graph._nodes.columns.get_loc('x'),
                                   graph._nodes.columns.get_loc('y')]]
    pt = shapely.Point(coords.x, coords.y)
    return pt


def _edge_line_string(graph: StreetGraph, edge: tuple[float, float, float]) -> 'shapely.Point':
    # pylint: disable=protected-access
    query_result = graph._edges.query(
        f'(u=={edge[0]} & v=={edge[1]}) | (u=={edge[1]} & v=={edge[0]})')
    ls = query_result.iloc[0, graph._edges.columns.get_loc('geometry')]
    from_node = query_result.iloc[0, graph._edges.columns.get_loc('from')]
    if from_node != edge[0]:
        ls = ls.reverse()
    return ls


def _line_string_distances(linestring: 'shapely.LineString') -> list[float]:
    import osmnx as ox
    distances = []
    for i in range(1, len(linestring.coords)):
        prev_coord = linestring.coords[i-1]
        coord = linestring.coords[i]
        dist = ox.distance.euclidean(y1=prev_coord[1], x1=prev_coord[0], y2=coord[1], x2=coord[0])
        distances.append(dist)
    return distances


def _line_string_turn_angles_deg(linestring: 'shapely.LineString') -> list[float]:
    angles_deg = []
    if len(linestring.coords) < 3:
        return angles_deg
    for i in range(1, len(linestring.coords)-1):
        prev_coord = linestring.coords[i-1]
        coord = linestring.coords[i]
        next_coord = linestring.coords[i+1]
        angle = _turn_angle_deg(x1=prev_coord[0], y1=prev_coord[1], x2=coord[0], y2=coord[1],
                                x3=next_coord[0], y3=next_coord[1])
        angles_deg.append(angle)
    return angles_deg


def _turn_angle_deg(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> float:
    # return value from 0 (going straight forward) to 180 (making a U-turn)
    bearing1_deg = degrees(atan2(x2-x1, y1-y2))
    bearing2_deg = degrees(atan2(x3-x2, y2-y3))
    angle_deg = abs(bearing1_deg-bearing2_deg)
    if angle_deg > 180:
        angle_deg = 360 - angle_deg
    return angle_deg


def _merge_line_strings(ls1: 'shapely.LineString', ls2: 'shapely.LineString'
                        ) -> 'shapely.LineString':
    import shapely
    multi_line = shapely.MultiLineString([ls1, ls2])
    # if end points do not corresponds, line_merge returns a MultiLineString instead
    # of a LineString otherwise
    merged_line = shapely.line_merge(line=multi_line, directed=True)
    if shapely.get_type_id(merged_line) != 1: # 1 is LineString
        raise RuntimeError('Failed to merge LineStrings.')
    return merged_line


def _split_line_string(linestring: 'shapely.LineString', splitter_point: 'shapely.Point'
                       ) -> tuple['shapely.LineString', 'shapely.LineString']:
    import shapely
    linestring = shapely.ops.snap(g1=linestring, g2=splitter_point, tolerance=0.001)
    geometry_collection = shapely.ops.split(geom=linestring, splitter=splitter_point)
    # "If the splitter does not split the geometry, a collection with a single geometry equal to
    # the input geometry is returned."
    if len(geometry_collection.geoms) == 2:
        return (geometry_collection.geoms[0], geometry_collection.geoms[1])
    elif len(geometry_collection.geoms) == 1:
        if shapely.Point(linestring.coords[0]) == splitter_point:
            return (None, geometry_collection.geoms[0])
        elif shapely.Point(linestring.coords[-1]) == splitter_point:
            return (geometry_collection.geoms[0], None)
    raise RuntimeError('Failed to split LineString.')


def _line_string_to_coord_tuples(linestring: 'shapely.LineString', invertxy: bool
                                 ) -> list[tuple[float,float]]:
    tuple_list = []
    if invertxy is False:
        for coord in list(linestring.coords):
            tuple_list.append((coord[0], coord[1]))
    else:
        for coord in list(linestring.coords):
            tuple_list.append((coord[1], coord[0]))
    return tuple_list


def _is_intersection(radio_path: StreetCanyonRadioPath, x_projected_coord: float, y_projected_coord
                     ) -> bool:
    # pylint: disable=protected-access
    for i, projected_coord in enumerate(radio_path._projected_coords_path):
        x = projected_coord[0]
        y = projected_coord[1]
        if x == x_projected_coord and y == y_projected_coord:
            if (i-1) >= 0 and (i-1) < len(radio_path.is_intersection):
                return radio_path.is_intersection[i-1]
            else:
                return False
    raise RuntimeError('Failed to find point.')
