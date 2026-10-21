# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Site-specific over roof-tops (suburban area) figure (ITU-R P.1411-13). This figure is not part of
the recommendation.
"""

import matplotlib.pyplot as plt
from propakai import p1411_13 as p1411


def extra_figure_b() -> None:
    """
    Site-specific over roof-tops (suburban area) figure (ITU-R P.1411-13). This figure is not part
    of the recommendation.
    """
    hr = 10 # Average height of buildings (m).
    h1 = hr+40 # Station 1 antenna height (m), with hr_m+1 <= h1_m <= hr_m+100.
    h2 = hr-8.5 # Station 2 antenna height (m), with hr_m-10 <= h2_m <= hr_m-4.
    w = 10 # Street width (m) at station 2's location, with 10 <= w2_m <= 25.
    phi_deg = 90 # Street orientation with respect to the direct path (deg), with 0 <= phi_deg <= 90
    max_dist = 1000 # Path length (m), with 10 <= d_m <= 5000.
    dists = []
    freqs = [2,5,10,20,30] # Operating frequency (GHz), with 0.8 <= f_GHz <= 38.
    losses = [[],[],[],[],[]]
    for d_m in range(10, max_dist+1, 1):
        dists.append(d_m)
        for i, f_ghz in enumerate(freqs):
            L_NLoS1 = p1411.site_specific_over_rooftops_suburban(f_ghz=f_ghz, d_m=d_m, h1_m=h1,
                          h2_m=h2, hr_m=hr, w2_m=w, phi_deg=phi_deg)
            losses[i].append(L_NLoS1)

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_xlim((0, max_dist))
    ax1.set_xticks([*range(0, max_dist+1, 50)])
    ax1.set_ylim((160,40))
    ax1.set_yticks([*range(40, 160+1, 20)])
    ax1.plot(dists, losses[0], color='#008DD2', label='2 GHz')
    ax1.plot(dists, losses[1], color='#E31E24', label='5 GHz')
    ax1.plot(dists, losses[2], color='#1D8545', label='10 GHz')
    ax1.plot(dists, losses[3], color='#B73B7B', label='20 GHz')
    ax1.plot(dists, losses[4], color='#A5CFE0', label='30 GHz')
    ax1.set_title('EXTRA FIGURE B\nSite-specific over roof-tops (suburban area)')
    ax1.set_xlabel('Path length (m)')
    ax1.set_ylabel('Basic transmission loss (dB)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    extra_figure_b()
