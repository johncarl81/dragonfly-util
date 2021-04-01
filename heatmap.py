#!/usr/bin/env python

# https://www.earthinversion.com/geophysics/plotting-the-geospatial-data-clipped-by-coastlines-in-python/
import argparse, datetime
import numpy as np
import pandas as pd
from pykrige.ok import OrdinaryKriging
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from operator import itemgetter

def heatmap(input, output, start, end, nlags):

    df=pd.read_csv(input, ", ")

    lons=np.array(df['lon'])
    lats=np.array(df['lat'])
    data=np.array(df['co2'])

    print len(lons)

    if start is not None and end is not None:
        lons = lons[start:end]
        lats = lats[start:end]
        data = data[start:end]

    # lons = lons[0::3]
    # lats = lats[0::3]
    # data = data[0::3]

    print "{} {}".format((max(lons) - min(lons)), (max(lats) - min(lats)))

    grid_space = (max(lats) - min(lats)) / 100
    grid_lon = np.arange(np.amin(lons) - 0.000002, np.amax(lons) + 0.000002, grid_space) #grid_space is the desired delta/step of the output array
    grid_lat = np.arange(np.amin(lats) - 0.000002, np.amax(lats) + 0.000002, grid_space)

    OK = OrdinaryKriging(lons, lats, data, variogram_model='linear', verbose=True, nlags=nlags)
    z1, ss1 = OK.execute('grid', grid_lon, grid_lat)

    xintrp, yintrp = np.meshgrid(grid_lon, grid_lat)
    fig, ax = plt.subplots(figsize=(6, 4))
    params = {'mathtext.default': 'regular' }
    plt.rcParams.update(params)

    cs=ax.contourf(xintrp, yintrp, z1, np.linspace(420, 500, 20), extend='max', cmap='Blues')

    cs_lines = ax.contour(xintrp, yintrp, z1, np.linspace(420, 500, 20), cmap='Reds', linewidths = 0.9)

    ax.plot(-106.655342 - 0.000078, 35.825955 - 0.000035, marker='X', c='r', markeredgewidth=1, markeredgecolor=(0, 0, 0, 1), markersize=10)

    max_co2_index = max(enumerate(data), key=itemgetter(1))[0]
    # ax.plot(lons[max_co2_index], lats[max_co2_index], marker='*', c='b',markeredgewidth=1, markeredgecolor=(0, 0, 0, 1), markersize=12)
    print "Max CO2: {}".format(data[max_co2_index])

    # cs_lines = ax.contour(xintrp, yintrp, z1, np.linspace(min(data), max(data) - 15, 20), cmap='reds_alpha', linewidths = 0.8)

    # ax.clabel(cs_lines, fontsize=9, inline=True)

    # plt.xlim(-106.6558, -106.655)
    # plt.ylim(35.8255, 35.82627)

    ax.plot(lons, lats, 'k--', lw=0.5)

    cbar = fig.colorbar(cs)
    cbar.add_lines(cs_lines)
    cbar.ax.set_ylabel('$CO_2$ (ppm)')

    ax.set_ylabel('Latitude')
    ax.set_xlabel('Longitude')
    ax.ticklabel_format(useOffset=False)

    # plt.xlim(min(lons), max(lons))
    # plt.ylim(min(lats), max(lats))

    plt.tight_layout()
    plt.savefig(output,dpi=300,bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Convert Dragonfly log into CSV')
    parser.add_argument('--input', type=str, help='Input Dragonfly csv.')
    parser.add_argument('--output', type=str, help='Output heatmap.')
    parser.add_argument('--start', type=int, help='dataset starting index', default=None)
    parser.add_argument('--end', type=int, help='dataset ending index', default=None)
    parser.add_argument('--nlags', type=int, help='dataset ending index', default=6)

    args = parser.parse_args()

    heatmap(args.input, args.output, args.start, args.end, args.nlags)
