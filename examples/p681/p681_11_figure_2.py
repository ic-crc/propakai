# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 2 from ITU-R P.681-11."""

import matplotlib.pyplot as plt
import numpy as np
from propakai import p681_11 as p681


def figure_2() -> None:
    """Calculates values and display FIGURE 2 from ITU-R P.681-11."""
    dists = [*np.arange(0.01, 0.1, 0.01), *np.arange(0.1, 1, 0.1), *np.arange(1, 10+1, 1)]
    probs = []
    for dd_m in dists:
        p = p681.fade_duration_distribution(dd_m)
        probs.append(p)
    fig, ax1 = plt.subplots()
    fig.set_size_inches(8, 6.75)
    ax1.set_xlim((0.02, 10))
    ax1.set_xscale('log')
    ax1.set_xticks(dists)
    ax1.set_ylim((1, 100))
    ax1.set_yscale('log')
    ax1.set_yticks([*range(1, 10, 1), *range(10, 100+1, 10)])
    ax1.plot(dists, probs, color='#000000', linestyle='solid')
    ax1.set_title('FIGURE 2\nBest fit cumulative fade distribution for roadside tree\n'\
                  'shadowing with a 5 dB threshold')
    ax1.set_xlabel('Fade duration (m)')
    ax1.set_ylabel('Percentage of fade duration > abscissa')
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_2()
