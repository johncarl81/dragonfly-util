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

    return [lons[minIndex], lats[minIndex]]

def minLon(lats, lons):
    minIndex = min(enumerate(lons), key=itemgetter(1))[0]

    return [lons[minIndex], lats[minIndex]]

def maxLat(lats, lons):
    minIndex = max(enumerate(lats), key=itemgetter(1))[0]

    return [lons[minIndex], lats[minIndex]]

def maxLon(lats, lons):
    minIndex = max(enumerate(lons), key=itemgetter(1))[0]

    return [lons[minIndex], lats[minIndex]]

def heatmap(input, output, nlags):

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
    fig, ax = plt.subplots(figsize=(10,10))

    lmin = -106.658654
    lmax = -106.652426
    rmin = 35.824343
    rmax = 35.827756

    img = plt.imread('humming_ortho_15cm_wgs84.tif')
    ax.imshow(img, extent=[lmin, lmax, rmin, rmax])

    cs=ax.contourf(xintrp, yintrp, z1, np.linspace(min(data), max(data), 100),extend='both', cmap='jet', alpha=0.5)

    # clip contours by polygon
    clip_vertices = [minLat(lats, lons), minLon(lats, lons), maxLat(lats, lons), maxLon(lats, lons)]
    clip_map = Polygon(list(clip_vertices),fc='#EEEEEE00',ec='none')
    ax.add_patch(clip_map)
    for collection in cs.collections:
        collection.set_clip_path(clip_map)

    plt.xlim(-106.6558, -106.655)
    plt.ylim(35.8255, 35.82627)

    ax.plot(lons, lats, 'k--')

    cbar = fig.colorbar(cs)
    cbar.ax.set_ylabel('CO2 PPM')

    ax.set_ylabel('Latitude')
    ax.set_xlabel('Longitude')
    ax.ticklabel_format(useOffset=False)

    plt.savefig(output, dpi=300, bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Convert Dragonfly log into CSV')
    parser.add_argument('--input', type=str, help='Input Dragonfly csv.')
    parser.add_argument('--output', type=str, help='Output heatmap.')
    parser.add_argument('--start', type=int, help='dataset starting index', default=None)
    parser.add_argument('--end', type=int, help='dataset ending index', default=None)
    parser.add_argument('--nlags', type=int, help='dataset ending index', default=6)

    args = parser.parse_args()

    heatmap('csv/hummingbird_1_4_2021_LAWNMOWER1.csv', 'Hummingbird_CO2_Concentration.png', 6)
