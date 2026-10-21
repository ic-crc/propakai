# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Provides an interface to using the ITU Digitized World Map (IDWM) dataset from the ITU-R Geospatial
Catalog. Contrarily to other modules in geo_catalog, gc_idwm downloads and stores data files
(geojson format) instead of qurerying the interpolation service from the ITU.

https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/idwm

gc_idwm requires **geopandas** and **shapely** to be installed. If they are not already, you may do
so with:
```bash
python -m pip install geopandas shapely
```
"""

from typing import TYPE_CHECKING
from os.path import join, exists
import enum
from threading import Lock
from filelock import FileLock
from .. import _download_utils as _du

if TYPE_CHECKING:
    # imports here are not performed at runtime, only when type-checking
    import geopandas


__all__ = ['MapId',
           'RadioClimaticZone3',
           'RadioClimaticZone4',
           'get_filepath',
           'ground_conductivity_vlf',
           'ground_conductivity_mf',
           'ground_conductivity_rj81',
           'radio_climatic_zone3',
           'radio_climatic_zone4',
           'aeronautical_zones_mwara',
           'aeronautical_zones_rdara',
           'aeronautical_zones_volmet',
           'maritime_zone',
           'ciraf_zone']


class MapId(enum.Enum):
    """Available maps from the ITU Digitized World Map (IDWM) product."""
    GC_VLF         =  1
    GC_MF          =  2
    GC_RJ81        =  3
    COASTAL        =  4
    AERO_MWARA     =  5
    AERO_RDARA     =  6
    AERO_VOLMET    =  7
    MARITIME       =  8
    CIRAF          =  9
    COUNTRIES      = 10
    LAKES          = 11
    LAKES_LINES    = 12
    PROPA_GE06     = 13
    PROPA_GE84     = 14
    PROPA_GE89     = 15
    PROPA_ST61     = 16
    RAIN_CLIM      = 17
    ALLOT_AP25     = 18
    XR2_ALLOT_RJ88 = 19
    NOISE_RJ81     = 20
    NOISE_RJ88     = 21
    NOISE_GE75     = 22


class RadioClimaticZone3(enum.Enum):
    """
    3 types of radio-climatic zones, as appearing in the IDWM product.

    - SEA: Seas, oceans and other large bodies of water (i.e. covering a circle of at least 100 km
    in diameter).  
    - COASTAL_LAND: Coastal land and shore areas, i.e. land adjacent to the sea up to an altitude
    of 100 m relative to mean sea or water level, but limited to a distance of 50 km from the
    nearest sea area.  
    - INLAND: All land, other than coastal and shore areas defined as COASTAL_LAND above.
    """
    SEA = 1
    COASTAL_LAND = 3
    INLAND = 4


class RadioClimaticZone4(enum.Enum):
    """
    4 types of radio-climatic zones, as defined in some recommendations like P.620.

    - A1_COASTAL_LAND: coastal land and shore areas, i.e. land adjacent to a Zone B or Zone C area
    (see below), up to an altitude of 100 m relative to mean sea or water level, but limited to a
    maximum distance of 50 km from the nearest Zone B or Zone C area as the case may be.
    - A2_INLAND: all land, other than coastal land and shore defined as Zone A1 above.
    - B_COLD_SEA: cold seas, oceans and large bodies of inland water situated at latitudes above
    30°, with the exception of the Mediterranean and the Black Sea.
    - C_WARM_SEA: warm seas, oceans and large bodies of inland water situated at latitudes below
    30°, as well as the Mediterranean and the Black Sea.
    """
    B_COLD_SEA = 1
    C_WARM_SEA = 2
    A1_COASTAL_LAND = 3
    A2_INLAND = 4


def get_filepath(map_id: MapId) -> str:
    """
    Gets the local GeoJSON file path for the specified IDWM map. If not present, the file is first
    downloaded from the ITU-R Geospatial Catalog.
    
    Args:
        map_id (MapId): IDWM map identifier.

    Returns:
        str: Full path to the local GeoJSON file for the specified map id.
    """
    filepath = _download_map(map_id)
    return filepath


def ground_conductivity_vlf(lat: float, lon: float) -> float|None:
    """
    ITU-R P.832-4.

    Gets ground conductivity (S/m) from the World Atlas of Ground Conductivities for the VLF band
    (limited in application to frequencies up to 30 kHz).

    This information is intended to be used for field strength predictions in connection with the
    ground-wave propagation curves contained in Recommendation ITU-R P.368.
    
    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        float|None: Ground conductivity (S/m), or None when no value can be obtained (e.g. over
            sea).
    """
    gdf = _get_map_data(MapId.GC_VLF, lat, lon)
    try:
        value = gdf.iloc[0]['gnd_cond'] # in mS/m
        return float(value)/1000 # convert to S/m
    except IndexError:
        return None


def ground_conductivity_mf(lat: float, lon: float) -> float|None:
    """
    ITU-R P.832-4.

    Gets ground conductivity (S/m) from the World Atlas of Ground Conductivities for the MF band.

    This information is intended to be used for field strength predictions in connection with the
    ground-wave propagation curves contained in Recommendation ITU-R P.368.
    
    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        float|None: Ground conductivity (S/m), or None when no value can be obtained (e.g. over
            sea).
    """
    gdf = _get_map_data(MapId.GC_MF, lat, lon)
    try:
        value = gdf.iloc[0]['gnd_cond'] # in mS/m
        return float(value)/1000 # convert to S/m
    except IndexError:
        return None


def ground_conductivity_rj81(lat: float, lon: float) -> float|None:
    """
    ITU-R P.832-4.

    Gets ground conductivity (S/m) value for the RJ81 agreement.
    
    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        float|None: Ground conductivity (S/m) for the RH81 agreement, or None when no value can
            be obtained.
    """
    gdf = _get_map_data(MapId.GC_RJ81, lat, lon)
    try:
        value = gdf.iloc[0]['gnd_cond'] # in mS/m
        return float(value)/1000 # convert to S/m
    except IndexError:
        return None


def radio_climatic_zone3(lat: float, lon: float) -> RadioClimaticZone3:
    """
    ITU-R P.452-18, Annex 1, Section 3.2.1.  
    ITU-R P.1812-8, Annex 1, Section 3.3.  
    ITU-R P.620-7, Annex 1, Section 4.2.

    Gets the radio-climatic zone.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        RadioClimaticZone3: SEA (1), COASTAL_LAND (3), or INLAND (4).
    """
    gdf = _get_map_data(MapId.COASTAL, lat, lon)
    # NOTE: let code possibly raise exception here (instead of returning None) since a climatic
    # zone value is expected for any valid lat and lon values.
    value = gdf.iloc[0]['zone_type_id']
    return RadioClimaticZone3(value)


def radio_climatic_zone4(lat: float, lon: float) -> RadioClimaticZone4:
    """
    ITU-R P.620-7, Annex 1, Section 4.2.

    Gets the radio-climatic zone.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        RadioClimaticZone4: B_COLD_SEA (1), C_WARM_SEA (2), A1_COASTAL_LAND (3), or A2_INLAND (4).
    """
    zone3 = radio_climatic_zone3(lat, lon)
    if zone3 == RadioClimaticZone3.COASTAL_LAND:
        return RadioClimaticZone4.A1_COASTAL_LAND
    if zone3 == RadioClimaticZone3.INLAND:
        return RadioClimaticZone4.A2_INLAND

    # zone3 == RadioClimaticZone3.SEA
    if abs(lat) < 30:
        return RadioClimaticZone4.C_WARM_SEA

    from shapely.geometry import Point, Polygon
    # polygon enclosing the Mediterranean and the Black Sea
    warm_seas_coords = [(39.852,-5.231), (33.581,-5.548), (28.287,18.704), (30.558,32.223),
                        (32.829,43.260), (51.311,43.471), (47.615,7.298), (41.489,-1.468)]
    warm_seas_polygon = Polygon([(lon, lat) for lat, lon in warm_seas_coords])
    if warm_seas_polygon.contains(Point(lon, lat)):
        return RadioClimaticZone4.C_WARM_SEA
    return RadioClimaticZone4.B_COLD_SEA


def aeronautical_zones_mwara(lat: float, lon: float) -> list[str]:
    """
    Gets the Aeronautical Zone(s) (MWARA) at the specified location.
    
    Maps of major world air route area (MWARA), i.e. areas embracing a certain number of major
    world air routes, which generally follow the same traffic pattern and are so related
    geographically that the same frequency families may logically be applied.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        list[str]: List of Aeronautical Zone(s) (MWARA) at the specified location.
    """
    gdf = _get_map_data(MapId.AERO_MWARA, lat, lon)
    return gdf['zone_id'].tolist()


def aeronautical_zones_rdara(lat: float, lon: float) -> list[str]:
    """
    Gets the Aeronautical Zone(s) (RDARA) at the specified location.
    
    Maps of Regional and Domestic Air Route Area (RDARA), i.e. areas embracing a certain number of
    the air routes using the Aeronautical Mobile (R) Service.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        list[str]: List of Aeronautical Zone(s) (RDARA) at the specified location.
    """
    gdf = _get_map_data(MapId.AERO_RDARA, lat, lon)
    return gdf['zone_id'].tolist()


def aeronautical_zones_volmet(lat: float, lon: float) -> list[str]:
    """
    Gets the Aeronautical Zone(s) (VOLMET) at the specified location.
    
    Maps of VOLMET Reception Area is an area within which aircraft should be able to receive
    broadcasts from one or more stations in the associated VOLMET Allotment Area.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        list[str]: List of Aeronautical Zone(s) (VOLMET) at the specified location.
    """
    gdf = _get_map_data(MapId.AERO_VOLMET, lat, lon)
    return gdf['zone_id'].tolist()


def maritime_zone(lat: float, lon: float) -> int|None:
    """
    Gets the maritime zone (MAR01 to MAR22) for the maritime mobile service at the specified
    location.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        int|None: The maritime zone at the specified location, or None over land.
    """
    gdf = _get_map_data(MapId.MARITIME, lat, lon)
    value = gdf.iloc[0]['zone_id']
    if value == 'Land':
        return None
    return int(value)


def ciraf_zone(lat: float, lon: float) -> int:
    """
    Gets the CIRAF zone for High Frequency (HF) broadcasting at the specified location.

    Args:
        lat (float): Latitude (degrees), with -90 <= lat <= 90.
        lon (float): Longitude (degrees), with -180 <= lon <= 180.
    
    Returns:
        int: The CIRAF zone for High Frequency (HF) broadcasting at the specified location.
    """
    gdf = _get_map_data(MapId.CIRAF, lat, lon)
    value = gdf.iloc[0]['zone_id']
    return int(value)


def _get_map_data(map_id: MapId, lat: float, lon: float) -> 'geopandas.GeoDataFrame':
    from shapely.geometry import Point
    gdf = _thread_safe_get_map(map_id)
    result = gdf[gdf.contains(Point(lon, lat))]
    return result


def _thread_safe_get_map(map_id: MapId) -> 'geopandas.GeoDataFrame':
    with _gc_idwm_shared['gdf_maps_lock']:
        if map_id not in _gc_idwm_shared['gdf_maps']:
            try:
                gdf = _load_map(map_id)
            except FileNotFoundError:
                _download_map(map_id)
                gdf = _load_map(map_id)
            _gc_idwm_shared['gdf_maps'][map_id] = gdf
        gdf = _gc_idwm_shared['gdf_maps'][map_id]
    return gdf


def _load_map(map_id: MapId) -> 'geopandas.GeoDataFrame':
    import geopandas as gpd
    pathname = join(_du.install_dir(), _gc_idwm_shared['DATA_DIR'], _get_map_filename(map_id))
    if not exists(pathname):
        raise FileNotFoundError(f'File not found: {pathname}')
    gdf = gpd.read_file(pathname)
    gdf = gdf.to_crs(epsg=4326)
    return gdf


def _download_map(map_id: MapId) -> str:
    data_dir = _gc_idwm_shared['DATA_DIR']
    full_path_data_dir = join(_du.install_dir(), data_dir)
    filename = _get_map_filename(map_id)
    lock = FileLock(_du.get_lockfile_pathname(f'{data_dir}_{filename}'))
    with lock:
        if _du.files_all_exist(full_path_data_dir, [filename]) is False:
            _du.download(_get_map_url(map_id), full_path_data_dir, filename, False)
            _du.print_notice()
    return join(full_path_data_dir, filename)


def _get_map_filename_no_ext(map_id: MapId) -> str:
    filenames = {
        MapId.GC_VLF: 'gc_vlf',
        MapId.GC_MF: 'gc_mf',
        MapId.GC_RJ81: 'gc_x2',
        MapId.COASTAL: 'coastal',
        MapId.AERO_MWARA: 'aereo_mwara',
        MapId.AERO_RDARA: 'aereo_rdara',
        MapId.AERO_VOLMET: 'aereo_volmet',
        MapId.MARITIME: 'maritime',
        MapId.CIRAF: 'hfbc_ciraf_zones',
        MapId.COUNTRIES: 'idwm',
        MapId.LAKES: 'idwm_lakes',
        MapId.LAKES_LINES: 'idwm_lakes_lines',
        MapId.PROPA_GE06: 'propa_ge06',
        MapId.PROPA_GE84: 'propa_ge84',
        MapId.PROPA_GE89: 'propa_ge89',
        MapId.PROPA_ST61: 'propa_st61',
        MapId.RAIN_CLIM: 'rain_zones',
        MapId.ALLOT_AP25: 'allot_ap25',
        MapId.XR2_ALLOT_RJ88: 'allot_mf_x2',
        MapId.NOISE_RJ81: 'noise_zones_rj81',
        MapId.NOISE_RJ88: 'noise_zones_rj88',
        MapId.NOISE_GE75: 'noise_zones_ge75',
    }
    return filenames[map_id]


def _get_map_filename(map_id: MapId) -> str:
    return f'{_get_map_filename_no_ext(map_id)}.json'


def _get_map_url(map_id: MapId) -> str:
    filename = _get_map_filename_no_ext(map_id)
    url = r'https://br-geoportal.itu.int/ITU-R/BR-Geo/wfs?service=WFS&version=2.0.0&request=GetF' \
        rf'eature&typeNames=vector%3A{filename}&outputFormat=application%2Fjson'
    return url


_gc_idwm_shared = {
    'DATA_DIR': 'idwm',
    'gdf_maps_lock': Lock(),
    'gdf_maps': {}
}
