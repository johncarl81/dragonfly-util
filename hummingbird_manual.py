#!/usr/bin/env python

# https://www.earthinversion.com/geophysics/plotting-the-geospatial-data-clipped-by-coastlines-in-python/
import argparse, datetime
import numpy as np
import pandas as pd
import glob
from pykrige.ok import OrdinaryKriging
from matplotlib.patches import Polygon
from pykrige.kriging_tools import write_asc_grid
import pykrige.kriging_tools as kt
import matplotlib.pyplot as plt
# from mpl_toolkits.basemap import Basemap
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Path, PathPatch
from operator import itemgetter

# datetime.datetime.strptime("{} {}".format(lineparts[0], lineparts[1]), '%Y-%m-%d %H:%M:%S.%f')

def minLat(lats, lons):
    minIndex = min(enumerate(lats), key=itemgetter(1))[0]

    return [lons[minIndex] - 0.000005, lats[minIndex] - 0.000005]

def minLon(lats, lons):
    minIndex = min(enumerate(lons), key=itemgetter(1))[0]

    return [lons[minIndex] - 0.000005, lats[minIndex] + 0.000005]

def maxLat(lats, lons):
    maxIndex = max(enumerate(lats), key=itemgetter(1))[0]

    return [lons[maxIndex] + 0.000005, lats[maxIndex] +  0.000005]

def maxLon(lats, lons):
    maxIndex = max(enumerate(lons), key=itemgetter(1))[0]

    return [lons[maxIndex] + 0.000005, lats[maxIndex] - 0.000005]

def heatmap(input, output, nlags):

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

    df=pd.read_csv(input, ", ")

    lons=np.array(df['lon'])
    lats=np.array(df['lat'])
    data=np.array(df['co2'])

    grid_space = (max(lats) - min(lats)) / 100
    grid_lon = np.arange(np.amin(lons), np.amax(lons), grid_space) #grid_space is the desired delta/step of the output array
    grid_lat = np.arange(np.amin(lats), np.amax(lats), grid_space)

    OK = OrdinaryKriging(lons, lats, data, variogram_model='gaussian', verbose=True, nlags=nlags)
    z1, ss1 = OK.execute('grid', grid_lon, grid_lat)

    xintrp, yintrp = np.meshgrid(grid_lon, grid_lat)
    fig, ax = plt.subplots(figsize=(12,4))
    params = {'mathtext.default': 'regular' }
    plt.rcParams.update(params)

    lmin = -106.658654
    lmax = -106.652426
    rmin = 35.824343
    rmax = 35.827756

    img = plt.imread('humming_ortho_5cm_wgs84.tif')
    ax.imshow(img, extent=[lmin, lmax, rmin, rmax])
    # img2 = plt.imread('hummingbird_source_outline.png')
    # ax.imshow(img2, extent=[lmin, lmax, rmin, rmax])

    cs=ax.contourf(xintrp, yintrp, z1, np.linspace(420, max(data), 100), cmap='jet', alpha=0.5)

    # cs_lines = ax.contour(xintrp, yintrp, z1, np.linspace(min(data), max(data), 15), cmap='Reds', linewidths = 0.8)

    # ax.clabel(cs_lines, fontsize=6, inline=1)

    # clip contours by polygon
    clip_vertices = [minLat(lats, lons), minLon(lats, lons), maxLat(lats, lons), maxLon(lats, lons)]
    clip_map = Polygon(list(clip_vertices),fc='#EEEEEE00',ec='none')
    ax.add_patch(clip_map)
    # for collection in cs.collections:
    #     collection.set_clip_path(clip_map)
    # for collection in cs_lines.collections:
    #     collection.set_clip_path(clip_map)

    # plt.xlim(min(lons), max(lons))
    # plt.ylim(min(lats), max(lats))

    plt.xlim(-106.6557, -106.6551)
    plt.ylim(35.82575, 35.82602)

    ax.plot(lons, lats, 'k--', lw=0.5)

    ax.plot(-106.655342, 35.825955, marker='*', c='r',markeredgewidth=1, markeredgecolor=(0, 0, 0, 1), markersize=12)


    cbar = fig.colorbar(cs)
    # cbar.add_lines(cs_lines)

    plt.yticks(rotation=90)
    ax.locator_params(nbins=4)
    cbar.ax.set_ylabel('$CO_2$ (ppm)')


    ax.set_ylabel('Latitude')
    ax.set_xlabel('Longitude')
    ax.ticklabel_format(useOffset=False)
    plt.tight_layout()

    plt.savefig(output, dpi=300, bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Convert Dragonfly log into CSV')
    parser.add_argument('--input', type=str, help='Input Dragonfly csv.')
    parser.add_argument('--output', type=str, help='Output heatmap.')
    parser.add_argument('--start', type=int, help='dataset starting index', default=None)
    parser.add_argument('--end', type=int, help='dataset ending index', default=None)
    parser.add_argument('--nlags', type=int, help='dataset ending index', default=6)

    args = parser.parse_args()

    heatmap('csv/hummingbird_manual_06_10_2020.csv', 'Hummingbird_Baseline_Manual.pdf', 6)
