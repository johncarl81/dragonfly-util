#!/usr/bin/env python

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from pykrige.ok import OrdinaryKriging
from VirtualPlume import dotdict
from matplotlib.colors import LinearSegmentedColormap

PARTITIONS = 10

class Reading:
    def __init__(self, value, lat, lon):
        self.value = float(value)
        self.lat = float(lat)
        self.lon = float(lon)

    def add(self, latadd, lonadd):
        return Reading(self.value, self.lat + latadd, self.lon + lonadd)

def buildReadings(name, input):
    df=pd.read_csv(input, ",")

    lons=np.array(df[name + '.lon'])
    lats=np.array(df[name + '.lat'])
    data=np.array(df[name + '.value'])

    readings = []

    for i in range(len(lons)):
        readings.append(Reading(data[i], lats[i], lons[i]))

    return readings

def writecsv(input, output, start_time):
    readings = buildReadings(input, False, start_time)
    with open(output, 'w') as outputFile:
        outputFile.write("{}, {}, {}, {}, {}\n".format("time", "co2", "lat", "lon", "alt"))
        for reading in readings:
            outputFile.write("{}, {}, {}, {}, {}\n".format(reading.time, reading.value, reading.lat, reading.lon, reading.alt))

def plot_flight(ax, flight_data, color, style, name):
    ax.plot([v.lon for v in flight_data], [v.lat for v in flight_data], color = color, linestyle=style, zorder=3, label=name)
    markersize = 50
    ax.scatter(flight_data[0].lon, flight_data[0].lat, color = color, marker = 'o', s = markersize, zorder=3)

    for i in range(0, PARTITIONS):
        middle = i * len(flight_data) / PARTITIONS
        ax.scatter(flight_data[middle].lon, flight_data[middle].lat, color = color, marker = '>', s = markersize, zorder=3)
    last = len(flight_data) - 1
    ax.scatter(flight_data[last].lon, flight_data[last].lat, color = color, marker='X', s = markersize, zorder=3)

def linearRegressionNormal(readingPositions):

    x = []
    y = []

    for readingPosition in readingPositions:
        x.append([readingPosition.lon, readingPosition.lat])
        y.append(readingPosition.value)

    x, y = np.array(x), np.array(y)

    model = LinearRegression().fit(x, y)

    return dotdict({
        "x": model.coef_[0],
        "y": model.coef_[1]
    })

def heatmap(data, fig, ax, nlags):
    # get colormap
    ncolors = 256
    reds_color_array = plt.get_cmap('Reds')(range(ncolors))
    blues_color_array = plt.get_cmap('Blues')(range(ncolors))

    # change alpha values
    reds_color_array[:,-1] = np.linspace(0.0,1.0,ncolors)
    blues_color_array[:,-1] = np.linspace(0.0,1.0,ncolors)

    # create a colormap object
    reds_map_object = LinearSegmentedColormap.from_list(name='reds_alpha',colors=reds_color_array)
    plt.register_cmap(cmap=reds_map_object)
    blues_map_object = LinearSegmentedColormap.from_list(name='blues_alpha',colors=blues_color_array)
    plt.register_cmap(cmap=blues_map_object)

    lons=np.array([v.lon for v in data])
    lats=np.array([v.lat for v in data])
    data=np.array([v.value for v in data])

    grid_space = (max(lats) - min(lats)) / 100
    grid_lon = np.arange(np.amin(lons) - 0.00003, np.amax(lons) + 0.00003, grid_space) #grid_space is the desired delta/step of the output array
    grid_lat = np.arange(np.amin(lats) - 0.00002, np.amax(lats) + 0.00004, grid_space)

    OK = OrdinaryKriging(lons, lats, data, variogram_model='gaussian', verbose=True, nlags=nlags)
    z1, ss1 = OK.execute('grid', grid_lon, grid_lat)

    xintrp, yintrp = np.meshgrid(grid_lon, grid_lat)

    cs=ax.contourf(xintrp, yintrp, z1, np.linspace(420, 520, 100), cmap='blues_alpha', zorder=2)

    cs_lines = ax.contour(xintrp, yintrp, z1, np.linspace(420, 520, 20), cmap='reds_alpha', linewidths = 0.8)

    cbar = fig.colorbar(cs)
    cbar.add_lines(cs_lines)
    cbar.ax.set_ylabel('$CO_2$ (ppm)')

def main():
    df1data = buildReadings('df1', 'gradient_descent_mission.log')
    df2data = buildReadings('df2', 'gradient_descent_mission.log')
    df3data = buildReadings('df3', 'gradient_descent_mission.log')

    df1data = df1data[550:1400]
    df2data = df2data[550:1400]
    df3data = df3data[550:1400]

    fig, ax = plt.subplots(figsize=(5, 5))
    params = {'mathtext.default': 'regular' }
    plt.rcParams.update(params)

    plot_flight(ax, df1data, 'C0', '-', 'dragonfly1')
    plot_flight(ax, df2data, 'C1', '--', 'dragonfly2')
    plot_flight(ax, df3data, 'C2', '-.', 'dragonfly3')

    ax.set_ylabel('Latitude')
    ax.set_xlabel('Longitude')
    ax.ticklabel_format(useOffset=False)

    ax.legend()

    # lmin = -106.59838
    # lmax = -106.59429
    # rmin = 35.19344
    # rmax = 35.19665
    #
    # img = plt.imread('balloon_fiesta.png')
    # ax.imshow(img, extent=[lmin, lmax, rmin, rmax])

    connection_line_color = 'k'
    connection_line_style = ':'


    def plot_connections(index):
        ax.plot([df1data[index].lon, df2data[index].lon], [df1data[index].lat, df2data[index].lat], color = connection_line_color, linestyle=connection_line_style, zorder=4)
        ax.plot([df3data[index].lon, df2data[index].lon], [df3data[index].lat, df2data[index].lat], color = connection_line_color, linestyle=connection_line_style, zorder=4)

    def plot_normal(index):
        norm = linearRegressionNormal([df1data[index], df2data[index], df3data[index]])
        magnitude = math.sqrt(norm.x * norm.x + norm.y * norm.y)
        ax.arrow(df2data[index].lon, df2data[index].lat, norm.x * 0.00002 / magnitude, norm.y * 0.00002 / magnitude, head_width=0.00001, head_length=0.00001, width=0.000001, fc='k', ec='k', zorder=5)

    for i in range(PARTITIONS):
        middle = i * len(df3data) / PARTITIONS
        plot_connections(middle)
        plot_normal(middle)

    last = len(df3data) - 1
    plot_connections(last)
    plot_normal(last)

    heatmap(df1data + df2data + df3data, fig, ax, 20)

    # plt.xlim(-106.5968, -106.5958)
    # plt.ylim(35.1940, 35.1953)

    ax.locator_params(nbins=3)
    plt.yticks(rotation=90)

    plt.tight_layout()
    plt.savefig('Balloon_Fiesta_Gradient_Descent.pdf', dpi=300, bbox_inches='tight')

if __name__ == '__main__':
    main()
