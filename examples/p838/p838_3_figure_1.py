# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 1 from ITU-R P.838-3."""

import matplotlib.pyplot as plt
import numpy as np
from propakai import p838_3 as p838


def figure_1() -> None:
    """Calculates values and display FIGURE 1 from ITU-R P.838-3."""
    freqs = [*np.arange(1, 10, 0.1), *np.arange(10, 100, 1), *np.arange(100, 1000+1, 5)]
    k_coeffs = []
    for f_ghz in freqs:
        k_coeffs.append(p838._kH(f_ghz))
    fig, ax1 = plt.subplots()
    fig.set_size_inches(9, 6.75)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlim((1, 1000))
    ax1.set_xticks([1, 10, 100, 1000])
    ax1.set_ylim((1E-5, 10))
    ax1.set_yticks([1E-5, 1E-4, 1E-3, 1E-2, 1E-1, 1, 10])
    ax1.plot(freqs, k_coeffs, color='#000000')
    ax1.set_title('FIGURE 1\nk coefficient for horizontal polarization')
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('Coefficient kH')
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_1()
