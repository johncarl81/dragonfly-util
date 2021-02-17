#!/usr/bin/env python

import argparse, csv
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from waypointUtil import build3DDDSAWaypoints, Span

def main():

    waypoints = build3DDDSAWaypoints(Span.RANGE, 2, 1, 0, 3, 1, 1)

    lat = [w.y for w in waypoints]
    lon = [w.x for w in waypoints]
    alt = [w.z for w in waypoints]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')



    ax.plot(lat, lon, alt, 'k--', label='DDSA Path')
    ax.legend()

    ax.set_xlabel('Latitude')
    ax.set_xlim(max(lat), min(lat))
    ax.set_ylabel('Longitude')
    ax.set_zlabel('Altitude')


    plt.show()

if __name__ == '__main__':
    main()
