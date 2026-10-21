# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 1 from ITU-R P.676-13."""

import matplotlib.pyplot as plt
from propakai import p676_13 as p676


def figure_1() -> None:
    """Calculates values and display FIGURE 1 from ITU-R P.676-13."""
    freqs = []
    atts = [[],[]]
    for f_ghz in range(1, 1001, 1):
        freqs.append(f_ghz)
        atts[0].append(p676.gaseous_attenuation(f_ghz, 1013.25, 288.15, 7.5))
        atts[1].append(p676.gaseous_attenuation(f_ghz, 1013.25, 288.15, 0))

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_yscale('log')
    ax1.set_xlim((0,1000))
    ax1.set_xticks([*range(0, 1000+1, 100)])
    ax1.set_ylim((1E-3, 1E5))
    ax1.set_yticks([1E-3,1E-2,1E-1,1,1E1,1E2,1E3,1E4,1E5])
    ax1.plot(freqs, atts[0], color='#FF0000', label='standard')
    ax1.plot(freqs, atts[1], color='#0000FF', label='dry')
    ax1.set_title('FIGURE 1\nSpecific attenuation due to atmospheric gases, calculated at 1 GHz ' \
                   'intervals, including line centres')
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('Specific attenuation (dB/km)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_1()
