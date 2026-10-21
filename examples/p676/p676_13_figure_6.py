# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 6 from ITU-R P.676-13."""

import matplotlib.pyplot as plt
import numpy as np
from propakai import p676_13 as p676


def figure_6() -> None:
    """Calculates values and display FIGURE 6 from ITU-R P.676-13."""
    freqs = []
    disps = []
    for f_ghz in np.arange(0, 100.01, 0.5):
        freqs.append(f_ghz)
        disps.append(p676.phase_dispersion(f_ghz=f_ghz, p_hpa=1013.25, t_k=15+273.15, rho_gm3=7.5))

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_xlim((0,100))
    ax1.set_xticks([*range(0, 100+1, 5)])
    ax1.set_ylim((-100, 100))
    ax1.set_yticks([*range(-100, 100+1, 10)])
    ax1.plot(freqs, disps, color='#000000')
    ax1.set_title('FIGURE 6\nThe frequency dependent specific phase dispersion for a standard ' \
                  'atmosphere\n(p = 1 013.25 hPa, rho = 7.5 g/m$^3$, T = 15$^o$C)')
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('Frequency dependent specific phase dispersion (deg/km)')
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_6()
