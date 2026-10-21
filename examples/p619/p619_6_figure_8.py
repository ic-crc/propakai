# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 8 from ITU-R P.619-6."""

import matplotlib.pyplot as plt
import numpy as np
from propakai import p619_6 as p619


def figure_8() -> None:
    """Calculates values and display FIGURE 8 from ITU-R P.619-6."""
    f_ghz = 30
    ga_dbi = 0
    nwet_ppm = 42.5
    fs_elev_angles = [5,10,20,35,90]
    percentages = [*np.arange(0.01, 0.1, 0.01),
                   *np.arange(0.1, 1, 0.1),
                   *range(1, 10+1, 1)]
    Ast = [[],[],[],[],[],[],[],[],[],[]]

    for p in percentages:
        for i, theta_deg in enumerate(fs_elev_angles):
            enh = p619._tropospheric_scintillation_attenuation(f_ghz, theta_deg, p, nwet_ppm,
                                                               None, None, ga_dbi)
            enh = abs(enh) # enhancements are negative sign, fades are positive sign
            Ast[i].append(enh)

            fade = p619._tropospheric_scintillation_attenuation(f_ghz, theta_deg, 100-p, nwet_ppm,
                                                                None, None, ga_dbi)
            Ast[i+5].append(fade)

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlim((0.01, 10))
    ax1.set_xticks([0.01,0.1,1,10])
    ax1.set_ylim((0.1, 10))
    ax1.set_yticks([0.1,1,10])
    ax1.plot(percentages, Ast[0], color='#FF0000', linestyle='dotted', label='5%, enhanc.')
    ax1.plot(percentages, Ast[1], color='#0000FF', linestyle='dotted', label='10%, enhanc.')
    ax1.plot(percentages, Ast[2], color="#00AA00", linestyle='dotted', label='20%, enhanc.')
    ax1.plot(percentages, Ast[3], color='#FF00FF', linestyle='dotted', label='35%, enhanc.')
    ax1.plot(percentages, Ast[4], color="#777777", linestyle='dotted', label='90%, enhanc.')
    ax1.plot(percentages, Ast[5], color='#FF0000', label='5%, fade')
    ax1.plot(percentages, Ast[6], color='#0000FF', label='10%, fade')
    ax1.plot(percentages, Ast[7], color='#00AA00', label='20%, fade')
    ax1.plot(percentages, Ast[8], color='#FF00FF', label='35%, fade')
    ax1.plot(percentages, Ast[9], color='#777777', label='90%, fade')
    ax1.set_title('FIGURE 8\nTropospheric scintillation enhancements and fades plotted against ' \
                  'free-space elevation angle\nfor N$_{wet}$ = 42.5 at 30 GHz, antenna gain = 0 ' \
                  'dBi')
    ax1.set_xlabel('Percentage time fades and enhancements exceeded')
    ax1.set_ylabel('Enhancement, fade (dB)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_8()
