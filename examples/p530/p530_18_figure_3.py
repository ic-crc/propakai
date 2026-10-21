# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 3 from ITU-R P.530-18."""

import matplotlib.pyplot as plt
import numpy as np
from propakai import p530_18 as p530


def figure_3() -> None:
    """Calculates values and display FIGURE 3 from ITU-R P.530-18."""
    p0_list = [0.01, 0.0316, 0.1, 0.316, 1, 3.16, 10, 31.6, 100, 316, 1000]
    pw_list_per_p0 = []
    A_list = np.arange(0, 50.01, 0.5)
    for i, p0 in enumerate(p0_list):
        pw_list_per_p0.append([])
        for A in A_list:
            pw = p530._fade_depth_distribution(A, p0, 0, 0, 0, 0, p530.TimePeriod.AVG_WORST_MONTH)
            pw_list_per_p0[i].append(pw)
    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 8)
    ax1.set_xlim((0,50))
    ax1.set_xticks([*range(0, 50+1, 5)])
    ax1.set_yscale('log')
    ax1.set_ylim((1E-5, 1E2))
    ax1.set_yticks([1E-5,1E-4,1E-3,1E-2,1E-1,1,1E1,1E2])
    ax1.minorticks_off()
    for i, p0 in enumerate(p0_list):
        ax1.plot(A_list, pw_list_per_p0[i], color='#000000')
        mid_pt_index = int(len(A_list)/2)
        plt.text(A_list[mid_pt_index], pw_list_per_p0[i][mid_pt_index], f'{p0}')
    ax1.set_title('FIGURE 3\nPercentage of time, pw, fade depth, A, exceeded in average worst ' \
                  'month,\nwith p0 (in equation (11))\nranging from 0.01 to 1 000')
    ax1.set_xlabel('Fade depth, A (dB)')
    ax1.set_ylabel('Percentage of time abscissa is exceeded')
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_3()
