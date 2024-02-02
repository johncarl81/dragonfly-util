#!/usr/bin/env python

import math, datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from pykrige.ok import OrdinaryKriging
from VirtualPlume import dotdict
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

PARTITIONS = 10

class Reading:
    def __init__(self, value, lat, lon, time):
        self.value = float(value)
        self.lat = float(lat)
        self.lon = float(lon)
        self.time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

def buildReadings(input):
    df=pd.read_csv(input, ",")

    lons=np.array(df['lon'])
    lats=np.array(df['lat'])
    data=np.array(df['co2'])
    time=np.array(df['time'])

    readings = []

    for i in range(len(lons)):
        readings.append(Reading(data[i], lats[i], lons[i], time[i]))

    return readings

def plot_flight(ax, flight_data, color, style, name):
    ax.plot([v.lon for v in flight_data], [v.lat for v in flight_data], color=color, linestyle=style, zorder=3, label=name)
    markersize = 50
    ax.scatter(flight_data[0].lon, flight_data[0].lat, color = color, marker = 'o', s = markersize, zorder=3)

    for i in range(1, PARTITIONS):
        middle = i * len(flight_data) / PARTITIONS
        ax.scatter(flight_data[middle].lon, flight_data[middle].lat, color = color, marker = 's', s = markersize, zorder=3)
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

def addRuler(plt, ax, length):
    lowerleft = [plt.xlim()[0], plt.ylim()[0]]
    upperright = [plt.xlim()[1], plt.ylim()[1]]

    # Calculate width by latitide
    earthCircumference = 40008000
    width = abs(1.0 * length / ((earthCircumference / 360) * math.cos(lowerleft[1] * 0.01745)))
    height = (upperright[1] - lowerleft[1]) * 0.018

    location = [plt.xlim()[0] + (plt.xlim()[1] - plt.xlim()[0]) *.95 - length, plt.ylim()[0] + (plt.ylim()[1] - plt.ylim()[0]) *.03]

    ax.add_patch(Rectangle(location, width, height, ec=(0,0,0,1), fc=(1,1,1,1)))
    ax.add_patch(Rectangle(location, width/2, height, ec=(0,0,0,1), fc=(0,0,0,1)))
    ax.annotate("0", xy=(location[0], location[1] + (1.5 * height)), ha='center')
    ax.annotate("{} m".format(length), xy=(location[0] + width, location[1] + (1.5 * height)), ha='center')

def heatmap(data, fig, ax, nlags):
    # get colormap
    ncolors = 256
    reds_color_array = plt.get_cmap('Reds')(range(ncolors))
    blues_color_array = plt.get_cmap('Blues')(range(ncolors))

    # change alpha values
    reds_color_array[:,-1] = np.linspace(0.0,1.0,ncolors)
    blues_color_array[:,-1] = np.linspace(0.0,1.0,ncolors)

    # create a colormap object
    if 'reds_alpha' not in plt.colormaps():
        reds_map_object = LinearSegmentedColormap.from_list(name='reds_alpha',colors=reds_color_array)
        plt.register_cmap(cmap=reds_map_object)
    if 'blues_alpha' not in plt.colormaps():
        blues_map_object = LinearSegmentedColormap.from_list(name='blues_alpha',colors=blues_color_array)
        plt.register_cmap(cmap=blues_map_object)

    lons=np.array([v.lon for v in data])
    lats=np.array([v.lat for v in data])
    data=np.array([v.value for v in data])

    grid_space = (max(lats) - min(lats)) / 100
    grid_lon = np.arange(np.amin(lons) - 0.00002, np.amax(lons) + 0.00002, grid_space) #grid_space is the desired delta/step of the output array
    grid_lat = np.arange(np.amin(lats) - 0.00002, np.amax(lats) + 0.00001, grid_space)

    OK = OrdinaryKriging(lons, lats, data, variogram_model='gaussian', verbose=True, nlags=nlags)
    z1, ss1 = OK.execute('grid', grid_lon, grid_lat)

    xintrp, yintrp = np.meshgrid(grid_lon, grid_lat)

    cs = ax.contourf(xintrp, yintrp, z1, np.linspace(420, 500, 100), cmap='Blues', zorder=2)

    cs_lines = ax.contour(xintrp, yintrp, z1, np.linspace(420, 500, 20), cmap='Reds', linewidths = 0.8)

    cbar = fig.colorbar(cs)
    cbar.add_lines(cs_lines)
    cbar.ax.set_ylabel('$CO_2$ (ppm)')

def distance(one, two):
    earthCircumference = 40008000
    dx = (one.lon - two.lon) * (earthCircumference / 360) * math.cos(one.lat * 0.01745)
    dy = (one.lat - two.lat) * (earthCircumference / 360)

    return math.sqrt((dx * dx) + (dy * dy))

def distanceList(one, two):
    return [distance(tuple[0], tuple[1]) for tuple in zip(one, two)]

def timeList(data):
    # return [d.time for d in data]
    return range(len(data))

def main():
    df2data = buildReadings('csv/balloon_fiesta_flocking_df2.csv')
    df3data = buildReadings('csv/balloon_fiesta_flocking_df3.csv')
    df4data = buildReadings('csv/balloon_fiesta_flocking_df4.csv')

    df2data = df2data[1200:1700]
    df3data = df3data[1200:1700]
    df4data = df4data[1190:1690]

    fig, ax = plt.subplots(figsize=(5, 3.8))
    params = {'mathtext.default': 'regular' }
    plt.rcParams.update(params)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42

    # lmin = -106.59838
    # lmax = -106.59429
    # rmin = 35.19344
    # rmax = 35.19665
    #
    # img = plt.imread('balloon_fiesta.png')
    # ax.imshow(img, extent=[lmin, lmax, rmin, rmax])

    plot_flight(ax, df2data, 'C0', '-', 'dragonfly1')
    plot_flight(ax, df3data, 'C1', '--', 'dragonfly2')
    plot_flight(ax, df4data, 'C2', '-.', 'dragonfly3')

    ax.set_ylabel('Latitude')
    ax.set_xlabel('Longitude')
    ax.ticklabel_format(useOffset=False)

    connection_line_color = 'k'
    connection_line_style = ':'


    def plot_connections(index):
        ax.plot([df2data[index].lon, df3data[index].lon], [df2data[index].lat, df3data[index].lat], color = connection_line_color, linestyle=connection_line_style, zorder=4)
        ax.plot([df4data[index].lon, df3data[index].lon], [df4data[index].lat, df3data[index].lat], color = connection_line_color, linestyle=connection_line_style, zorder=4)

    def plot_normal(index):
        norm = linearRegressionNormal([df2data[index], df3data[index], df4data[index]])
        magnitude = math.sqrt(norm.x * norm.x + norm.y * norm.y)
        ax.arrow(df3data[index].lon, df3data[index].lat, norm.x * 0.00002 / magnitude, norm.y * 0.00002 / magnitude, head_width=0.00001, head_length=0.00001, width=0.000001, fc='k', ec='k', zorder=5)

    for i in range(PARTITIONS):
        middle = i * len(df3data) / PARTITIONS
        plot_connections(middle)
        # plot_normal(middle)

    for i in range(50):
        middle = i * len(df3data) / 50
        plot_normal(middle)
    last = len(df4data) - 1
    plot_connections(last)
    plot_normal(last)

    heatmap(df2data + df3data + df4data, fig, ax, 10)

    ax.locator_params(nbins=3)
    plt.yticks(rotation=90)
    ax.legend()

    # plt.xlim(-106.5968, -106.5958)
    # plt.ylim(35.1940, 35.1953)

    plt.tight_layout()
    plt.savefig('Balloon_Fiesta_Flocking.pdf', dpi=300, bbox_inches='tight')

    plt.clf()
    params = {'mathtext.default': 'regular' }
    plt.rcParams.update(params)

    plt.plot(timeList(df2data), distanceList(df2data, df3data), color = 'C0', linestyle='--', label='$|x_{1,2}|$')
    plt.plot(timeList(df2data), distanceList(df3data, df4data), color = 'C0', linestyle=':',  label='$|x_{2,3}|$')
    plt.plot(timeList(df2data), [math.sqrt(6*6+6*6)]*len(df2data), color = 'C0', linestyle='-', lw=0.8, label='$|x_{1,2}|$ and $|x_{2,3}|$ target separation: 8.5m')
    plt.plot(timeList(df2data), distanceList(df4data, df2data), color = 'C1', linestyle='-.', label='$|x_{1,3}|$')
    plt.plot(timeList(df2data), [6+6]*len(df2data), color = 'C1', linestyle='-', lw=0.8, label='$|x_{1,3}|$ target separation: 12m')
    plt.legend()

    print "DF1,2 Min: {} Max{}".format(min(distanceList(df2data, df3data)), max(distanceList(df2data, df3data)))
    print "DF2,3 Min: {} Max{}".format(min(distanceList(df3data, df4data)), max(distanceList(df3data, df4data)))
    print "DF3,1 Min: {} Max{}".format(min(distanceList(df2data, df4data)), max(distanceList(df2data, df4data)))


    print "DF1,2 Min: {} Max{}".format(min(distanceList(df2data, df3data)) - math.sqrt(6*6+6*6), max(distanceList(df2data, df3data)) - math.sqrt(6*6+6*6))
    print "DF2,3 Min: {} Max{}".format(min(distanceList(df3data, df4data)) - math.sqrt(6*6+6*6), max(distanceList(df3data, df4data)) - math.sqrt(6*6+6*6))
    print "DF3,1 Min: {} Max{}".format(min(distanceList(df2data, df4data)) - (6+6), max(distanceList(df2data, df4data)) - (6+6))

    plt.ylim(0, 15)
    plt.ylabel('Separation (m)')
    plt.xlabel('Flight time (s)')

    addRuler(plt, ax, 20)

    plt.savefig('Balloon_Fiesta_Flocking_Distance.pdf', dpi=300, bbox_inches='tight')

if __name__ == '__main__':
    main()
