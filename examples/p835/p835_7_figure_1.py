# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 1 from ITU-R P.835-7."""

import matplotlib.pyplot as plt
from propakai import p835_7 as p835


def figure_1() -> None:
    """Calculates values and display FIGURE 1 from ITU-R P.835-7."""
    goemetric_heights_km = range(0, 101, 1)
    temperatures_k = []
    for gh_km in goemetric_heights_km:
        t_k = p835.temperature(gh_km)
        temperatures_k.append(t_k)

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 8)
    ax1.set_xlim((180,300))
    ax1.set_xticks([*range(180, 300+1, 10)])
    ax1.set_ylim((0, 100))
    ax1.set_yticks([*range(0, 100+1, 10)])
    ax1.plot(temperatures_k, goemetric_heights_km, color="#20ABEC")
    ax1.set_title('FIGURE 1\nTemperature vs. geometric height')
    ax1.set_xlabel('Temperature (K)')
    ax1.set_ylabel('Geometric height (km)')
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_1()
