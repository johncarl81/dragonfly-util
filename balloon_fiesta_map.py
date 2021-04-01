#!/usr/bin/env python

import math
import numpy as np
import pandas as pd
from pykrige.ok import OrdinaryKriging
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
from VirtualPlume import buildco2

def addRuler(plt, ax, length):
    lowerleft = [plt.xlim()[0], plt.ylim()[0]]
    upperright = [plt.xlim()[1], plt.ylim()[1]]

    location = [plt.xlim()[0] + (plt.xlim()[1] - plt.xlim()[0]) *.05, plt.ylim()[0] + (plt.ylim()[1] - plt.ylim()[0]) *.03]

    # Calculate width by latitide
    earthCircumference = 40008000
    width = abs(1.0 * length / ((earthCircumference / 360) * math.cos(lowerleft[1] * 0.01745)))
    height = (upperright[1] - lowerleft[1]) * 0.018

    ax.add_patch(Rectangle(location, width, height, ec=(0,0,0,1), fc=(1,1,1,1)))
    ax.add_patch(Rectangle(location, width/2, height, ec=(0,0,0,1), fc=(0,0,0,1)))
    ax.annotate("0", xy=(location[0], location[1] + (1.5 * height)), ha='center')
    ax.annotate("{} m".format(length), xy=(location[0] + width, location[1] + (1.5 * height)), ha='center')

def heatmap(fig, ax, input, start = None, end = None, nlags = 6, render_axis=False, render_legend=False, wrap_data = False, max_value = 750):

    # get colormap
    ncolors = 256
    reds_color_array = plt.get_cmap('Reds')(range(ncolors))
    blues_color_array = plt.get_cmap('Blues')(range(ncolors))

    # change alpha values
    reds_color_array[:,-1] = np.linspace(0.2, 1, ncolors)
    blues_color_array[:,-1] = np.linspace(0, 1, ncolors)

    # create a colormap object
    reds_map_object = LinearSegmentedColormap.from_list(name='reds_alpha',colors=reds_color_array)
    plt.register_cmap(cmap=reds_map_object)
    blues_map_object = LinearSegmentedColormap.from_list(name='blues_alpha',colors=blues_color_array)
    plt.register_cmap(cmap=blues_map_object)

    df=pd.read_csv(input, ",")

    lons=np.array(df['lon'])
    lats=np.array(df['lat'])
    data = buildco2(lons, lats)

    if start is not None and end is not None:
        lons = lons[start:end]
        lats = lats[start:end]
        data = buildco2(lons, lats)

    grid_space = (max(lats) - min(lats)) / 100
    grid_lon = np.arange(np.amin(lons), np.amax(lons), grid_space) #grid_space is the desired delta/step of the output array
    grid_lat = np.arange(np.amin(lats) - 0.0003, np.amax(lats), grid_space)

    OK = OrdinaryKriging(lons, lats, data, variogram_model='gaussian', verbose=True, nlags=nlags)
    z1, ss1 = OK.execute('grid', grid_lon, grid_lat)

    xintrp, yintrp = np.meshgrid(grid_lon, grid_lat)

    lmin = -106.597258
    lmax = -106.595138
    rmin = 35.193484
    rmax = 35.195758

    img = plt.imread('bfp_ortho.tif')
    ax.imshow(img, extent=[lmin, lmax, rmin, rmax])

    cs=ax.contourf(xintrp, yintrp, z1, np.linspace(420, 750, 100), extend='max', cmap='blues_alpha')

    cs_lines = ax.contour(xintrp, yintrp, z1, np.linspace(450, max_value, 10), cmap='Reds', linewidths = 0.8)

    print min(lons), max(lons), min(lats), max(lats)

    if wrap_data:
        plt.xlim(min(lons), max(lons))
        plt.ylim(min(lats), max(lats))
    else:
        plt.xlim(-106.5967, -106.59575)
        plt.ylim(35.19405, 35.19515)

    ax.plot(lons, lats, 'k--', lw=0.5)


    def fmt(x, pos):
        return r'${}$'.format(int(x))

    if render_legend:
        cbar = fig.colorbar(cs, format=ticker.FuncFormatter(fmt))
        cbar.add_lines(cs_lines)
        cbar.ax.set_ylabel('$CO_2$ (ppm)')

    if render_axis:
        ax.set_ylabel('Latitude')
        ax.set_xlabel('Longitude')
        plt.yticks(rotation='vertical')
        ax.locator_params(nbins=3)
        ax.ticklabel_format(useOffset=False)
    else:
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        plt.tick_params(bottom=False, left=False)

    ax.plot(-106.59625, 35.19466, marker='*', c='r',markeredgewidth=1, markeredgecolor=(0, 0, 0, 1), markersize=12)

if __name__ == '__main__':
    fig, ax = plt.subplots(figsize=(5, 4.5))

    params = {'mathtext.default': 'regular' }
    plt.rcParams.update(params)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42

    heatmap(fig, ax, 'csv/balloon_fiesta_lawnmower.csv', render_axis=False, render_legend=True, wrap_data = False)
    addRuler(plt, ax, 20)

    minx = -106.5963623
    maxx = -106.5961441
    miny = 35.1945146
    maxy = 35.1947016

    ax.add_patch(Rectangle((minx, miny), (maxx - minx), (maxy - miny), 1, ec=(0,0,0,1), fc=(0,0,0,0 ), ls='-.'))
    # ax.text(minx - 0.000003, maxy + 0.00001, 'DDSA (See Detail)')

    left, bottom, width, height = [0.48, 0.12, 0.25, 0.25]
    ax2 = fig.add_axes([left, bottom, width, height], xticks=[], yticks=[])
    heatmap(fig, ax2, 'csv/balloon_fiesta_ddsa.csv', 190, 2100, 10, render_axis=False, render_legend=False, wrap_data = True, max_value = 2500)


    plt.tight_layout()
    plt.savefig('Balloon_Fiesta.pdf', dpi=300,bbox_inches='tight')
