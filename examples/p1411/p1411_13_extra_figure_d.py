# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
Site-specific near street level (residential area) figure (ITU-R P.1411-13). This figure is not
part of the recommendation.
"""

from math import sqrt
import matplotlib.pyplot as plt
from propakai import p1411_13 as p1411


def extra_figure_d() -> None:
    """
    Site-specific near street level (residential area) figure (ITU-R P.1411-13). This figure is not
    part of the recommendation.
    """
    f = 14 # Operating frequency (GHz), with 2 <= f_GHz <= 26.
    htx = 4 # Transmitter antenna height (m), with 1.2 <= hTx_m <= 6.
    hrx = 1.5 # Receiver antenna height (m), with 1.2 <= hRx_m <= 6.
    hbtx = 10 # Height of nearest building from transmitter in receiver direction (m).
    hbrx = 8 # Height of nearest building from receiver in transmitter direction (m).
    a = 25 # Distance between transmitter and nearest building from transmitter (m).
    c = 25 # Distance between receiver and nearest building from receiver (m).
    m = 9  # Average building height of the buildings with less than 3 stories (m).
    n = 200 # Building density (buildings/km2).
    x1 = 200
    x2 = 800
    max_road_dist = x1+x2
    dists = []
    losses = [[],[],[],[]]
    for road_dist in range(x1, max_road_dist+1, 1):
        # one 90 deg street corner at 200 meters from station1
        x2_temp = road_dist-x1
        d = sqrt((x1*x1)+(x2_temp*x2_temp)) # Distance between the two terminals (m),
                                            # with 0 <= d_m <= 1000.
        dists.append(road_dist)
        theta_list = [90.0]
        x1_list = [float(x1)]
        x2_list = [float(x2_temp)]
        b = d-a-c # Distance between nearest buildings from transmitter and receiver (m).

        L, Lr, Lb, Lv = p1411.site_specific_near_street_level_residential(f_ghz=f, d_m=d,
                            htx_m=htx, hrx_m=hrx, hbtx_m=hbtx, hbrx_m=hbrx, a_m=a, b_m=b,
                            c_m=c, m_m=m, n_bldgkm2=n, theta_list_deg=theta_list,
                            x1_list_m=x1_list, x2_list_m=x2_list)
        losses[0].append(L)
        losses[1].append(Lr)
        losses[2].append(Lb)
        losses[3].append(Lv)

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_xlim((0, max_road_dist))
    ax1.set_xticks([*range(0, max_road_dist+1, 50)])
    ax1.set_ylim((240, 80))
    ax1.set_yticks([*range(80, 240+1, 20)])
    ax1.plot(dists, losses[0], color='#008DD2', label='L')
    ax1.plot(dists, losses[1], color='#E31E24', label='Lr (along road)')
    ax1.plot(dists, losses[2], color='#1D8545', label='Lb (between houses)')
    ax1.plot(dists, losses[3], color='#B73B7B', label='Lv (over roofs)')
    ax1.set_title('EXTRA FIGURE D\nSite-specific near street level (residential area)\n' \
                  'with one 90 degrees street corner at 200m from station 1')
    ax1.set_xlabel('Road distance (m)')
    ax1.set_ylabel('Path loss (dB)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    extra_figure_d()
