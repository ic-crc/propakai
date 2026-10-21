# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 25 from ITU-R P.681-11."""

from dataclasses import dataclass
from math import degrees, atan
import matplotlib.pyplot as plt
from propakai import p681_11 as p681


def figure_25() -> None:
    """Calculates values and display FIGURE 25 from ITU-R P.681-11."""
    h_m = 20
    w_m = 20
    l_m = 200

    delta_phi_min = 0
    delta_phi_max = 90
    delta_phi_list = [*range(delta_phi_min, delta_phi_max+1, 1)]

    MKA = degrees(atan(h_m/(w_m/2))) # eq.(9)

    @dataclass
    class _TestCase:
        index: int
        name: str
        color: str
        theta1_deg: float
        theta2_deg: float
        rho_list: list[float]
    case_list = []

    # Special case 1: both satellites are above the MKA for any azimuth spacing
    case_1 = _TestCase(index=0,
                       name='Special case 1',
                       color='#FF0000',
                       theta1_deg = MKA + (90-MKA)*0.1,
                       theta2_deg = MKA + (90-MKA)*0.2,
                       rho_list=[])
    case_list.append(case_1)

    # Special case 2: one satellite is always above MKA and the other is always below
    case_2 = _TestCase(index=1,
                       name='Special case 2',
                       color='#00AA00',
                       theta1_deg = MKA*0.33,
                       theta2_deg = MKA + (90-MKA)*0.5,
                       rho_list=[])
    case_list.append(case_2)

    # Special case 3: the two satellites are at the same elevation
    case_3 = _TestCase(index=2,
                       name='Special case 3',
                       color='#0000FF',
                       theta1_deg = MKA*0.375,
                       theta2_deg = MKA*0.375,
                       rho_list=[])
    case_list.append(case_3)

    # Special case 4: satellites with very different elevations
    case_4 = _TestCase(index=3,
                       name='Special case 4',
                       color='#FF7700',
                       theta1_deg = MKA * 0.001,
                       theta2_deg = MKA * 0.999,
                       rho_list=[])
    case_list.append(case_4)

    # General model
    case_5 = _TestCase(index=4,
                       name='General model',
                       color='#000000',
                       theta1_deg = MKA * 0.35,
                       theta2_deg = MKA * 0.65,
                       rho_list=[])
    case_list.append(case_5)

    # Compute rho values
    for case_i in case_list:
        for delta_phi_deg in delta_phi_list:
            rho = p681.shadowing_cross_correlation_coefficient(delta_phi_deg, case_i.theta1_deg,
                                                               case_i.theta2_deg, h_m, w_m, l_m)
            case_i.rho_list.append(rho)

    fig, ax1 = plt.subplots()
    fig.set_size_inches(8, 6.75)
    ax1.set_xlim((delta_phi_min, delta_phi_max))
    ax1.set_ylim((-1.1, 1.1))
    ax1.set_yticks([-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1])
    for case_i in case_list:
        ax1.plot(delta_phi_list, case_i.rho_list, case_i.color, linestyle='solid',
                 label=case_i.name)
    ax1.set_title('FIGURE 25\nThree segment cross correlation coefficient model')
    ax1.set_xlabel('Azimuth spacing (degrees)')
    ax1.legend()
    ax1.set_ylabel('Correlation coefficient')
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_25()
