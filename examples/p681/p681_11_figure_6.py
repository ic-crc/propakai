# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 6 from ITU-R P.681-11."""

from typing import Callable
import inspect
import matplotlib.pyplot as plt
from propakai import p681_11 as p681


def figure_6a() -> None:
    """Calculates values and display FIGURE 6a from ITU-R P.681-11."""
    _figure_6('MKF of a street canyon', p681.street_canyon_masking_function)


def figure_6b() -> None:
    """Calculates values and display FIGURE 6b from ITU-R P.681-11."""
    _figure_6('MKF of a single wall', p681.single_wall_masking_function)


def figure_6c() -> None:
    """Calculates values and display FIGURE 6c from ITU-R P.681-11."""
    _figure_6('MKF of a street crossing', p681.street_crossing_masking_function)


def figure_6d() -> None:
    """Calculates values and display FIGURE 6d from ITU-R P.681-11."""
    _figure_6('MKF of a T-junction', p681.t_junction_masking_function)


def _figure_6(subtitle: str, masking_function: Callable) -> None:

    def masking_function_calls(phi_min, phi_max, mask_func):
        h_m = 20
        w1_m = 20
        w2_m = 20
        phi_list = []
        theta_list = []
        arg_count = len(inspect.signature(masking_function).parameters)
        for phi in range(phi_min, phi_max+1, 1):
            for theta in range(0, 90+1, 1):
                if arg_count == 4:
                    link_avail = mask_func(theta, h_m, w1_m, phi)
                else:
                    link_avail = mask_func(theta, h_m, w1_m, w2_m, phi)
                if link_avail is False:
                    phi_list.append(phi)
                    theta_list.append(theta)
        return (phi_list, theta_list)

    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.set_size_inches(8, 6.75)

    ax1.set_xlim((0, 180))
    ax1.set_xticks([*range(0, 180+1, 20)])
    ax1.set_ylim((0, 90))
    ax1.set_yticks([*range(0, 80+1, 20)])
    ax1.set_title(f'FIGURE 6\n{subtitle}')
    ax1.set_ylabel('Elevation angle (degrees)')
    ax1.grid(True, 'both','both')

    phis, thetas = masking_function_calls(0, 180, masking_function)
    ax1.scatter(phis, thetas, s=10, c='#000000')

    ax2.set_xlim((0, -180))
    ax2.set_xticks([*range(0, -180-1, -20)])
    ax2.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
    ax2.set_ylim((90, 0))
    ax2.set_yticks([*range(80, 0-1, -20)])
    ax2.set_xlabel('Azimuth (degrees)')
    ax2.set_ylabel('Elevation angle (degrees)')
    ax2.grid(True, 'both','both')

    phis, thetas = masking_function_calls(-180, 0, masking_function)
    ax2.scatter(phis, thetas, s=10, c='#000000')

    plt.show()


if __name__ == '__main__':
    figure_6a()
    figure_6b()
    figure_6c()
    figure_6d()
