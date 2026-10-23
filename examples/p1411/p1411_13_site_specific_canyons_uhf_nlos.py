# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Calculates path loss for a single reception point according to equations from Section 4.1.3.1 of
ITU-R P.1411-13 (see also FIGURE 3 from Section 3.1.2). Distances to and from the street corner and
the street corner angle are computed using OpenStreetMap data.
"""

from os.path import dirname, abspath, join
from math import radians
from propakai import p1411_13 as p1411
from propakai.extras import streets


if __name__ == '__main__':
    print('\nITU-R P.1411-13, site specific model for propagation within ' \
          'street canyons (NLoS) in the 0.8 to 2.0 GHz band')

    freq_ghz = 1.5
    tx_lat = 43.659072
    tx_lon = -79.382108
    rx_lat = 43.6613634
    rx_lon = -79.3818735
    tx_street_width_m = 27.0
    rx_street_width_m = 27.0

    # Download OpenStreetMap data and get a street graph for the area surrounding the transmitter
    # and receiver locations.
    print('Getting street data...', end='', flush=True)
    street_graph = streets.StreetGraph(bounds=[(tx_lat, tx_lon), (rx_lat, rx_lon)])
    print('done', flush=True)

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
    thrsh = 45 # minimum turn-angle on a path to consider it as a "street corner"
    selected_path = streets.sort_by_street_corner_turns(radio_paths=radio_paths,
                                                        turn_angle_threshold_deg=thrsh)[0]

    # If desired, a path may be exported to a geojson file and visualized using a GIS application.
    script_dir = dirname(abspath(__file__))
    selected_path.to_geojson_file(join(script_dir, 'radio_path.geojson'))

    distances_m = selected_path.distances_to_street_corners(turn_angle_threshold_deg=thrsh)
    angles_deg = selected_path.street_corner_angles(turn_angle_threshold_deg=thrsh)

    if len(angles_deg) == 1: # Check that the selected path only has one turn at street crossings.

        # Compute path loss
        L = p1411.site_specific_street_canyons_nlos_uhf(
            f_ghz=freq_ghz,
            x1_m=distances_m[0],
            x2_m=distances_m[1],
            w1_m=tx_street_width_m,
            w2_m=rx_street_width_m,
            alpha_rad=radians(angles_deg[0])
        )

        print(f'Distance from station 1 to street crossing, x1 (m): {distances_m[0]:.1f}')
        print(f'Distance from street crossing to station 2, x2 (m): {distances_m[1]:.1f}')
        print(f'Total travel distance (m): {sum(distances_m):.1f}')
        print(f'Street corner angle, alpha (rad): {radians(angles_deg[0]):.2f} ' \
              f'({angles_deg[0]:.2f} deg)')
        print(f'Path loss (dB): {L:.1f}\n')
