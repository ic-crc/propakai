# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 1 from ITU-R P.1546-6."""

import matplotlib.pyplot as plt
from propakai import p1546_6 as p1546


def figure_1() -> None:
    """Calculates values and display FIGURE 1 from ITU-R P.1546-6."""
    f_mhz = 100
    t_percent = 50
    path = p1546.Path.LAND
    h1_list = [10, 20, 37.5, 75, 150, 300, 600, 1200]
    d_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,25,30,35,40,45,50,55,60,65,70,75,
              80,85,90,95,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,325,350,375,
              400,425,450,475,500,525,550,575,600,625,650,675,700,725,750,775,800,825,850,875,900,
              925,950,975,1000]
    E_per_h1 = []

    for h1 in h1_list:
        E_list = [] 
        for d in d_list:
            E = p1546._fs_tables_interpolation(f_mhz, t_percent, path, h1, d,
                                               0, (), None) # unused params (h1>=0)
            E_list.append(E)
        E_per_h1.append(E_list)

    fig, ax1 = plt.subplots()
    fig.set_size_inches(7, 8)
    ax1.set_xscale('log')
    ax1.set_xlim((1,1000))
    ax1.set_xticks(ticks=[1, 10, 100, 1000], labels=['1', '10', '100', '1000'])
    ax1.set_ylim((-80, 120))
    ax1.set_yticks([*range(-80, 120+1, 10)])
    for i, E_list in enumerate(E_per_h1):
        ax1.plot(d_list, E_list, label=f'{h1_list[i]} m')

    path_str_map = {p1546.Path.LAND: 'land path',
                    p1546.Path.COLD_SEA : 'cold sea path',
                    p1546.Path.WARM_SEA: 'warm sea path'}
    ax1.set_title(f'FIGURE 1\n{f_mhz:.0f} MHz, {path_str_map[path]}, {t_percent:.0f}% time')
    ax1.set_xlabel('Distance (km)')
    ax1.set_ylabel('Field strength (dB(μVm)) for 1 kW e.r.p.')
    ax1.legend(title='Transmitting/base\nantenna heights, h1')
    plt.grid(True, 'both','both')
    plt.show()


if __name__ == '__main__':
    figure_1()
