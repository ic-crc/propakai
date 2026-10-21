# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 1 from ITU-R P.681-11."""

import matplotlib.pyplot as plt
from propakai import p681_11 as p681


def figure_1() -> None:
    """Calculates values and display FIGURE 1 from ITU-R P.681-11."""
    f_ghz = 1.5
    percents = [1,2,5,10,20,30,50]
    fades = [[],[],[],[],[],[],[]]
    thetas = [*range(10, 60+1, 1)]
    for index, p in enumerate(percents):
        for theta_deg in thetas:
            fade = p681.roadside_trees_shadowing_fade(f_ghz, theta_deg, p)
            fades[index].append(fade)
    fig, ax1 = plt.subplots()
    fig.set_size_inches(8, 6.75)
    ax1.set_xlim((10, 60))
    ax1.set_xticks([*range(10, 60+1, 5)])
    ax1.set_ylim((0, 30))
    ax1.set_yticks([*range(0, 30+1, 2)])
    for i, p in enumerate(percents):
        if i%2 == 0:
            linestyle = 'solid'
        else:
            linestyle = 'dotted'
        ax1.plot(thetas, fades[i], color='#000000', linestyle=linestyle)
        pt_index = int(len(thetas)*0.16)
        plt.text(thetas[pt_index], fades[i][pt_index], f'{p}%')
    ax1.set_title('FIGURE 1\nFading at 1.5 GHz due to roadside shadowing versus path elevation '\
                  'angle')
    ax1.set_xlabel('Path elevation angle (degrees)')
    ax1.set_ylabel('Fade exceeded (dB)')
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_1()
