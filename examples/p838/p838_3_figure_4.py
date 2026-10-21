# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 4 from ITU-R P.838-3."""

import matplotlib.pyplot as plt
import numpy as np
from propakai import p838_3 as p838


def figure_4() -> None:
    """Calculates values and display FIGURE 4 from ITU-R P.838-3."""
    freqs = [*np.arange(1, 10, 0.1), *np.arange(10, 100, 1), *np.arange(100, 1000+1, 5)]
    alpha_coeffs = []
    for f_ghz in freqs:
        alpha_coeffs.append(p838._alphaV(f_ghz))
    fig, ax1 = plt.subplots()
    fig.set_size_inches(9, 6.75)
    ax1.set_xscale('log')
    ax1.set_xlim((1, 1000))
    ax1.set_xticks([1, 10, 100, 1000])
    ax1.set_ylim((0.4, 1.8))
    ax1.set_yticks([*np.arange(0.4, 1.8+0.001, 0.2)])
    ax1.plot(freqs, alpha_coeffs, color='#000000')
    ax1.set_title('FIGURE 4\nalpha coefficient for vertical polarization')
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('Coefficient alphaV')
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_4()
