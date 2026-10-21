# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 4 from ITU-R P.530-18."""

import matplotlib.pyplot as plt
import numpy as np
from propakai import p530_18 as p530


def figure_4() -> None:
    """Calculates values and display FIGURE 4 from ITU-R P.530-18."""
    p0_list = [0.01, 0.0316, 0.1, 0.316, 1, 3.16, 10, 31.6, 100, 316, 1000]
    pw_list_per_p0 = []
    E_list = np.arange(0, 20.01, 0.2)
    for i, p0 in enumerate(p0_list):
        pw_list_per_p0.append([])
        for E in E_list:
            pw = p530._enhancement_distribution(E, p0, 0, 0, 0, 0, p530.TimePeriod.AVG_WORST_MONTH)
            pw_list_per_p0[i].append(100.0-pw)
    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_xlim((0,20))
    ax1.set_xticks([*range(0, 20+1, 2)])
    ax1.set_yscale('log')
    ax1.set_ylim((1E-4, 1E2))
    ax1.set_yticks([1E-4,1E-3,1E-2,1E-1,1,1E1,1E2])
    ax1.minorticks_off()
    for i, p0 in enumerate(p0_list):
        ax1.plot(E_list, pw_list_per_p0[i], color='#000000')
        mid_pt_Index = int(len(E_list)/2)
        plt.text(E_list[mid_pt_Index], pw_list_per_p0[i][mid_pt_Index], f'{p0}')
    ax1.set_title('FIGURE 4\nPercentage of time, (100-pw), enhancement, E, exceeded in the  ' \
                  'average worst month,\nwith p0 (in equation (11)) ranging from 0.01 to 1 000')
    ax1.set_xlabel('Enhancement (dB)')
    ax1.set_ylabel('Percentage of time abscissa is exceeded')
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_4()
