# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates path loss according to Section 4.2.2.1 of ITU-R P.1411-13."""

import matplotlib.pyplot as plt
from propakai import p1411_13 as p1411
from propakai.extras import buildings as bldg
from propakai.extras import topography as topo


def main():
    print('\nITU-R P.1411-13, site specific model for propagation over rooftops in an urban area')

    freq_ghz = 10.0
    tx_height_m = 55.0
    rx_height_m = 2.0
    tx_lat = 45.4314310
    tx_lon = -75.6635237
    rx_lat = 45.4288756
    rx_lon = -75.6627794

    # Download building footprints from OpenStreetMap. Building heights are estimated from the
    # number of floors ('building:levels' tag) when present. Otherwise buildings are assigned
    # the specified default height in meters. This building data will be used to calculate input
    # parameters for the propagation model.
    bounds = bldg.LatLonBox((tx_lat, tx_lon), (rx_lat, rx_lon))
    bldg_list = bldg.from_open_street_map(bounds, avg_floor_height_m=3.0, default_height_m=3.0)

    # NOTE: Alternately, if you have better building footprint and height data available from a
    # shapefile (.shp), you may use the bldg.from_shapefile() function instead.

    # Display the building heights profile on the direct path from the transmitter to the receiver.
    sampling_res_m = 1.0
    lat_lon_profile = topo.lat_lon_profile(tx_lat, tx_lon, rx_lat, rx_lon, sampling_res_m)
    dist_profile_m = topo.distance_profile_m(tx_lat, tx_lon, rx_lat, rx_lon, sampling_res_m)
    bldg_list = bldg.filter_by_path_intersection(bldg_list, lat_lon_profile)
    bldg_height_profile_m = bldg.height_profile(bldg_list, lat_lon_profile)
    _display_building_height_profile(list(dist_profile_m), list(bldg_height_profile_m),
                                     'Building height profile')

    # In order to get correct metrics for the multi-screen diffraction model, we remove the two
    # smaller buildings (i.e. the buildings that are not part of the multi-screen).
    bldg_list = [b for b in bldg_list if b.height_m > 25]

    # Display the updated building heights profile.
    bldg_height_profile_m = bldg.height_profile(bldg_list, lat_lon_profile)
    _display_building_height_profile(list(dist_profile_m), list(bldg_height_profile_m),
                                     'Updated building height profile (multi-screen)')

    # Calculate path loss along the transmitter to receiver path.
    path_loss_profile_db = [float('nan')] * len(lat_lon_profile)
    for i in range(1, len(lat_lon_profile)):

        if bldg_height_profile_m[i] > 0:
            continue # skip indoor locations

        # Extract building metrics to use as inputs for the propagation model (see ITU-R P.1411-13,
        # FIGURE 2 for more details):
        #   d_m:  Path length (great-circle distance) from the transmitter to the receiver (meters).
        #   hr_m: Average height of buildings along the path (meters).
        #   b_m:  Average building separation distance along the path (meters).
        #   l_m:  Length of the path covered by buildings (meters).
        #   w_m:  Street width at the receiver location (meters), which is the distance between
        #         the two buildings encompassing the receiver. -1 if can't be calculated.
        d_m, hr_m, b_m, l_m, w_m = bldg.p1411_urban_metrics(bldg_list, latt=tx_lat, lont=tx_lon,
                                       latr=lat_lon_profile[i][0], lonr=lat_lon_profile[i][1])

        if l_m > 0 and w_m is None:
            continue # skip points where the street width cannot be obtained

        if hr_m is None or b_m is None or w_m is None:
            continue # skip point if could not retrieve required metric

        lb = p1411.site_specific_over_rooftops_urban(
                f_ghz=freq_ghz, d_m=d_m, h1_m=tx_height_m, h2_m=rx_height_m, hr_m=hr_m, l_m=l_m,
                b_m=b_m, w2_m=w_m,
                phi_deg=90.0, # Street orientation with respect to the direct path (deg).
                env=p1411.EnvironmentD.METROPOLITAN_CENTRE) # env is only used when f_ghz <= 2

        path_loss_profile_db[i] = lb

    # Plot profiles
    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax2 = ax1.twinx()
    ax1.plot(dist_profile_m, path_loss_profile_db, 'g-', label='path loss (dB)')
    ax2.plot(dist_profile_m, bldg_height_profile_m, color='#B0B0B0')
    ax1.invert_yaxis()
    ax1.set_xlabel('Path length (m)')
    ax1.set_ylabel('Path loss (dB)')
    ax2.set_ylabel('Building height (m)')
    ax1.set_title('ITU-R P.1411-13, site specific model for propagation over rooftops in an ' \
                  f'urban area, {freq_ghz:.1f} GHz')
    ax1.legend()
    plt.show()


def _display_building_height_profile(dist_profile_m: list[float],
                                     bldg_heights_profile_m: list[float], title: str):
    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.plot(dist_profile_m, bldg_heights_profile_m, color='#B0B0B0')
    ax1.set_xlabel('Path length (m)')
    ax1.set_ylabel('Building height (m)')
    ax1.set_title(title)
    plt.show()


if __name__ == '__main__':
    main()
