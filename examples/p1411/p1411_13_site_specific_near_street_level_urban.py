# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates path loss according to Section 4.3.2 of ITU-R P.1411-13"""

from os.path import dirname, abspath, join
from math import log10
from propakai import p1411_13 as p1411
from propakai.extras import streets


if __name__ == '__main__':
    print('\nITU-R P.1411-13, site specific model for propagation between terminals located' \
          ' from below roof-top height to near street level in an urban environment\n')

    freq_ghz = 3.5
    tx_height_m = 4.0
    rx_height_m = 1.5
    tx_lat = 45.4189209
    tx_lon = -75.6994100
    hs_m = 0.75 # Effective road height (m), see ITU-R P.1411-13 TABLE 5 and TABLE 6
    rx_locations = [(45.4202813,-75.7005318), (45.4213236,-75.6971346), (45.4205041,-75.6980416)]
    script_dir = dirname(abspath(__file__))

    # Download OpenStreetMap data and get a street graph for the area surrounding the transmitter
    # and receiver locations.
    street_graph = streets.StreetGraph(bounds=rx_locations + [(tx_lat, tx_lon)])

    # If desired, the street graph may be displayed.
    street_graph.display()

    for rx_location in rx_locations:
        rx_lat = rx_location[0]
        rx_lon = rx_location[1]

        # GetStreetCanyonsRadioPaths() computes one or more paths following street lines based on a
        # shortest travel distance algorithm. The shortest path is often but not always the path
        # having the lowest number of turns at street crossings, so we will ask for a few different
        # paths to be returned and then select one with the lowest amount of turns at street
        # crossings (usually preferable propagation-wise).
        radio_paths = streets.compute_street_canyon_radio_paths(graph=street_graph,
                                                                latt=tx_lat, lont=tx_lon,
                                                                latr=rx_lat, lonr=rx_lon,
                                                                num_paths=4)

        # We can have the paths simplified before the sort takes place. This is ususally helpful as
        # it removes very small street sections that unnecessarily complexifies the path.
        radio_paths = [rp.new_simplified() for rp in radio_paths]

        # Sort paths in ascending order of turns at street crossings.
        radio_paths = streets.sort_by_street_corner_turns(radio_paths)

        # Get the recommendation's x1, x2 (if applicable) and x3 (if applicable) values using the
        # first path in the sorted list of paths.
        x_list = radio_paths[0].distances_to_street_corners()

        if len(x_list) == 1:
            print('LoS situation')
            L_dB = p1411.site_specific_near_street_level_urban(
                f_ghz=freq_ghz,
                x1_m=x_list[0], x2_m=0, x3_m=0,
                h1_m=tx_height_m, h2_m=rx_height_m,
                hs_m=hs_m
            )
            filepath = join(script_dir, 'LoS_radio_path.geojson')
            radio_paths[0].to_geojson_file(filepath)
            print(f'  path loss = {L_dB:.1f} dB\n')

        elif len(x_list) == 2:
            print('1-Turn NLoS situation')
            L_dB = p1411.site_specific_near_street_level_urban(
                f_ghz=freq_ghz,
                x1_m=x_list[0], x2_m=x_list[1], x3_m=0,
                h1_m=tx_height_m, h2_m=rx_height_m,
                hs_m=hs_m
            )
            filepath = join(script_dir, '1-turn_NLoS_radio_path.geojson')
            radio_paths[0].to_geojson_file(filepath)
            print(f'  path loss = {L_dB:.1f} dB\n')

        elif len(x_list) == 3:
            print('2-Turn NLoS situation')

            # Compute the path loss for different route paths and get the overall loss using
            # equation (68) from ITU-R P.1411-13.
            i = 0
            summing = 0
            while len(x_list) == 3:
                Li_dB = p1411.site_specific_near_street_level_urban(
                    f_ghz=freq_ghz,
                    x1_m=x_list[0], x2_m=x_list[1], x3_m=x_list[2],
                    h1_m=tx_height_m, h2_m=rx_height_m,
                    hs_m=hs_m
                )
                summing += 1.0/pow(10.0, Li_dB/10.0)
                filepath = join(script_dir, f'2-turn_NLoS_radio_path_{i}.geojson')
                radio_paths[i].to_geojson_file(filepath)
                print(f'  radio path [{i}]: travel distance = {sum(x_list):.1f} m, ' \
                      f'path loss = {Li_dB:.1f} dB')
                i += 1
                if len(radio_paths) > i:
                    x_list = radio_paths[i].distances_to_street_corners()
                else:
                    break
            L_dB = -10.0*log10(summing)
            print(f'  overall path loss = {L_dB:.1f} dB\n')

        else:
            print('No path with 2 turns or less found.\n')
