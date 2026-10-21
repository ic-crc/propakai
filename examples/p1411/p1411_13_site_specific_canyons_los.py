# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates path loss according to Section 4.1.2 of ITU-R P.1411-13."""

import matplotlib.pyplot as plt
from propakai import p1411_13 as p1411
from propakai import p530_18 as p530
from propakai.extras import topography as topo


if __name__ == '__main__':
    print('\nITU-R P.1411-13, site specific models for propagation within street canyons (LoS)')

    tx_lat = 45.416904
    tx_lon = -75.705472
    tx_height_m = 4.0
    rx_lat = 45.421069
    rx_lon = -75.695849
    rx_height_m = 1.5
    freqs_ghz = [1.5, 9.0, 28.0]
    p = 0.0
    path_losses_db = [[],[],[]]  # one list of path losses over distance for each frequency
    rain_att_db = [] # rain attenuation over distance

    sampling_res_m = 1.0 # sampling resolution, in meters
    dist_profile_m = topo.distance_profile_m(tx_lat, tx_lon, rx_lat, rx_lon, sampling_res_m)
    dist_profile_m = dist_profile_m[1:] # remove first element (i.e. distance of 0 m)

    for dist_m in dist_profile_m:
        for fi, f_ghz in enumerate(freqs_ghz):
            if f_ghz <= 3.0:
                L, _, _ = p1411.site_specific_street_canyons_los_uhf(
                            f_ghz=f_ghz, d_m=dist_m,h1_m=tx_height_m, h2_m=rx_height_m)
            elif f_ghz <= 10.0:
                hs_m = 0.7 # effective road height (m), depends on the traffic on the road
                           # (see ITU-R P.1411-13, TABLE 5 and 6)
                L, _, _ = p1411.site_specific_street_canyons_los_shf(
                            f_ghz=f_ghz, d_m=dist_m, h1_m=tx_height_m, h2_m=rx_height_m, hs_m=hs_m)
            else:
                n = 2.1 # basic transmission loss exponent (see ITU-R P.1411-13, TABLE 7)

                # includes atmospheric gases attenuation but not rain attenuation
                L = p1411.site_specific_street_canyons_los_mmwave(f_ghz=f_ghz, d_m=dist_m, n=n)

                # Caluculate rain attenuation exceeded for p% of the time.
                p = 1.0 # time percentage (%) (yearly stats), valid values from 0.001 to 1
                Ap = p530.rain_attenuation_long_term_stats(
                         f_ghz=f_ghz,
                         d_km=dist_m/1000,
                         p_percent=p,
                         theta_deg=0, # path elev angle, may be approx. to 0 for most terr. paths
                         tau_deg=90, # polarization tilt angle relative to the horizontal
                         lat=tx_lat, lon=tx_lon) # location for getting rainfall rate stats,
                                                 # use either tx or rx location for short paths
                rain_att_db.append(Ap)

            path_losses_db[fi].append(L)

    # Plot results
    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    max_dist_m = int(dist_profile_m[-1])
    ax1.set_xlim((0, max_dist_m))
    ax1.set_xticks([*range(0, max_dist_m+1, 50)])
    ax1.set_ylim((140, 40))
    ax1.set_yticks([*range(40, 140+1, 20)])
    ax1.plot(dist_profile_m, path_losses_db[0], color='#008DD2', label=f'{freqs_ghz[0]:.1f} GHz')
    ax1.plot(dist_profile_m, path_losses_db[1], color='#E31E24', label=f'{freqs_ghz[1]:.1f} GHz')
    ax1.plot(dist_profile_m, path_losses_db[2], color='#1D8545', label=f'{freqs_ghz[2]:.1f} GHz')
    ax1.plot(dist_profile_m, [sum(x) for x in zip(path_losses_db[2], rain_att_db)], color='#B73B7B',
             label=f'{freqs_ghz[2]:.1f} GHz with rain attenuation\nexceeded for {p}% of the time')
    ax1.set_title('ITU-R P.1411-13, site specific models for propagation within street canyons ' \
                  '(LoS)')
    ax1.set_xlabel('Path length (m)')
    ax1.set_ylabel('Path loss (dB)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()
