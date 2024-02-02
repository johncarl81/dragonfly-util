#!/usr/bin/env python

import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

VIRTUAL_SOURCE = dotdict({
    "latitude": 35.19468,
    "longitude": -106.59625
})

def differenceInMeters(one, two):
    earthCircumference = 40008000
    return [
        ((one.longitude - two.longitude) * (earthCircumference / 360) * math.cos(one.latitude * 0.01745)),
        ((one.latitude - two.latitude) * (earthCircumference / 360))
    ]

def calculateCO2(position):


    [y, x] = differenceInMeters(position, VIRTUAL_SOURCE)

    if x >= 0 :
        return 420

    Q = 50000
    K = 2
    H = 2
    u = 1

    value = (Q / (2 * math.pi * K * -x)) * math.exp(- (u * ((pow(y, 2) + pow(H, 2))) / (4 * K * -x)))

    if value < 0:
        return 420
    else:
        return 420 + value

def buildco2(x, y):
    values = []
    for i in range(len(x)):
        values.append(calculateCO2(dotdict({"longitude": float(x[i]), "latitude": float(y[i])})))
    return values

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

def heatmap(fig, ax, start = None, end = None, render_axis=False, render_legend=False, wrap_data = False, max_value = 750):

    # get colormap
    ncolors = 256
    reds_color_array = plt.get_cmap('Reds')(range(ncolors))
    blues_color_array = plt.get_cmap('Blues')(range(ncolors))

    # change alpha values
    reds_color_array[:,-1] = np.linspace(0, 1, ncolors)
    blues_color_array[:,-1] = np.linspace(0, 1, ncolors)

    # create a colormap object
    if 'reds_alpha' not in plt.colormaps():
        reds_map_object = LinearSegmentedColormap.from_list(name='reds_alpha',colors=reds_color_array)
        plt.register_cmap(cmap=reds_map_object)
    if 'blues_alpha' not in plt.colormaps():
        blues_map_object = LinearSegmentedColormap.from_list(name='blues_alpha',colors=blues_color_array)
        plt.register_cmap(cmap=blues_map_object)

    lmin = -106.597258
    lmax = -106.595138
    rmin = 35.193484
    rmax = 35.195758

    grid_space = (lmax - lmin) / 1000
    grid_lon = np.arange(lmin, lmax, grid_space) #grid_space is the desired delta/step of the output array
    grid_lat = np.arange(rmin, rmax, grid_space)

    xintrp, yintrp = np.meshgrid(grid_lon, grid_lat)

    @np.vectorize
    def func(x,y):
        # some arbitrary function
        return calculateCO2(dotdict({"longitude": float(x), "latitude": float(y)}))

    data = func(xintrp, yintrp)

    img = plt.imread('bfp_ortho.tif')
    ax.imshow(img, extent=[lmin, lmax, rmin, rmax])

    cs=ax.contourf(xintrp, yintrp, data, np.linspace(420, 750, 100), extend='max', cmap='blues_alpha')

    cs_lines = ax.contour(xintrp, yintrp, data, np.linspace(460, 1200, 10), cmap='Reds', linewidths = 0.8)


    plt.xlim(-106.5967, -106.59575)
    plt.ylim(35.19405, 35.19515)


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

    # scalebar = ScaleBar(0.2) # 1 pixel = 0.2 meter
    # plt.gca().add_artist(scalebar)

    addRuler(plt, ax, 20)

    ax.plot(-106.59625, 35.19466, marker='*', c='r',markeredgewidth=1, markeredgecolor=(0, 0, 0, 1), markersize=12)

if __name__ == '__main__':
    fig, ax = plt.subplots(figsize=(5, 4.5))

    params = {'mathtext.default': 'regular' }
    plt.rcParams.update(params)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42

    heatmap(fig, ax, render_axis=False, render_legend=True, wrap_data = False)

    plt.tight_layout()
    plt.savefig('Balloon_Fiesta_Virtual_Plume_Final.pdf', dpi=300,bbox_inches='tight')
