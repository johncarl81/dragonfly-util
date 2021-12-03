#!/usr/bin/env python

import datetime
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.ticker import FormatStrFormatter
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from pandas.plotting import register_matplotlib_converters
from pykrige.ok import OrdinaryKriging
from scipy.spatial import ConvexHull
import matplotlib.ticker as ticker

from .mplogtocsv import parse_mplog

register_matplotlib_converters()


def load_csv(csv_file):
    df = pd.read_csv(csv_file, ', ', engine='python')

    lons = np.array(df['lon'])
    lats = np.array(df['lat'])
    data = np.array(df['co2'])

    return [lons, lats, data]

def add_ruler(plt, ax, length, height_scale):
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

def geo_axis_format(ax):
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.tick_params(bottom=False, left=False)

def display_path(csv_file, ortho_map):
    fig, ax = plt.subplots(figsize=(10, 5))
    ortho_map.plot(plt, ax)

    # Load CSV data
    [lons, lats, data] = load_csv(csv_file)

    ax.plot(lons, lats, 'k--', lw=1)

    geo_axis_format(ax)
    ax.plot()

def zoom_to_altitude_data(ax, data):
    max_alt = 0
    min_alt = 100000
    max_lon = -360
    min_lon = 360
    for d in data:
        max_alt = max(max_alt, d.alt)
        min_alt = min(min_alt, d.alt)
        max_lon = max(max_lon, d.lon)
        min_lon = min(min_lon, d.lon)

    dalt = max_alt - min_alt
    dlon = max_lon - min_lon
    lat_margin_scale = 0.1
    lon_margin_scale = 0.5
    minimum_size = 0.001

    dalt = max(dalt, minimum_size)
    dlon = max(dlon, minimum_size)

    ax.set_xlim(min_lon - (lon_margin_scale * dlon), max_lon + (lon_margin_scale * dlon))
    ax.set_ylim(min_alt - (lat_margin_scale * dalt), max_alt + (lat_margin_scale * dalt))

def zoom_to_data(ax, data):
    max_lat = -360
    min_lat = 360
    max_lon = -360
    min_lon = 360
    for d in data:
        max_lat = max(max_lat, d.lat)
        min_lat = min(min_lat, d.lat)
        max_lon = max(max_lon, d.lon)
        min_lon = min(min_lon, d.lon)

    dlat = max_lat - min_lat
    dlon = max_lon - min_lon
    lat_margin_scale = 0.1
    lon_margin_scale = 0.1
    minimum_size = 0.001

    dlat = max(max(dlat, dlon), minimum_size)
    dlon = max(dlat, dlon)

    ax.set_xlim(min_lon - (lon_margin_scale * dlon), max_lon + (lon_margin_scale * dlon))
    ax.set_ylim(min_lat - (lat_margin_scale * dlat), max_lat + (lat_margin_scale * dlat))


def find_max_distance(reference_point, data):
    max_point = reference_point
    max_distance = 0

    for d in data:
        distance = d.distance(reference_point)
        if distance > max_distance:
            max_distance = distance
            max_point = d

    return max_point


def plot_maps(fig, ax, ortho_maps):
    for ortho_map in ortho_maps:
        ortho_map.plot(plt, ax)


def plot_data_path(ax, data):
    ax.plot([d.lon for d in data], [d.lat for d in data], 'k--', lw=1)


def display_data_path(data, ortho_maps):
    fig, ax = plt.subplots(figsize=(16, 6))

    plot_maps(fig, ax, ortho_maps)
    plot_data_path(ax, data)

    zoom_to_data(ax, data)

    geo_axis_format(ax)
    ax.plot()


def save_data_path(data, ortho_maps, filename):
    fig, ax = plt.subplots(figsize=(16, 6))

    plot_maps(fig, ax, ortho_maps)
    plot_data_path(ax, data)

    zoom_to_data(ax, data)

    geo_axis_format(ax)
    plt.savefig(filename, dpi=300, bbox_inches='tight')


def plot_data_altitude(ax, data):
    ax.plot([d.time for d in data], [d.alt for d in data])

    ax.set_xlabel('Time')

    ax.set_ylabel('Altitude')



def display_data_altitude(data):
    fig, ax = plt.subplots(figsize=(16, 6))

    plot_data_altitude(ax, data)

    ax.plot()

krige_data = {}

def plot_krige(name, fig, ax, lons, lats, data, nlags=6, minco2=None, maxco2=None, legend=True):

    # get colormap
    ncolors = 256
    reds_color_array = plt.get_cmap('Reds')(range(ncolors))
    blues_color_array = plt.get_cmap('Blues')(range(ncolors))

    # change alpha values
    reds_color_array[:,-1] = np.linspace(0.2, 1, ncolors)
    blues_color_array[:,-1] = np.linspace(0.3, 1, ncolors)

    # create a colormap object
    reds_map_object = LinearSegmentedColormap.from_list(name='reds_alpha',colors=reds_color_array)
    plt.register_cmap(cmap=reds_map_object)
    blues_map_object = LinearSegmentedColormap.from_list(name='blues_alpha',colors=blues_color_array)
    plt.register_cmap(cmap=blues_map_object)

    grid_margin = 0.00002

    lat_grid_space = (max(lats) - min(lats)) / 100
    lon_grid_space = (max(lons) - min(lons)) / 100
    grid_lon = np.arange(np.amin(lons) - grid_margin, np.amax(lons) + grid_margin, lon_grid_space)  # grid_space is the desired delta/step of the output array
    grid_lat = np.arange(np.amin(lats) - grid_margin, np.amax(lats) + grid_margin, lat_grid_space)

    if(name in krige_data.keys()):
        z1 = krige_data[name]
    else:
        OK = OrdinaryKriging(lons, lats, data, nlags=nlags)
        z1, ss1 = OK.execute('grid', grid_lon, grid_lat)
        krige_data[name] = z1

    xintrp, yintrp = np.meshgrid(grid_lon, grid_lat)

    maximum = max(map(max, *z1)) if maxco2 is None else maxco2
    minimum = min(map(min, *z1)) if minco2 is None else minco2

    cs = ax.contourf(xintrp, yintrp, z1, np.linspace(minimum, maximum, 100), extend='max', cmap='blues_alpha')

    cs_lines = ax.contour(xintrp, yintrp, z1, np.linspace(minimum, maximum, 15), cmap='Reds', linewidths = 0.8)

    points = []
    for i in range(len(lons)):
        points.append([lons[i], lats[i]])
    #points = np.array(zip(lons, lats))
    points = np.array(points)
    hull = ConvexHull(points)

    hullPoints = [points[v] for v in hull.vertices]

    clippath = Path(hullPoints)
    patch = PathPatch(clippath, facecolor='none', ec='none')
    ax.add_patch(patch)
    for c in cs.collections:
        c.set_clip_path(patch)

    for c in cs_lines.collections:
        c.set_clip_path(patch)

    def fmt(x, pos):
        if minco2 is None or maxco2 is None:
            return r'${:.1f}$'.format(x)
        return r'${:.1f}$'.format((x - minco2) / (maxco2 - minco2))

    if legend:
        cbar = fig.colorbar(cs, format=ticker.FuncFormatter(fmt))
        cbar.add_lines(cs_lines)
        cbar.ax.set_ylabel('Normalized $CO_2$ Over Ambient')

def display_krige(name, csv_file, ortho_map, nlags=6):
    fig, ax = plt.subplots(figsize=(16, 6))
    ortho_map.plot(plt, ax)

    # Load CSV data
    [lons, lats, data] = load_csv(csv_file)

    plot_krige(name, ax, lons, lats, data, nlags)

    geo_axis_format(ax)
    ax.plot()


def display_readings_krige(name, readings, ortho_maps, nlags=6, minco2=None, maxco2=None, addons=None):
    fig, ax = plt.subplots(figsize=(16, 6))

    plot_maps(fig, ax, ortho_maps)

    plot_krige(name, fig, ax, [r.lon for r in readings], [r.lat for r in readings], [r.value for r in readings], nlags, minco2, maxco2)

    zoom_to_data(ax, readings)
    geo_axis_format(ax)

    if addons is not None:
        addons(plt, fig, ax)

    ax.plot()


def save_readings_krige(name, readings, ortho_maps, filename, nlags=6):
    fig, ax = plt.subplots(figsize=(16, 6))

    plot_maps(fig, ax, ortho_maps)

    plot_krige(name, fig, ax, [r.lon for r in readings], [r.lat for r in readings], [r.value for r in readings], nlags)

    zoom_to_altitude_data(ax, readings)
    geo_axis_format(ax)
    plt.savefig(filename, dpi=300, bbox_inches='tight')


def display_altitude_readings_krige(name, readings, nlags=6):
    fig, ax = plt.subplots(figsize=(16, 6))

    plot_krige(name, fig, ax, [r.lon * 40008000 / 360  for r in readings], [r.alt for r in readings], [r.value for r in readings], nlags)

    ax.set_xlabel('Distance')
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.set_ylabel('Altitude (m)')

    ax.plot()


def save_altitude_readings_krige(name, readings, filename, nlags=6):
    fig, ax = plt.subplots(figsize=(16, 6))

    plot_krige(name, fig, ax, [r.lon * 40008000 / 360 for r in readings], [r.alt for r in readings], [r.value for r in readings], nlags)

    zoom_to_data(ax, readings)
    ax.set_xlabel('Longitude')
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.set_ylabel('Altitude (m)')
    plt.savefig(filename, dpi=300, bbox_inches='tight')


def filter_zero(data):
    filtered = []
    for d in data:
        if d.lat != 0 and d.lon != 0:
            filtered.append(d)
    return filtered

def display_maps(maps):
    fig, ax = plt.subplots(figsize=(15, 30))
    plot_maps(fig, ax, maps)

    geo_axis_format(ax)
    ax.plot()

def plot_readings(fig, ax, readings):
    ax.plot([r.time for r in readings], [r.value for r in readings])

    ax.set_xlabel('Time')
    ax.set_ylabel('CO2 PPM')


def display_readings(readings):
    fig, ax = plt.subplots(figsize=(16, 6))

    plot_readings(fig, ax, readings)

    ax.plot()


def plot_scatter(fig, ax, readings, draw_path):
    min_reading = min([r.value for r in readings])
    max_reading = max([r.value for r in readings])
#    values = [2000 * ((r.value - min_reading) / (max_reading - min_reading)) ** 2 for r in readings]
    values = [1.0 * r.value for r in readings]
#[(r.value - min_reading) / (max_reading - min_reading) for r in readings]
    ax.autoscale(False)
    sc = ax.scatter([r.lon for r in readings],
                    [r.lat for r in readings],
                    c=values,
                    marker='o')

    if draw_path:
        ax.plot([r.lon for r in readings],
                [r.lat for r in readings],
                'k--',
                label='parametric curve 1')

    ax.set_xlabel('Longitude')
    ax.set_xlim(min([r.lon for r in readings]), max([r.lon for r in readings]))


    ax.set_ylabel('Latitude')
    ax.set_ylim(min([r.lat for r in readings]), max([r.lat for r in readings]))

    fig.colorbar(sc)

#    max_size = 5
#    legendCircles = []
#    legendNames = []
#    for i in range(0, max_size):
#        legendCircles.append(Line2D([0], [0], marker="o", alpha=0.4, markersize=i * 10))
#        legendNames.append("{}ppm".format(int(min_reading + ((1.0 * i / max_size) * (max_reading - min_reading)))))
#
#    fig.legend(legendCircles, legendNames, numpoints=1)
    fig.legend()

def plot_altitude_scatter(fig, ax, readings):
    min_reading = min([r.value for r in readings])
    max_reading = max([r.value for r in readings])
#    values = [2000 * ((r.value - min_reading) / (max_reading - min_reading)) ** 2 for r in readings]
    values = [1.0 * r.value for r in readings]
    ax.autoscale(False)
    sc = ax.scatter([r.lon for r in readings],
                    [r.alt for r in readings],
                    c=values,
                    marker='o')
    ax.plot([r.lon for r in readings],
            [r.lat for r in readings],
            'k--',
            label='parametric curve 1')
    ax.legend()

    ax.set_xlabel('Longitude')
    ax.set_xlim(min([r.lon for r in readings]), max([r.lon for r in readings]))


    ax.set_ylabel('Altitude (m)')
    ax.set_ylim(min([r.alt for r in readings]), max([r.alt for r in readings]))


    fig.colorbar(sc)

#    max_size = 5
#    legendCircles = []
#    legendNames = []
#    for i in range(0, max_size):
#        legendCircles.append(Line2D([0], [0], marker="o", alpha=0.4, markersize=i * 10))
#        legendNames.append("{}ppm".format(int(min_reading + ((1.0 * i / max_size) * (max_reading - min_reading)))))
#
#    fig.legend(legendCircles, legendNames, numpoints=1)

def plot_altitude_reading_scatter(fig, ax, readings):
    minimum_alt = int(min([r.alt for r in readings]))

    ax.scatter([r.alt - minimum_alt for r in readings],
               [r.value for r in readings],
               s=1,
               marker='o')

    ax.set_ylabel('CO2 PPM')
    ax.set_xlabel("Altitude (relative to {}m)".format(minimum_alt))

def display_altitude_reading_scatter(readings):
    fig, ax = plt.subplots(figsize=(16, 6))
    plot_altitude_reading_scatter(fig, ax, readings)

    ax.plot()


def display_scatter(readings, maps, draw_path=True):
    fig, ax = plt.subplots(figsize=(16, 6))
    plot_maps(fig, ax, maps)
    plot_scatter(fig, ax, readings, draw_path)

    zoom_to_data(ax, readings)
    geo_axis_format(ax)

    ax.plot()

def save_scatter(readings, maps, filename, draw_path=True):
    fig, ax = plt.subplots(figsize=(16, 6))
    plot_maps(fig, ax, maps)
    plot_scatter(fig, ax, readings, draw_path)

    zoom_to_data(ax, readings)
    geo_axis_format(ax)

    plt.savefig(filename, dpi=300, bbox_inches='tight')

def display_altitude_scatter(readings):
    fig, ax = plt.subplots(figsize=(16, 6))
    plot_altitude_scatter(fig, ax, readings)

    ax.set_xlabel('Longitude')
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.set_ylabel('Altitude (m)')
    ax.plot()
