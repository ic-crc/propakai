# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 3 from ITU-R P.619-6."""

import matplotlib.pyplot as plt
from propakai import p619_6 as p619
from propakai import p835_6 as p835


def figure_3() -> None:
    """Calculates values and display FIGURE 3 from ITU-R P.619-6."""
    f_ghz = 30
    he_km = 1
    hs_km = 100
    ref_atm = p835.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL
    elev_angles = []
    rho0s = [2.5, 7.5, 12.5]
    att = [[],[],[]]

    for theta_e_deg in range(-10, 90+1, 1):
        elev_angles.append(theta_e_deg)
        for i, rho0 in enumerate(rho0s):
            Ag_dB, status = p619.earth_space_path_gaseous_attenuation(f_ghz, he_km, hs_km,
                                                                      theta_e_deg, None,
                                                                      None, ref_atm, rho0)
            if status == p619.CalculationStatus.COMPLETED:
                att[i].append(Ag_dB)
            else:
                att[i].append(None)
            print(f'{theta_e_deg:.1f}°, {rho0:.1f} g/m3, {Ag_dB:.3f} dB, {status}')

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_yscale('log')
    ax1.set_xlim((-10, 90))
    ax1.set_xticks([*range(-10, 90+1, 10)])
    ax1.set_ylim((0.1, 100))
    ax1.plot(elev_angles, att[2], color='#0000FF', label='12.5 g/m$^3$')
    ax1.plot(elev_angles, att[1], color='#FF0000', linestyle='--', label='7.5 g/m$^3$')
    ax1.plot(elev_angles, att[0], color='#000000', linestyle='--', label='2.5 g/m$^3$')
    ax1.set_title('FIGURE 3\nAtmospheric attenuation vs. elevation angle along Earth-space ' \
                  'propagation path (earth station altitude = 1 km,\nspace station altitude = ' \
                  '100 km, frequency = 30 GHz)')
    ax1.set_xlabel('Apparent elevation angle (degrees)')
    ax1.set_ylabel('Atmospheric attenuation (dB)')
    ax1.legend(title='Water Vapour density on Earth surface')
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_3()
