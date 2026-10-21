# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 4 from ITU-R P.676-13."""

import matplotlib.pyplot as plt
from propakai import p676_13 as p676
from propakai import p835_6 as p835


def figure_4() -> None:
    """Calculates values and display FIGURE 4 from ITU-R P.676-13."""
    freqs = []
    atts = [[],[]]
    MAGRA = p835.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL
    for f_ghz in range(1, 1001, 1):
        freqs.append(f_ghz)
        att_std_dB, _, _ = p676.slant_path_gaseous_attenuation(f_ghz=f_ghz, h1_km=0, h2_km=100.01,
                                                               phi1_deg=90, atm=MAGRA, rho0_gm3=7.5)
        atts[0].append(att_std_dB)
        # Note: The "peaks" of the dry curve generated here do not perfectly match those from
        # the figure in the recommendation. Not sure what input parameters were used.
        att_dry_dB, _, _ = p676.slant_path_gaseous_attenuation(f_ghz=f_ghz, h1_km=0, h2_km=100.01,
                                                               phi1_deg=90, atm=MAGRA, rho0_gm3=0)
        atts[1].append(att_dry_dB)
        print(f'{f_ghz} GHz, {att_std_dB:.3f} dB, {att_dry_dB:.3f} dB')

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_yscale('log')
    ax1.set_xlim((0,1000))
    ax1.set_xticks([*range(0, 1000+1, 100)])
    ax1.set_ylim((1E-3, 1E5))
    ax1.set_yticks([1E-3,1E-2,1E-1,1,1E1,1E2,1E3,1E4,1E5])
    ax1.plot(freqs, atts[0], color='#FF0000', label='standard')
    ax1.plot(freqs, atts[1], color='#0000FF', label='dry')
    ax1.set_title('FIGURE 4\nZenith attenuation due to atmospheric gases, calculated at 1 GHz ' \
                  'intervals, including line centre')
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('Zenith attenuation (dB)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_4()
