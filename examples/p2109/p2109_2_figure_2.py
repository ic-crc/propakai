# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 2 from ITU-R P.2109-2."""

import matplotlib.pyplot as plt
import numpy as np
from propakai import p2109_2 as p2109


def figure_2() -> None:
    """Calculates values and display FIGURE 2 from ITU-R P.2109-2."""
    freqs = [0.1, 1, 10, 100]
    probs = [*np.arange(0.001, 1, 0.001)]
    losses = [[],[],[],[],[],[],[],[]]
    TRAD = p2109.BuildingType.TRADITIONAL
    EFF = p2109.BuildingType.THERMALLY_EFFICIENT
    for i, f_ghz in enumerate(freqs):
        for p in probs:
            losses[i*2].append(p2109.building_entry_loss(f_ghz, 0, p*100, TRAD))
            losses[(i*2)+1].append(p2109.building_entry_loss(f_ghz, 0, p*100, EFF))

    fig, ax1 = plt.subplots()
    fig.set_size_inches(9, 6.75)
    ax1.set_xlim((-20, 140))
    ax1.set_xticks([*range(-20, 140+1, 20)])
    ax1.set_ylim((0, 1))
    ax1.set_yticks([*np.arange(0, 1+0.01, 0.1)])
    ax1.plot(losses[0], probs, color='#000000', linestyle='dashed',
             label='0.1 GHz, Traditional')
    ax1.plot(losses[1], probs, color='#000000', linestyle='dotted',
             label='0.1 GHz, Thermally-efficient')
    ax1.plot(losses[2], probs, color='#FF0000', linestyle='dashed',
             label='  1 GHz, Traditional')
    ax1.plot(losses[3], probs, color='#FF0000', linestyle='dotted',
             label='  1 GHz, Thermally-efficient')
    ax1.plot(losses[4], probs, color='#00FF00', linestyle='dashed',
             label=' 10 GHz, Traditional')
    ax1.plot(losses[5], probs, color='#00FF00', linestyle='dotted',
             label=' 10 GHz, Thermally-efficient')
    ax1.plot(losses[6], probs, color='#0000FF', linestyle='dashed',
             label='100 GHz, Traditional')
    ax1.plot(losses[7], probs, color='#0000FF', linestyle='dotted',
             label='100 GHz, Thermally-efficient')
    ax1.set_title('FIGURE 2\nBuilding entry loss predicted at horizontal incidence')
    ax1.set_xlabel('L$^{omni}_{BEL}$ (dB)')
    ax1.set_ylabel('Probability')
    ax1.legend()
    plt.legend(prop={'family': 'monospace', 'size': 10})
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_2()
