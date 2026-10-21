# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 4 from ITU-R P.681-11."""

import matplotlib.pyplot as plt
from propakai import p681_11 as p681


def figure_4() -> None:
    """Calculates values and display FIGURE 4 from ITU-R P.681-11."""
    f_ghz = 1.6
    hb = 15
    hm = 1.5
    dm = 17.5
    phis = [45, 90]
    cfs = [0, 0.7]
    probabilities = [[],[],[],[]]
    thetas = [*range(0, 80+1, 1)]
    index = 0
    for phi in phis:
        for cf in cfs:
            for theta in thetas:
                p = p681.building_blockage_probability(f_ghz, cf, theta, hm, dm, hb, phi)
                probabilities[index].append(p)
            index +=1
    fig, ax1 = plt.subplots()
    fig.set_size_inches(8, 6.75)
    ax1.set_xlim((0, 80))
    ax1.set_xticks([*range(0, 80+1, 10)])
    ax1.set_ylim((0, 100))
    ax1.set_yticks([*range(0, 100+1, 20)])
    ax1.plot(thetas, probabilities[0], color='#000000', linestyle='solid',
             label='φ=45°, C$_f$=0')
    ax1.plot(thetas, probabilities[1], color='#000000', linestyle='dashed',
             label='φ=45°, C$_f$=0.7')
    ax1.plot(thetas, probabilities[2], color='#0000AA', linestyle='solid',
             label='φ=90°, C$_f$=0')
    ax1.plot(thetas, probabilities[3], color='#0000AA', linestyle='dashed',
             label='φ=90°, C$_f$=0.7')
    ax1.set_title('FIGURE 4\nExamples of roadside building shadowing\n'\
                  '(f=1.6GHz, h$_b$=15m, h$_m$=1.5m, d$_m$=17.5m')
    ax1.set_xlabel('Path elevation angle (degrees)')
    ax1.legend()
    ax1.set_ylabel('Fade exceeded (dB)')
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_4()
