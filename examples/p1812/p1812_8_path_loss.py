# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Example for obtaining various terrain profiles and using ITU-R P.1812-8 for predicting basic
transmission loss.

NOTE: For this example to run successfully, you need to specify the full path to directories
      containing terrain data (see terrain_height_dir, clutter_cat_dir, surface_height_dir).
"""

import array
from propakai import p1812_8_dso as p1812
from propakai.extras import topography as topo


if __name__ == '__main__':
    f_ghz = 3.6 # Frequency (GHz)
    p_percent = 50 # Annual time percentage Lb not exceeded (%)
    pl_percent = 50 # Location percentage Lb not exceeded (%)
    latt = 45 # Latitude of transmitter (degrees)
    lont = -75 # Longitude of transmitter (degrees)
    latr = 45.01 # Latitude of receiver (degrees)
    lonr = -75.01 # Longitude of receiver (degrees)
    htg_m = 12 # Transmit antenna height above ground (m)
    hrg_m = 1.5 # Receive antenna height above ground (m)
    vpol = True # Is polarization vertical (True) or horizontal (False)
    res_m = 30 # Terrain profile resolution (m)

    # NOTE : Specify your terrain data directories
    terrain_height_dir = '<enter directory>'
    clutter_cat_dir = '<enter directory>'
    surface_height_dir = '<enter directory>'


    d_km = topo.distance_profile_km(latt, lont, latr, lonr, res_m)
    coords = topo.lat_lon_profile(latt, lont, latr, lonr, res_m)


    print('Getting terrain height profile...', end='')
    terrain_height_reader = topo.GeoRasterDirectoryReader(terrain_height_dir, recursive=False,
                                                    extensions=['.tif']) # or other raster type(s)
    h_mamsl = terrain_height_reader.read_floats(coords, bilinear_interpol=True)
    print('done')


    print('Getting clutter category profile...', end='')
    clutter_cat_reader = topo.GeoRasterDirectoryReader(clutter_cat_dir, recursive=False,
                                                    extensions=['.tif']) # or other raster type(s)
    native_cc = clutter_cat_reader.read_ints(coords)
    print('done')

    # We then need to convert the native clutter categories to one of the following:
    #   1) Clutter categories from P.1812 (1=Water/Sea, 2=Open/Rural, 3=Suburban,
    #                                      4=Urban/Trees/Forest, 5=Dense Urban).
    #   2) Representative clutter heights (m).

    # Example for option 1) with ESA WorldCover clutter categories (10=Tree cover, 50=Built-up,
    # 80=Permanent water bodies), adjust as necessary.
    cat_mapping = {10: p1812.ClutterCategory.URBAN_TREES_FOREST.value,
                   50: p1812.ClutterCategory.URBAN_TREES_FOREST.value,
                   80: p1812.ClutterCategory.WATER_SEA.value}
    default_cat: int = p1812.ClutterCategory.OPEN_RURAL.value # Open/Rural for all others
    cc = array.array('i', [cat_mapping.get(x, default_cat) for x in native_cc])

    # Example for option 2) with ESA WorldCover clutter categories (10=Tree cover, 50=Built-up,
    # 80=Permanent water bodies), adjust as necessary.
    h_mapping = {10: 15.0, # i.e. 15 meters
                 50: 15.0,
                 80: 0.0}
    default_h = 0.0 # 0 m for all others
    rch_m = array.array('d', [h_mapping.get(x, default_h) for x in native_cc])


    # If available, we may use surface height data instead of clutter data.
    print('Getting surface height profile...', end='')
    surface_height_reader = topo.GeoRasterDirectoryReader(surface_height_dir, recursive=False,
                                                    extensions=['.tif']) # or other raster type(s)
    sh_mamsl = surface_height_reader.read_floats(coords, bilinear_interpol=True)
    print('done')


    # Optionally a radio-climatic zone profile may be obtained using the coastal area map from the
    # IDWM product. See
    # https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/collections/idwm/items/coastal
    print('Getting radio-climatic zone profile...', end='')
    rcz = topo.radio_climatic_zone3_profile(coords)
    print('done')


    # Using all profiles as input for the purpose of demonstration here, however only one of cc,
    # rch_m and sh_mamsl need to be specified. rcz may be omitted for inland paths.
    lb_db = p1812.basic_transmission_loss(f_ghz, p_percent, pl_percent, latt, lont, latr, lonr,
                                          htg_m, hrg_m, vpol, d_km, h_mamsl, cc, rch_m, sh_mamsl,
                                          rcz)
    print(f'Path loss: {lb_db:.2f} dB')
