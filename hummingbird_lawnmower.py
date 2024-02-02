#!/usr/bin/env python

# https://www.earthinversion.com/geophysics/plotting-the-geospatial-data-clipped-by-coastlines-in-python/
import argparse, datetime
import numpy as np
import pandas as pd
import math
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
from matplotlib.patches import Rectangle
import matplotlib.patheffects as path_effects
import matplotlib.ticker as ticker

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

def addRuler(plt, ax, length, height_scale):
    lowerleft = [plt.xlim()[0], plt.ylim()[0]]
    upperright = [plt.xlim()[1], plt.ylim()[1]]

    # Calculate width by latitide
    earthCircumference = 40008000
    width = abs(1.0 * length / ((earthCircumference / 360) * math.cos(lowerleft[1] * 0.01745)))
    height = (upperright[1] - lowerleft[1]) * 0.018 * height_scale

    location = [plt.xlim()[0] + (plt.xlim()[1] - plt.xlim()[0]) *.05, plt.ylim()[1] - ((plt.ylim()[1] - plt.ylim()[0]) *(.1 + (height_scale * .02)))]

    ax.add_patch(Rectangle(location, width, height, ec=(0,0,0,1), fc=(1,1,1,1), lw=height_scale))
    ax.add_patch(Rectangle(location, width/2, height, ec=(0,0,0,1), fc=(0,0,0,1), lw=height_scale))
    ax.annotate("0", xy=(location[0], location[1] + (1.5 * height)), ha='center', fontsize = 10 + (5 * height_scale))
    ax.annotate("{} m".format(length), xy=(location[0] + width, location[1] + (1.5 * height)), ha='center', fontsize = 10 + (5 * height_scale))

def heatmap(input, output, include_map, heatmap_alpha, nlags, draw_path, draw_legend, grid_margin = 0, iso_line_width = 1.8, ruler_length = 10, ruler_size = 1, offset = [0,0], clip_boundary = True, countour_res = 20, latrange = [35.82575, 35.8260], lonrange = [-106.65565, -106.65515], disable_kriging = False):

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

    lons=np.array(df['lon'])[500:]
    lats=np.array(df['lat'])[500:]
    data=np.array(df['co2'])[500:]

    lons = [l + offset[0] for l in lons]
    lats = [l + offset[1] for l in lats]

    grid_space = (max(lats) - min(lats)) / 100
    grid_lon = np.arange(np.amin(lons) - grid_margin, np.amax(lons) + grid_margin, grid_space) #grid_space is the desired delta/step of the output array
    grid_lat = np.arange(np.amin(lats) - grid_margin, np.amax(lats) + grid_margin, grid_space)

    if not disable_kriging:
        OK = OrdinaryKriging(lons, lats, data, variogram_model='gaussian', verbose=True, nlags=nlags)
        z1, ss1 = OK.execute('grid', grid_lon, grid_lat)

    xintrp, yintrp = np.meshgrid(grid_lon, grid_lat)
    fig, ax = plt.subplots(figsize=(10,4))
    params = {'mathtext.default': 'regular' }
    plt.rcParams.update(params)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42

    lmin = -106.658654
    lmax = -106.652426
    rmin = 35.824343
    rmax = 35.827756

    if include_map:
        img = plt.imread('humming_ortho_5cm_wgs84.tif')
        ax.imshow(img, extent=[lmin, lmax, rmin, rmax])
    # img2 = plt.imread('hummingbird_source_outline.png')
    # ax.imshow(img2, extent=[lmin, lmax, rmin, rmax])

    # ax.add_patch(plt.Circle((-106.65556, 35.82594), 0.000065, facecolor='none', edgecolor='r', linestyle='--', linewidth=1, zorder=2))
    # ax.add_patch(plt.Circle((-106.65540, 35.82592), 0.00005, facecolor='none', edgecolor='r', linestyle='--', linewidth=1, zorder=2))
    ax.add_patch(plt.Circle((-106.655265, 35.826025), 0.000095, facecolor='none', edgecolor='r', linestyle='--', linewidth=2, zorder=2))

    if not disable_kriging:
        cs=ax.contourf(xintrp, yintrp, z1, np.linspace(420, 500, countour_res), extend='max', cmap='blues_alpha', zorder=3)

        cs_lines = ax.contour(xintrp, yintrp, z1, np.linspace(420, 500, countour_res), cmap='Reds', linewidths = iso_line_width, zorder=3)

    # ax.clabel(cs_lines, fontsize=9, inline=True)

    if clip_boundary:
        # clip contours by polygon
        clip_vertices = [minLat(lats, lons), minLon(lats, lons), maxLat(lats, lons), maxLon(lats, lons)]
        if not disable_kriging:
            clip_map = Polygon(list(clip_vertices),fc='none',ec='k')
            ax.add_patch(clip_map)
            for collection in cs.collections:
                collection.set_clip_path(clip_map)
            for collection in cs_lines.collections:
                collection.set_clip_path(clip_map)
    else:
        ax.add_patch(Rectangle((min(lons) - grid_margin, min(lats) - grid_margin), (max(lons) - min(lons)) + (2 * grid_margin), (max(lats) - min(lats)) + (2 * grid_margin),fc='none',ec='k'))
        # print "Adding patch: {} {} {} {}".format(min(lons), min(lats), (max(lons) - min(lons)), (max(lats) - min(lats)))
        #
        # ax.plot(min(lons), min(lats), marker='X', c='k',markeredgewidth=1, markeredgecolor=(0, 0, 0, 1), markersize=10, zorder=4)



    ax.set_xlim(lonrange[0], lonrange[1])
    ax.set_ylim(latrange[0], latrange[1])
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    plt.tick_params(bottom=False, left=False)

    if draw_path:
        ax.plot(lons, lats, 'k--', lw=0.5)

    ax.plot(-106.655342, 35.825955, marker='X', c='r',markeredgewidth=1, markeredgecolor=(0, 0, 0, 1), markersize=10, zorder=4)

    # max_co2_index = max(enumerate(data), key=itemgetter(1))[0]
    # ax.plot(lons[max_co2_index], lats[max_co2_index], marker='*', c='b',markeredgewidth=1, markeredgecolor=(0, 0, 0, 1), markersize=12)
    # print "Max CO2: {}".format(data[max_co2_index])


    if draw_legend and not disable_kriging:
        def fmt(x, pos):
            return r'${}$'.format(int(x))
        cbar = fig.colorbar(cs, format=ticker.FuncFormatter(fmt))
        cbar.add_lines(cs_lines)
        cbar.ax.set_ylabel('$CO_2$ (ppm)')

    ax.locator_params(nbins=4)

    plt.tight_layout()

    # addRuler(plt, ax, ruler_length, ruler_size)

    plt.savefig(output, dpi=300, bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Convert Dragonfly log into CSV')
    parser.add_argument('--input', type=str, help='Input Dragonfly csv.')
    parser.add_argument('--output', type=str, help='Output heatmap.')
    parser.add_argument('--start', type=int, help='dataset starting index', default=None)
    parser.add_argument('--end', type=iernt, help='dataset ending index', default=None)
    parser.add_argument('--nlags', type=int, help='dataset ending index', default=6)

    args = parser.parse_args()

    disable_kriging = False

    heatmap('csv/hummingbird_1_4_2021_LAWNMOWER1.csv', 'Hummingbird_CO2_Concentration_Lawnmower1.pdf', True, 0.7, 6, False, False, 0.00002, 1.8, 10, 2, disable_kriging=disable_kriging)

    latrange = [35.82575, 35.8260]
    lonrange = [-106.65568, -106.65512]
    heatmap('csv/hummingbird_1_4_2021_LAWNMOWER2.csv', 'Hummingbird_CO2_Concentration_Lawnmower2.pdf', True, 0.7, 6, False, True, 0.00002, 1.2, 10, 1, latrange=latrange, lonrange=lonrange, disable_kriging=disable_kriging)
    offset = [0.000078, 0.000035]

    latmiddle = (35.825829 + 35.8260245) / 2
    lonmiddle = (-106.65555 + -106.65519) / 2

    lat_range = (35.82600 - 35.82587)/2


    latrange = [latmiddle - lat_range, latmiddle + lat_range]
    lonrange = [lonmiddle - (2 * lat_range), lonmiddle + (2 * lat_range)]

    heatmap('csv/hummingbird_1_4_2021_DDSA1.csv', 'Hummingbird_CO2_Concentration_DDSA.pdf', True, 0.7, 6, True, False, 0.000005, 1.2, 5, 2, offset, False, 11, latrange, lonrange, disable_kriging=disable_kriging)
