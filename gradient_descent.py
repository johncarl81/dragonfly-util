#!/usr/bin/env python

import math
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
    def __init__(self, value, lat, lon):
        self.value = float(value)
        self.lat = float(lat)
        self.lon = float(lon)

    def add(self, latadd, lonadd):
        return Reading(self.value, self.lat + latadd, self.lon + lonadd)

def buildReadings(input):
    df=pd.read_csv(input, ",")

    lons=np.array(df['lon'])
    lats=np.array(df['lat'])
    data=np.array(df['co2'])

    readings = []

    for i in range(len(lons)):
        readings.append(Reading(data[i], lats[i], lons[i]))

    return readings


def plot_flight(ax, flight_data, color, style, name):
    ax.plot([v.lon for v in flight_data], [v.lat for v in flight_data], color = color, linestyle=style, zorder=3, label=name)
    markersize = 50
    ax.scatter(flight_data[0].lon, flight_data[0].lat, color = color, marker = 'o', s = markersize, zorder=3)

    for i in range(1, PARTITIONS):
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
    reds_color_array[:,-1] = np.linspace(0,1.0,ncolors)
    blues_color_array[:,-1] = np.linspace(0,1.0,ncolors)

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
    grid_lon = np.arange(np.amin(lons) - 0.0003, np.amax(lons) + 0.0003, grid_space) #grid_space is the desired delta/step of the output array
    grid_lat = np.arange(np.amin(lats) - 0.0003, np.amax(lats) + 0.001, grid_space)

    OK = OrdinaryKriging(lons, lats, data, variogram_model='gaussian', verbose=True, nlags=nlags)
    z1, ss1 = OK.execute('grid', grid_lon, grid_lat)

    xintrp, yintrp = np.meshgrid(grid_lon, grid_lat)

    cs=ax.contourf(xintrp, yintrp, z1, np.linspace(420, 490, 15), cmap='blues_alpha', zorder=2)

    cs_lines = ax.contour(xintrp, yintrp, z1, np.linspace(420, 490, 15), cmap='Reds', linewidths = 0.8)

    cbar = fig.colorbar(cs)
    cbar.add_lines(cs_lines)
    cbar.ax.set_ylabel('$CO_2$ (ppm)')

def addRuler(plt, ax, length):
    lowerleft = [plt.xlim()[0], plt.ylim()[0]]
    upperright = [plt.xlim()[1], plt.ylim()[1]]



    # Calculate width by latitide
    earthCircumference = 40008000
    width = abs(1.0 * length / ((earthCircumference / 360) * math.cos(lowerleft[1] * 0.01745)))
    height = (upperright[1] - lowerleft[1]) * 0.018

    location = [plt.xlim()[1] - (plt.xlim()[1] - plt.xlim()[0]) *.05 - width, plt.ylim()[0] + (plt.ylim()[1] - plt.ylim()[0]) *.03]

    ax.add_patch(Rectangle(location, width, height, ec=(0,0,0,1), fc=(1,1,1,1)))
    ax.add_patch(Rectangle(location, width/2, height, ec=(0,0,0,1), fc=(0,0,0,1)))
    ax.annotate("0", xy=(location[0], location[1] + (1.5 * height)), ha='center')
    ax.annotate("{} m".format(length), xy=(location[0] + width, location[1] + (1.5 * height)), ha='center')

def main():
    df1data = buildReadings('csv/balloon_fiesta_gd_df2.csv')
    df2data = buildReadings('csv/balloon_fiesta_gd_df3.csv')
    df3data = buildReadings('csv/balloon_fiesta_gd_df4.csv')


    size = 530
    df1start = 1780
    df2start = 490
    df3start = 1943

    originaldf1data = df1data[df1start:]
    originaldf2data = df2data[df2start:]
    originaldf3data = df3data[df3start:]

    # size = 100
    # df1start = 2170
    # df2start = 880
    # df3start = 2333

    print len(df1data), len(df2data), len(df3data)


    df1data = df1data[df1start:df1start + size]
    df2data = df2data[df2start:df2start + size]
    df3data = df3data[df3start:df3start + size]

    print len(df1data), len(df2data), len(df3data)

    fig, ax = plt.subplots(figsize=(5, 5))
    params = {'mathtext.default': 'regular' }
    plt.rcParams.update(params)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42

    plot_flight(ax, df1data, 'C0', '-', 'dragonfly1')
    plot_flight(ax, df2data, 'C1', '--', 'dragonfly2')
    plot_flight(ax, df3data, 'C2', '-.', 'dragonfly3')


    # ax.legend()

    lmin = -106.597258
    lmax = -106.595138
    rmin = 35.193484
    rmax = 35.195758

    offset_x = 0.000408873
    offset_y = 0.0002

    scale = 0.55

    # lcenter = ((lmax + lmin) / 2)
    # rcenter = ((rmax + rmin) / 2)
    # lmin = lmin + (scale * (lmin - lcenter)) + offset_y
    # lmax = lmax + (scale * (lmax - lcenter)) + offset_y
    # rmin = rmin + (scale * (rmin - rcenter)) + offset_x
    # rmax = rmax + (scale * (rmax - rcenter)) + offset_x
    #
    # print ("scale1: {} scale2: {}").format((scale * (lmin - lcenter)), (scale * (lmax - lcenter)))
    # print ("scale1: {} scale2: {}").format((scale * (rmin - rcenter)), (scale * (rmax - rcenter)))
    #
    # print "lmin {} lmax {} rmin {} rmax {}".format(lmin, lmax, rmin, rmax)

    img = plt.imread('bfp_ortho.tif')
    ax.imshow(img, extent=[lmin, lmax, rmin, rmax])

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

    dataclip = 465
    heatmap(df1data[:dataclip] + originaldf2data[:600] + df3data[:dataclip], fig, ax, 9)

    ax.plot(-106.5960480158447, 35.195058873, marker='*', c='r',markeredgewidth=1, markeredgecolor=(0, 0, 0, 1), markersize=12, zorder=10)

    plt.xlim(-106.59647, -106.59563)
    plt.ylim(35.19415, 35.1952)

    ax.locator_params(nbins=3)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    plt.tick_params(bottom=False, left=False)

    addRuler(plt, ax, 20)
    plt.tight_layout()
    plt.savefig('Balloon_Fiesta_Gradient_Descent.pdf', dpi=300, bbox_inches='tight')

if __name__ == '__main__':
    main()
