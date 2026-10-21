# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 2 from ITU-R P.676-13."""

import matplotlib.pyplot as plt
import numpy as np
from propakai import p676_13 as p676
from propakai import p835_6 as p835


def figure_2() -> None:
    """Calculates values and display FIGURE 2 from ITU-R P.676-13."""
    freqs = []
    dists = [0,5,10,15,20]
    atts = [[],[],[],[],[]]
    for f_ghz in np.arange(50, 70+0.005, 0.01):
        freqs.append(f_ghz)
        for i in range(0, 5, 1):
            d_km = dists[i]
            atts[i].append(p676.gaseous_attenuation(f_ghz, p835.pressure(d_km),
                                                    p835.temperature(d_km),
                                                    p835.water_vapour_density(d_km)))

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_yscale('log')
    ax1.set_xlim((50,70))
    ax1.set_xticks([*range(50, 70+1, 2)])
    ax1.set_ylim((1E-3, 1E2))
    ax1.set_yticks([1E-3,1E-2,1E-1,1,1E1,1E2])
    ax1.plot(freqs, atts[0], color='#FF0000', label='0 km')
    ax1.plot(freqs, atts[1], color='#0000FF', label='5 km')
    ax1.plot(freqs, atts[2], color='#22814C', label='10 km')
    ax1.plot(freqs, atts[3], color='#8000FF', label='15 km')
    ax1.plot(freqs, atts[4], color='#00A0E3', label='20 km')
    ax1.set_title('FIGURE 2\nSpecific attenuation in the range 50-70 GHz at the altitudes ' \
                  'indicated, calculated at intervals of 10 MHz,\nincluding line centres ' \
                  '(0 km, 5 km, 10 km, 15 km and 20 km)')
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('Specific attenuation (dB/km)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_2()
