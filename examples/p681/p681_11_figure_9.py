# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 9 from ITU-R P.681-11."""

import matplotlib.pyplot as plt
import numpy as np
from propakai import p681_11 as p681


def figure_9() -> None:
    """Calculates values and display FIGURE 9 from ITU-R P.681-11."""
    freqs = [0.87, 1.5]
    thetas = [45, 30]
    fade_depths = [*np.arange(2, 8+0.01, 0.1)]
    probs = [[],[],[],[]]
    i=0
    for theta_deg in thetas:
        for f_ghz in freqs:
            for fade_depth in fade_depths:
                p = p681.mountainous_multipath_fading_distribution(f_ghz, theta_deg, fade_depth,
                                                                   False)
                probs[i].append(p)
            i += 1
    fig, ax1 = plt.subplots()
    fig.set_size_inches(6.75, 8)
    ax1.set_xlim((0, 10))
    ax1.set_xticks([*range(0, 10+1, 1)])
    ax1.set_ylim((1, 20))
    ax1.set_yscale('log')
    y_ticks = [*range(1, 10+1, 1), 20]
    ax1.set_yticks(y_ticks)
    y_tick_labels = [str(n) for n in y_ticks]
    ax1.set_yticklabels(y_tick_labels)
    ax1.plot(fade_depths, probs[0], color='#000000', linestyle='solid', label='A: 870 MHz, 45°')
    ax1.plot(fade_depths, probs[1], color='#FF0000', linestyle='solid', label='B: 1.5 GHz, 45°')
    ax1.plot(fade_depths, probs[2], color='#00FF00', linestyle='solid', label='C: 870 MHz, 30°')
    ax1.plot(fade_depths, probs[3], color='#0000FF', linestyle='solid', label='D: 1.5 GHz, 30°')
    ax1.set_title('FIGURE 9\nBest fit cumulative fade distributions for multipath fading in\n'\
                  'mountainous terrain')
    ax1.set_xlabel('Fade depth (dB)')
    ax1.set_ylabel('Percentage of distance fade > abscissa')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_9()
