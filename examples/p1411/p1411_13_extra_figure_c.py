# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Site-specific near street level (urban area) figure (ITU-R P.1411-13). This figure is not part of
the recommendation.
"""

import matplotlib.pyplot as plt
from propakai import p1411_13 as p1411


def extra_figure_c() -> None:
    """
    Site-specific near street level (urban area) figure (ITU-R P.1411-13). This figure is not part
    of the recommendation.
    """
    x1 = 300 # Distance between Station 1 and the first street corner (m), with 0 < x1_m.
    x2 = 200 # Distance between the first street corner and the second street corner (m),
             # with 0 <= x2_m.
    x3 = 100 # Distance between the second street corner and Station 2 (m), with 0 <= x3_m.
    h1 = 3.5 # Station 1 antenna height (m), with 1.5 <= h1_m <= 4.
    h2 = 1.5 # Station 2 antenna height (m), with 1.5 <= h2_m <= 4.
    hs = 0.75 # Effective road height (m), with 0 <= hs_m.
    max_dist = x1+x2+x3
    dists = []
    freqs = [0.5,1,2,3,4] # Operating frequency (GHz), with 0.430 <= f_GHz <= 4.860.
    losses = [[],[],[],[],[]]
    for d_m in range(1, max_dist+1, 1):
        dists.append(d_m)
        if d_m <= x1:
            x1_temp = d_m
            x2_temp = 0
            x3_temp = 0
        elif d_m <= x1+x2:
            x1_temp = x1
            x2_temp = d_m - x1
            x3_temp = 0
        else:
            x1_temp = x1
            x2_temp = x2
            x3_temp = d_m - x1 - x2
        for i, f_ghz in enumerate(freqs):
            L = p1411.site_specific_near_street_level_urban(f_ghz=f_ghz, x1_m=x1_temp,
                    x2_m=x2_temp, x3_m=x3_temp, h1_m=h1, h2_m=h2, hs_m=hs)
            losses[i].append(L)

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_xlim((0, max_dist))
    ax1.set_xticks([*range(0, max_dist+1, 50)])
    ax1.set_ylim((160, 40))
    ax1.set_yticks([*range(40, 160+1, 20)])
    ax1.plot(dists, losses[0], color='#008DD2', label='0.5 GHz')
    ax1.plot(dists, losses[1], color='#E31E24', label='1 GHz')
    ax1.plot(dists, losses[2], color='#1D8545', label='2 GHz')
    ax1.plot(dists, losses[3], color='#B73B7B', label='3 GHz')
    ax1.plot(dists, losses[4], color='#A5CFE0', label='4 GHz')
    ax1.set_title('EXTRA FIGURE C\nSite-specific near street level (urban area)')
    ax1.set_xlabel('Road distance (m)')
    ax1.set_ylabel('Basic transmission loss (dB)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    extra_figure_c()
