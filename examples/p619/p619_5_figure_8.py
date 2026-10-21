# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 8 from ITU-R P.619-5."""

import matplotlib.pyplot as plt
import numpy as np
from propakai import p619_6 as p619


def figure_8() -> None:
    """Calculates values and display FIGURE 8 from ITU-R P.619-5."""
    heights = [0,0.5,1,2,3,5]
    theta0s = []
    Abs = [[],[],[],[],[],[]]
    for theta0_deg in np.arange(0, 6.1,0.1):
        theta0s.append(theta0_deg)
        for i, h in enumerate(heights):
            Abs[i].append(p619.beam_spreading_loss(theta0_deg, h))

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_xlim((0, 6))
    ax1.set_xticks([*np.arange(0, 6+0.01, 0.5)])
    ax1.set_ylim((0, 0.9))
    ax1.plot(theta0s, Abs[0], color='#000080', label='0 km')
    ax1.plot(theta0s, Abs[1], color='#FF8027', label='0.5 km')
    ax1.plot(theta0s, Abs[2], color='#808080', label='1 km')
    ax1.plot(theta0s, Abs[3], color='#FFC000', label='2 km')
    ax1.plot(theta0s, Abs[4], color='#00B0FF', label='3 km')
    ax1.plot(theta0s, Abs[5], color='#008000', label='5 km')
    ax1.set_title('FIGURE 8\nBeam spreading loss in both the Earth-to-space and space-to-Earth ' \
                  'directions')
    ax1.set_xlabel('Free-space elevation angle (degrees)')
    ax1.set_ylabel('Beam spreading loss (dB)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_8()
