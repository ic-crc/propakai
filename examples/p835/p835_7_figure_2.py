# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 2 from ITU-R P.835-7."""

import matplotlib.pyplot as plt
from propakai import p835_7 as p835


def figure_2() -> None:
    """Calculates values and display FIGURE 2 from ITU-R P.835-7."""
    goemetric_heights_km = range(0, 101, 1)
    pressures_hpa = []
    for gh_km in goemetric_heights_km:
        p_hpa = p835.pressure(gh_km)
        pressures_hpa.append(p_hpa)

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 8)
    ax1.set_xscale('log')
    ax1.set_xlim((1E-4, 1E3))
    ax1.set_xticks([1E-4,1E-3,1E-2,1E-1,1,1E1,1E2,1E3])
    ax1.set_ylim((0, 100))
    ax1.set_yticks([*range(0, 100+1, 10)])
    ax1.plot(pressures_hpa, goemetric_heights_km, color="#20ABEC")
    ax1.set_title('FIGURE 2\nTotal pressure vs. geometric height')
    ax1.set_xlabel('Total pressure (hPa)')
    ax1.set_ylabel('Geometric height (km)')
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_2()
