#!/usr/bin/env python

# https://www.earthinversion.com/geophysics/plotting-the-geospatial-data-clipped-by-coastlines-in-python/
import argparse, datetime
import numpy as np
import pandas as pd
from pykrige.ok import OrdinaryKriging
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def heatmap(input, output, start, end, nlags):

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

    df=pd.read_csv(input, ",")

    lons=np.array(df['lon'])
    lats=np.array(df['lat'])
    data=np.array(df['co2'])

    if start is not None and end is not None:
        lons = lons[start:end]
        lats = lats[start:end]
        data = data[start:end]

    print "{} {}".format((max(lons) - min(lons)), (max(lats) - min(lats)))

    grid_space = (max(lats) - min(lats)) / 100
    grid_lon = np.arange(np.amin(lons), np.amax(lons), grid_space) #grid_space is the desired delta/step of the output array
    grid_lat = np.arange(np.amin(lats), np.amax(lats), grid_space)

    OK = OrdinaryKriging(lons, lats, data, variogram_model='gaussian', verbose=True, nlags=nlags)
    z1, ss1 = OK.execute('grid', grid_lon, grid_lat)

    xintrp, yintrp = np.meshgrid(grid_lon, grid_lat)
    fig, ax = plt.subplots(figsize=(10,10))
    params = {'mathtext.default': 'regular' }
    plt.rcParams.update(params)

    # lmin = -106.658654
    # lmax = -106.652426
    # rmin = 35.824343
    # rmax = 35.827756
    #
    # img = plt.imread('humming_ortho_15cm_wgs84.tif')
    # ax.imshow(img, extent=[lmin, lmax, rmin, rmax])
    #
    # cs=ax.contourf(xintrp, yintrp, z1, np.linspace(min(data), max(data), 100),cmap='jet',alpha=0.5)

    lmin = -106.59838
    lmax = -106.59429
    rmin = 35.19344
    rmax = 35.19665


    img = plt.imread('balloon_fiesta.png')
    ax.imshow(img, extent=[lmin, lmax, rmin, rmax])

    cs=ax.contourf(xintrp, yintrp, z1, np.linspace(min(data), max(data) - 15, 100), cmap='blues_alpha')

    cs_lines = ax.contour(xintrp, yintrp, z1, np.linspace(min(data), max(data) - 15, 20), cmap='reds_alpha', linewidths = 0.8)

    ax.clabel(cs_lines, fontsize=9, inline=True)

    # plt.xlim(-106.6558, -106.655)
    # plt.ylim(35.8255, 35.82627)

    ax.plot(lons, lats, 'k--', lw=0.5)

    cbar = fig.colorbar(cs)
    cbar.add_lines(cs_lines)
    cbar.ax.set_ylabel('$CO_2$ (ppm)')

    ax.set_ylabel('Latitude')
    ax.set_xlabel('Longitude')
    ax.ticklabel_format(useOffset=False)

    plt.xlim(-106.5968, -106.5958)
    plt.ylim(35.1940, 35.1953)

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
