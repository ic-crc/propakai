# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 1 from ITU-R P.2109-2."""

import matplotlib.pyplot as plt
import numpy as np
from propakai import p2109_2 as p2109


def figure_1() -> None:
    """Calculates values and display FIGURE 1 from ITU-R P.2109-2."""
    freqs = [*np.arange(0.1, 1+0.01, 0.05), *np.arange(1, 10+0.1, 0.5), *np.arange(10, 100+0.1, 5)]
    losses = [[],[]]
    TRAD = p2109.BuildingType.TRADITIONAL
    EFF = p2109.BuildingType.THERMALLY_EFFICIENT
    for f_ghz in freqs:
        losses[0].append(p2109.building_entry_loss(f_ghz, 0, 50, TRAD))
        losses[1].append(p2109.building_entry_loss(f_ghz, 0, 50, EFF))

    fig, ax1 = plt.subplots()
    fig.set_size_inches(8, 6.75)
    ax1.set_xscale('log')
    ax1.set_xlim((0.1,100))
    ax1.set_xticks([0.1,1,10,100])
    ax1.set_ylim((10, 60))
    ax1.set_yticks([*range(10, 60+1, 5)])
    ax1.plot(freqs, losses[0], color='#000000', label='Traditional')
    ax1.plot(freqs, losses[1], color='#FF0000', label='Thermally-efficient')
    ax1.set_title('FIGURE 1\nMedian building entry loss predicted at horizontal incidence')
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('L$^{omni}_{BEL}$ (dB)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_1()
