# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Example for obtaining various terrain profiles and using ITU-R P.1546-6 for predicting basic
transmission loss.
"""

from propakai import p1546_6 as p1546
from propakai.extras import topography as topo


if __name__ == '__main__':
    # NOTE : Specify your terrain elevation data directory here
    terrain_height_dir = None

    f_mhz = 3600 # Frequency (MHz)
    t_percent = 50 # Time percentage Lb is not exceeded (%)
    latt = 45 # Latitude of transmitter (degrees)
    lont = -75 # Longitude of transmitter (degrees)
    latr = 45.01 # Latitude of receiver (degrees)
    lonr = -75.01 # Longitude of receiver (degrees)
    ha_m = 12 # Transmit antenna height above ground (m)
    h2_m = 1.5 # Receive antenna height above ground (m)
    env2 = p1546.Environment.RURAL_OR_OPEN # Environment type at receiver
    res_m = 30 # Terrain profile resolution (m)

    d_profile_km = topo.distance_profile_km(latt, lont, latr, lonr, res_m)
    coords = topo.lat_lon_profile(latt, lont, latr, lonr, res_m)

    h_profile_mamsl = None
    if terrain_height_dir is not None:
        print('Getting terrain height profile...', end='')
        terrain_height_reader = topo.GeoRasterDirectoryReader(terrain_height_dir, recursive=False,
                                                    extensions=['.tif']) # or other raster type(s)
        h_profile_mamsl = terrain_height_reader.read_floats(coords, bilinear_interpol=True)
        print('done')

    print('Getting path type profile...', end='')
    # First call to radio_climatic_zone4_profile() is slow as coastal vectorial data from IDWM is
    # loaded into memory. Subsequent calls are faster.
    path_type_profile = topo.radio_climatic_zone4_profile(coords)
    # Possible climatic zones from radio_climatic_zone4_profile() are:
    #   1 (B_COLD_SEA), 2 (C_WARM_SEA), 3 (A1_COASTAL_LAND), 4 (A2_INLAND).
    # They must be mapped to one of the path types for P.1546, which are:
    #   1 (COLD_SEA), 2 (WARM_SEA), 4 (LAND).
    path_map = {1: 1, 2: 2, 3: 4, 4: 4}
    path_type_profile = [path_map[x] for x in path_type_profile]
    print('done')

    # Alternately for an all-land path, path_type_profile may simply be set to None.

    lb_db, E_dbuvm = p1546.basic_transmission_loss(f_mhz, t_percent, ha_m, h2_m, env2, d_profile_km,
                                                   h_profile_mamsl, path_type_profile)
    print(f'Path loss: {lb_db:.2f} dB')
