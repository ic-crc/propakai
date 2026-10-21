# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 6 from ITU-R P.1411-13."""

import matplotlib.pyplot as plt
from propakai import p1411_13 as p1411


def figure_6() -> None:
    """Calculates values and display FIGURE 6 from ITU-R P.1411-13."""
    f_ghz = 0.400
    dists = []
    loc_percents = [1,10,50,90,99]
    losses = [[],[],[],[],[]]
    for d_m in range(1, 2000+1, 1):
        dists.append(d_m)
        for i, p in enumerate(loc_percents):
            L, _ = p1411.site_general_near_street_level(f_ghz, d_m, p, p1411.EnvironmentB.SUBURBAN)
            losses[i].append(L)

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_xlim((0,2000))
    ax1.set_xticks([*range(0, 2000+1, 200)])
    ax1.set_ylim((160,0))
    ax1.set_yticks([*range(0, 160+1, 20)])
    ax1.plot(dists, losses[0], color='#008DD2', label='1%')
    ax1.plot(dists, losses[1], color='#E31E24', label='10%')
    ax1.plot(dists, losses[2], color='#1D8545', label='50%')
    ax1.plot(dists, losses[3], color='#B73B7B', label='90%')
    ax1.plot(dists, losses[4], color='#A5CFE0', label='99%')
    ax1.set_title('FIGURE 6\nCurves of basic transmission loss not exceeded for 1, 10, 50, 90 ' \
                  'and 99% of locations\n(frequency = 400 MHz, suburban)')
    ax1.set_xlabel('Distance (m)')
    ax1.set_ylabel('Basic transmission loss (dB)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_6()
