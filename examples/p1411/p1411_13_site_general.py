# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates path loss according to Section 4.1.1 of ITU-R P.1411-13."""


from os.path import dirname, abspath, join
import matplotlib.pyplot as plt
from propakai import p1411_13 as p1411
from propakai.extras import topography as topo
from propakai.extras import buildings as bldg


if __name__ == '__main__':

    print('\nITU-R P.1411-13, site general model for propagation within street canyons')

    freq_ghz = 28.0
    tx_lat = 45.419626
    tx_lon = -75.6999886
    rx_lat = 45.4193700
    rx_lon = -75.6970786
    radio_env = p1411.EnvironmentA.URBAN_HIGH_RISE

    # Download building footprints from OpenStreetMap. Building heights are estimated from the
    # number of floors ('building:levels' tag) when present. Otherwise buildings are assigned
    # the specified default height in meters. This building data will be used to determine whether
    # a path is in line-of-sight (LoS) or non-line-of-sight (NLoS).
    print('Getting building footprint data...', end='', flush=True)
    bldg_bounds = bldg.LatLonBox((tx_lat, tx_lon), (rx_lat, rx_lon))
    bldg_list = bldg.from_open_street_map(bounds=bldg_bounds, default_height_m=3.0)
    print('done', flush=True)

    # Optionally, obtained footprints may be exported to geojson and visualized using a
    # GIS application.
    script_dir = dirname(abspath(__file__))
    bldg.to_geojson_file(bldg_list, join(script_dir, 'osm_footprints.geojson'))

    sampling_res_m = 1.0
    lat_lon_profile = topo.lat_lon_profile(tx_lat, tx_lon, rx_lat, rx_lon, sampling_res_m)
    dist_profile_km = topo.distance_profile_km(tx_lat, tx_lon, rx_lat, rx_lon, sampling_res_m)
    bldg_height_profile_m = bldg.height_profile(bldg_list, lat_lon_profile)
    path_loss_profile_db = [float('nan')] * len(dist_profile_km)
    path_loss_profile_db_out_of_range = [float('nan')] * len(dist_profile_km)

    print('Computing path loss...', end='', flush=True)
    for i in range(1, len(dist_profile_km)):

        if bldg_height_profile_m[i] > 0:
            continue # skip indoor locations

        # Site-general models from ITU-R P.1411 do not use antenna height parameters. Here antenna
        # height values of 1.5m are used only to help determine whether there is a LoS or not.
        is_los = topo.is_line_of_sight(latt=tx_lat, lont=tx_lon, ht_mamsl=1.5,
                                       latr=rx_lat, lonr=rx_lon, hr_mamsl=1.5,
                                       dp_km=dist_profile_km[:i+1],
                                       hp_mamsl=bldg_height_profile_m[:i+1])

        if is_los is True:
            path_type = p1411.PathType.LOS
        else:
            path_type = p1411.PathType.NLOS

        # Note: Two other functions for site general models are available, namely
        # site_general_over_rooftops() and site_general_near_street_level().
        Lb, warn_flag = p1411.site_general_street_canyons(f_ghz=freq_ghz,
                                                          d_m=dist_profile_km[i]*1000,
                                                          env=radio_env, path_type=path_type,
                                                          add_gaussian_random=False)

        # check if the frequency or distance is out of range for the model
        if warn_flag == 0:
            path_loss_profile_db[i] = Lb
        else:
            path_loss_profile_db_out_of_range[i] = Lb
    print('done', flush=True)

    # Plot profiles
    dist_profile_m = [d*1000 for d in dist_profile_km]
    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax2 = ax1.twinx()
    ax1.plot(dist_profile_m, path_loss_profile_db, 'g-', label='path loss (dB)')
    ax1.plot(dist_profile_m, path_loss_profile_db_out_of_range, 'xr',
             label="path loss (dB) - out of model's valid range")
    ax2.plot(dist_profile_m, bldg_height_profile_m, color='#B0B0B0')
    ax1.invert_yaxis()
    ax1.set_xlabel('Path length (m)')
    ax1.set_ylabel('Path loss (dB)')
    ax2.set_ylabel('Building height (m)')
    ax1.set_title('ITU-R P.1411-13, site general model for propagation within street canyons, ' \
                  f'{freq_ghz:.1f} GHz')
    ax1.legend()
    plt.show()
