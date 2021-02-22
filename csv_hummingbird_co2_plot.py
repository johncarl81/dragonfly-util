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

    fig, ax = plt.subplots(figsize=(5, 5))
    params = {'mathtext.default': 'regular' }
    plt.rcParams.update(params)

    ax.scatter(time, max, label='$CO_2$ Maximum', color='C0', s=4, marker='v')
    ax.scatter(time, avg, label='$CO_2$ Average', color='C1', s=4)

    ax.add_patch(Rectangle((110, 420), 12, 1000, ec=(0,0,0,1), fc=(1,0,0,0.2 ), ls='-.'))

    ax.set_ylabel('$CO_2$ (ppm)')
    ax.set_xlabel('Time on January 4, 2021')

    ax.legend()

    plt.xticks([(2 * v * 12) + 2 for v in range(0, 13)], ["{}:00".format(v) for v in range(0, 26, 2)])
    plt.xticks(rotation=-45)
    plt.yticks(rotation=90)

    plt.tight_layout()
    plt.savefig('HummingbirdGroundTruth.pdf', dpi=300, bbox_inches='tight')
    # plt.show()

if __name__ == '__main__':
    main()
