#!/usr/bin/env python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def main():
    df=pd.read_csv('csv/Tobias 01042021 HB CO2_for_IROS2021.csv', ",")

    time=np.array(df['Date'])
    avg=np.array(df['CO2_sensor_avg'])
    max=np.array(df['CO2_sensor_max'])

    fig, ax = plt.subplots(figsize=(5, 4))
    params = {'mathtext.default': 'regular' }
    plt.rcParams['legend.handlelength'] = 0.8
    plt.rcParams['legend.handleheight'] = 0.8
    plt.rcParams.update(params)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42

    max_values = ax.scatter(time, max, label='$CO_2$ Maximum', color='C0', s=4, marker='v')
    ave_values = ax.scatter(time, avg, label='$CO_2$ Mean', color='C1', s=4)

    ddsa_rectangle = ax.add_patch(Rectangle((100, -10), 5, 10000, ec=(0,0,0,1), fc=(1,0,0,0.2 ), ls='-.', label='DDSA'))
    lawnmower_rectangle = ax.add_patch(Rectangle((110, -10), 10, 10000, ec=(0,0,0,1), fc=(0,0,1,0.2 ), ls='--', label='Lawnmower'))

    ax.set_ylabel('$CO_2$ (ppm)')
    ax.set_xlabel('Time')

    ax.legend(loc='upper left', handles=[max_values, ave_values, ddsa_rectangle, lawnmower_rectangle])

    plt.xticks([(2 * v * 12) + 2 for v in range(0, 13)], ["{}:00".format(v) for v in range(0, 26, 2)])
    plt.xticks(rotation=-45)
    plt.yticks(rotation=90)

    plt.tight_layout()
    plt.savefig('Hummingbird_Ground_Truth.pdf', dpi=300, bbox_inches='tight')
    # plt.show()

if __name__ == '__main__':
    main()
