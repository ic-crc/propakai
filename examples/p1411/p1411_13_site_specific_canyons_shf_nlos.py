# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Calculates path loss according to equations from Section 4.1.3.2 of ITU-R P.1411-13. Distances to
and from the street corners are computed using OpenStreetMap data.
"""

from os.path import dirname, abspath, join
from math import ceil
import matplotlib.pyplot as plt
from propakai import p1411_13 as p1411
from propakai import p530_18 as p530
from propakai.extras import streets


if __name__ == '__main__':
    print('\nITU-R P.1411-13, site specific model for propagation within ' \
          'street canyons (NLoS) in the 2 to 38 GHz band')

    freq_ghz = 26.0
    tx_lat = 45.41853319
    tx_lon = -75.69908430
    tx_height_m = 5.0
    tx_street_width_m = 19.0
    rx_lat = 45.4212524
    rx_lon = -75.6972646
    rx_height_m = 1.5
    p = 0.0

    # Download OpenStreetMap data and get a street graph for the area surrounding the transmitter
    # and receiver locations.
    street_graph = streets.StreetGraph(bounds=[(tx_lat, tx_lon), (rx_lat, rx_lon)])

    # If desired, the street graph may be displayed.
    street_graph.display()

    # GetStreetCanyonsRadioPaths() computes one or more paths following street lines based on a
    # shortest travel distance algorithm. The shortest path is often but not always the path having
    # the lowest number of turns at street crossings, so we will ask for a few different paths to be
    # returned and then select one with the lowest amount of turns at street crossings (usually
    # preferable propagation-wise).
    radio_paths = streets.compute_street_canyon_radio_paths(graph=street_graph, latt=tx_lat,
                                                            lont=tx_lon, latr=rx_lat, lonr=rx_lon,
                                                            num_paths=4)

    # We can have the paths simplified before the sort takes place. This is ususally helpful as it
    # removes very small street sections that unnecessarily complexifies the path.
    radio_paths = [rp.new_simplified() for rp in radio_paths]

    # Sort paths in ascending order of turns at street crossings and select the first one.
    selected_path = streets.sort_by_street_corner_turns(radio_paths=radio_paths)[0]

    # If desired, a path may be exported to a geojson file and visualized using a GIS application.
    script_dir = dirname(abspath(__file__))
    selected_path.to_geojson_file(join(script_dir, 'radio_path.geojson'))

    x_m_list = selected_path.distances_to_street_corners()
    alpha_deg_list = selected_path.street_corner_angles()

    # Check that the selected path only has one turn at street crossings, so that we can apply the
    # model.
    if len(alpha_deg_list) != 1:
        raise RuntimeError('Could not find path with one street corner turn.')

    total_travel_dist_m = sum(x_m_list)
    travel_distances_m = range(1, ceil(total_travel_dist_m))
    path_losses_db = []
    rain_attenuations_db = []

    for travel_dist_m in travel_distances_m:
        if travel_dist_m < x_m_list[0]:
            x1_m = travel_dist_m
            x2_m = 0
        else:
            x1_m = x_m_list[0]
            x2_m = travel_dist_m - x1_m

        # Calculate path loss L including atmospheric gases attenuation but not rain attenuation.
        L = p1411.site_specific_street_canyons_nlos_shf(
            f_ghz=freq_ghz,
            x1_m=x1_m, x2_m=x2_m, w1_m=tx_street_width_m,
            h1_m=tx_height_m, h2_m=rx_height_m,
            hs_m=0.7, # Effective road height (m), depends on the traffic on the road (see ITU-R
                      # P.1411-13, TABLE 5 and 6). May not be used depending on frequency.
            n=2.1, # Basic transmission loss exponent (see ITU-R P.1411-13, TABLE 7).
            env=p1411.EnvironmentC.URBAN,
            bldg_layout=p1411.BuildingsLayout.WEDGE_SHAPED
        )
        path_losses_db.append(L)

        # Caluculate rain attenuation exceeded for p% of the time.
        p = 0.1 # Time percentage (%) (yearly stats), valid values from 0.001 to 1.
        Ap = p530.rain_attenuation_long_term_stats(
            f_ghz=freq_ghz,
            d_km=travel_dist_m/1000,
            p_percent=p,
            theta_deg=0, # path elev angle, may be approx. to 0 for most terr. paths
            tau_deg=90, # polarization tilt angle relative to the horizontal
            lat=tx_lat, lon=tx_lon # location for getting rainfall rate stats,
                                   # use either tx or rx location for short paths
        )
        rain_attenuations_db.append(Ap)

    # Plot results
    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    max_dist_m = int(travel_distances_m[-1])
    ax1.set_xlim((0, max_dist_m))
    ax1.set_xticks([*range(0, max_dist_m+1, 50)])
    ax1.set_ylim((160, 60))
    ax1.set_yticks([*range(60, 160+1, 20)])
    ax1.plot(travel_distances_m, path_losses_db, color='#008DD2', label=f'{freq_ghz:.1f} GHz')
    ax1.plot(travel_distances_m, [sum(x) for x in zip(path_losses_db, rain_attenuations_db)],
             color='#E31E24',
             label=f'{freq_ghz:.1f} GHz with rain attenuation\nexceeded for {p}% of the time')
    ax1.set_title('ITU-R P.1411-13, site specific model for propagation within street canyons' \
                  ' (NLoS)')
    ax1.set_xlabel('Path length (m)')
    ax1.set_ylabel('Path loss (dB)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()
