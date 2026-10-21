# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 4 from ITU-R P.1411-13."""

import matplotlib.pyplot as plt
from propakai import p1411_13 as p1411


def figure_4() -> None:
    """Calculates values and display FIGURE 4 from ITU-R P.1411-13."""
    h1 = 5.0 # Station 1 antenna height (m)
    h2 = 1.5 # Station 2 antenna height (m)
    x1 = 200 #  Distance Station 1 to street crossing (m)
    x2 = 400 # Distance Station 2 to street crossing (m)
    w1 = 10.0 # Street width at the position of the Station 1 (m)
    env = p1411.EnvironmentC.URBAN
    bldg_layout = p1411.BuildingsLayout.WEDGE_SHAPED
    hs = 0.75 #  Effective road height (m)
    n = 2.05 # Basic transmission loss exponent
    dists = []
    freqs = [2,5,10,20,30]
    losses = [[],[],[],[],[]]
    for d_m in range(1, x1+x2+1, 1):
        dists.append(d_m)
        for i, f_ghz in enumerate(freqs):
            if d_m <= x1:
                x1_temp = d_m
                x2_temp = 0.0
            else:
                x1_temp = x1
                x2_temp = d_m-x1
            L_NLoS2 = p1411.site_specific_street_canyons_nlos_shf(f_ghz=f_ghz, x1_m=x1_temp,
                          x2_m=x2_temp, w1_m=w1, h1_m=h1, h2_m=h2, hs_m=hs, n=n, env=env,
                          bldg_layout=bldg_layout)
            losses[i].append(L_NLoS2)

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_xlim((0,x1+x2))
    ax1.set_xticks([*range(0, x1+x2+1, 50)])
    ax1.set_ylim((160,40))
    ax1.set_yticks([*range(40, 160+1, 20)])
    ax1.plot(dists, losses[0], color='#008DD2', label='2 GHz')
    ax1.plot(dists, losses[1], color='#E31E24', label='5 GHz')
    ax1.plot(dists, losses[2], color='#1D8545', label='10 GHz')
    ax1.plot(dists, losses[3], color='#B73B7B', label='20 GHz')
    ax1.plot(dists, losses[4], color='#A5CFE0', label='30 GHz')
    ax1.set_title('FIGURE 4\nTypical trend of propagation along street canyons with low station ' \
                  'height\nfor frequency range from 2 to 38 GHz')
    ax1.set_xlabel('Distance of travel from station 1 (m)')
    ax1.set_ylabel('Basic transmission loss (dB)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_4()
