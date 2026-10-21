# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 8 from ITU-R P.676-13."""

import matplotlib.pyplot as plt
from propakai import p676_13 as p676


def figure_8() -> None:
    """Calculates values and display FIGURE 8 from ITU-R P.676-13."""
    freqs = []
    temperatures = []
    for f_ghz in range(1, 1000+1, 1):
        freqs.append(f_ghz)
        t_k = p676.downwelling_microwave_brightness_temperature(f_ghz, 90)
        temperatures.append(t_k)
        print(f'{f_ghz} GHz, {t_k:.3f} K')

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_xlim((0,1000))
    ax1.set_xticks([*range(0, 1000+1, 100)])
    ax1.set_ylim((0, 300))
    ax1.set_yticks([*range(0, 300+1, 25)])
    ax1.plot(freqs, temperatures, color='#000000')
    ax1.set_title('FIGURE 8\nZenith downwelling microwave brightness temperature for a\n' \
                  'standard atmosphere (1 GHz centres)')
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('Net downwelling microwave brightness temperature (K)')
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_8()
