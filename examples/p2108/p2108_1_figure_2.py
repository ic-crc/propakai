# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 2 from ITU-R P.2108-1."""

import matplotlib.pyplot as plt
from propakai import p2108_1 as p2108


def figure_2() -> None:
    """Calculates values and display FIGURE 2 from ITU-R P.2108-1."""
    thetas = [0,5,10,15,20,30,40,50,60,70,80,90]
    loc_percents = [0.1, *range(1, 100, 1), 99.9]
    losses = [[] for _ in range(len(thetas))]
    for i, theta in enumerate(thetas):
        for p in loc_percents:
            losses[i].append(p2108.earth_space_clutter_loss(30, theta, p))

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_xlim((-10,70))
    ax1.set_xticks([*range(-10,70+1,10)])
    ax1.set_ylim((0, 100))
    ax1.set_yticks([*range(0,100+1,10)])
    for i, theta in enumerate(thetas):
        ax1.plot(losses[i], loc_percents, label=f'{theta}°')
    ax1.set_title('FIGURE 2\nCumulative distribution of clutter loss not exceeded for 30 GHz')
    ax1.set_xlabel('Clutter loss (dB)')
    ax1.set_ylabel('Percent of locations')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_2()
