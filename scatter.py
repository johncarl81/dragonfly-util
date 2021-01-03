#!/usr/bin/env python

import argparse, csv
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

def writescatter(input):

    readings = []
    lat = []
    lon = []
    alt = []
    with open(input) as csvfile:
        for row in csv.reader(csvfile):
            if(float(row[0]) > 420):
                readings.append(float(row[0]))
                lat.append(float(row[1]))
                lon.append(float(row[2]))
                alt.append(float(row[3]))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    min_reading = min(readings)
    max_reading = max(readings)

    print "Min: {} Max: {}".format(min_reading, max_reading)

    readings = [2000 * ((reading - min_reading) / (max_reading - min_reading)) ** 2 for reading in readings]


    print "Min: {} Max: {}".format(min(readings), max(readings))

    sc = ax.scatter(lat, lon, alt, s=readings, marker='o')
    ax.plot(lat, lon, alt, 'k--', label='parametric curve 1')
    ax.legend()

    ax.set_xlabel('Latitude')
    ax.set_xlim(max(lat), min(lat))
    ax.set_ylabel('Longitude')
    ax.set_zlabel('Altitude')

    # produce a legend with the unique colors from the scatter
    # legend1 = ax.legend(*scatter.legend_elements(),
    #                     loc="lower left", title="Classes")
    # ax.add_artist(legend1)

    # produce a legend with a cross section of sizes from the scatter
    # handles, labels = scatter.legend_elements(prop="sizes", alpha=0.6)
    # legend2 = ax.legend(handles, labels, loc="upper right", title="Sizes")

    # plt.legend(*sc.legend_elements("sizes", num=6))
    #
    # fig.legend(markerscale=2)
    # handles, labels = sc.legend_elements(prop="sizes", alpha=0.6)
    # legend2 = ax.legend(handles, labels, loc="upper right", title="Sizes")

    max_size = 5
    legendCircles = []
    legendNames = []
    for i in range(0, max_size):
        legendCircles.append(Line2D([0], [0], marker="o", alpha=0.4, markersize=i * 10))
        legendNames.append("{}ppm".format(int(min_reading + ((1.0 * i / max_size) * (max_reading - min_reading)))))

    plt.legend(legendCircles, legendNames, numpoints=1, loc="best")


    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Plots CSV to scatter plot')
    parser.add_argument('--input', type=str, help='Input CSV.')
    # parser.add_argumenInputt('--input', type=str, help=' CSV.')
    args = parser.parse_args()

    writescatter(args.input)
