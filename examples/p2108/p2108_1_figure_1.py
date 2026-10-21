# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 1 from ITU-R P.2108-1."""

import matplotlib.pyplot as plt
import numpy as np
from propakai import p2108_1 as p2108


def figure_1() -> None:
    """Calculates values and display FIGURE 1 from ITU-R P.2108-1."""
    dists = [*np.arange(0.25, 2+0.01, 0.05), *range(2, 10+1, 1), *range(10, 100+1, 1)]
    freqs = [1,2,4,8,16,32,67]
    losses = [[],[],[],[],[],[],[]]
    for d_km in dists:
        for i, f_ghz in enumerate(freqs):
            losses[i].append(p2108.terrestrial_path_clutter_loss(f_ghz, d_km, 50))

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_xscale('log')
    ax1.set_xlim((0,100))
    ax1.set_xticks([0.1,1,10,100])
    ax1.set_ylim((15, 35))
    ax1.set_yticks([15,20,25,30,35])
    ax1.plot(dists, losses[0], color='#2020EC', label='1 GHz')
    ax1.plot(dists, losses[1], color='#FF8000', label='2 GHz')
    ax1.plot(dists, losses[2], color='#FFDE00', label='4 GHz')
    ax1.plot(dists, losses[3], color='#8000FF', label='8 GHz')
    ax1.plot(dists, losses[4], color='#427010', label='16 GHz')
    ax1.plot(dists, losses[5], color='#00FFFF', label='32 GHz')
    ax1.plot(dists, losses[6], color='#A00000', label='67 GHz')
    ax1.set_title('FIGURE 1\nMedian clutter loss for terrestrial paths')
    ax1.set_xlabel('Distance (km)')
    ax1.set_ylabel('Median clutter loss (dB)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_1()
