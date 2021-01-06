#!/usr/bin/env python

# https://www.earthinversion.com/geophysics/plotting-the-geospatial-data-clipped-by-coastlines-in-python/
import argparse, datetime
import numpy as np
import pandas as pd
import glob
from pykrige.ok import OrdinaryKriging
from pykrige.kriging_tools import write_asc_grid
import pykrige.kriging_tools as kt
import matplotlib.pyplot as plt
# from mpl_toolkits.basemap import Basemap
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Path, PathPatch

# datetime.datetime.strptime("{} {}".format(lineparts[0], lineparts[1]), '%Y-%m-%d %H:%M:%S.%f')

def heatmap(input, output):

    df=pd.read_csv(input, ", ")

    lons=np.array(df['lon'])
    lats=np.array(df['lat'])
    data=np.array(df['co2'])

    grid_space = (max(lons) - min(lons)) / 100
    grid_lon = np.arange(np.amin(lons), np.amax(lons), grid_space) #grid_space is the desired delta/step of the output array
    grid_lat = np.arange(np.amin(lats), np.amax(lats), grid_space)

    OK = OrdinaryKriging(lons, lats, data, variogram_model='gaussian', verbose=True, enable_plotting=False,nlags=10)
    z1, ss1 = OK.execute('grid', grid_lon, grid_lat)

    xintrp, yintrp = np.meshgrid(grid_lon, grid_lat)
    fig, ax = plt.subplots(figsize=(10,10))

    cs=ax.contourf(xintrp, yintrp, z1, np.linspace(min(data), max(data), 100),extend='both',cmap='jet')

    ax.plot(lons, lats, 'k--')

    cbar = fig.colorbar(cs)
    cbar.ax.set_ylabel('CO2 PPM')

    plt.savefig(output,dpi=300,bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Convert Dragonfly log into CSV')
    parser.add_argument('--input', type=str, help='Input Dragonfly csv.')
    parser.add_argument('--output', type=str, help='Output heatmap.')
    args = parser.parse_args()

    heatmap(args.input, args.output)
