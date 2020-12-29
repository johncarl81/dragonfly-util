#!/usr/bin/env python

import argparse, math
from enum import Enum
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt

class Reading:
    def __init__(self, value, lat, lon, alt):
        self.value = float(value)
        self.lat = float(lat)
        self.lon = float(lon)
        self.alt = float(alt)

    def add(self, latadd, lonadd):
        return Reading(self.value, self.lat + latadd, self.lon + lonadd, self.alt)

def buildKmlHeader():
    return '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.0"> <Document>
'''
def buildKmlFooter():
    return '</Document> </kml>'

def buildEntry(reading):
    return "{},{},{}\n".format(reading.lon, reading.lat, reading.alt)

def buildLine(readings, outputFile):
    outputFile.write('''<Placemark>
                    <LineString>
                        <altitudeMode>absolute</altitudeMode>
                        <coordinates>
                        ''')
    for reading in readings:
        outputFile.write(buildEntry(reading))
    outputFile.write('''</coordinates>
                    </LineString>
                    <Style> 
                      <LineStyle>  
                       <color>#ffffffff</color>
                       <width>2</width>
                      </LineStyle> 
                     </Style>
                </Placemark>
                ''')


def hexReading(minreading, maxreading, value):
    magnitude = (value - minreading) / (maxreading - minreading)
    return '{0:02x}'.format(int(magnitude * 255))


def buildPoints(readings, outputFile):
    radius = 0.000004
    i = 0
    minreading = min(reading.value for reading in readings)
    maxreading = max(reading.value for reading in readings)
    print "min: {} max: {}".format(minreading, maxreading)
    for reading in readings:
        hexreading = hexReading(minreading, maxreading, reading.value)
        outputFile.write('''<Placemark>
      <name>ppm: {} @ 512</name>
      <Polygon>
        <altitudeMode>absolute</altitudeMode>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
            '''.format(reading.value, i))

        outputFile.write(buildEntry(reading.add(radius, radius)))
        outputFile.write(buildEntry(reading.add(radius, -radius)))
        outputFile.write(buildEntry(reading.add(-radius, -radius)))
        outputFile.write(buildEntry(reading.add(-radius, radius)))
        outputFile.write(buildEntry(reading.add(radius, radius)))

        outputFile.write('''
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
     <Style> 
      <PolyStyle>  
       <color>#ffff{}{}</color>
      <outline>0</outline>
      </PolyStyle> 
     </Style>
    </Placemark>
    '''.format(hexreading, hexreading))

        i = i+1

def buildReadings(input, skipZeroing):
    readings = []
    with open(input, 'r') as inputFile:
        line = inputFile.readline()
        zeroing = False
        while line:
            line = inputFile.readline()
            lineparts = line.split()

            if line == 'LOG: data: "Finished zeroing"\n':
                zeroing = False
            elif line == 'LOG: data: "Zeroing"\n':
                zeroing = True

            if not skipZeroing or not zeroing:
                if len(lineparts) == 19 and lineparts[4] == '"M':
                    readings.append(Reading(lineparts[7], lineparts[16], lineparts[17], float(lineparts[18]) + 20))


    return readings

def writeKml(readings, output):
    with open(output, 'w') as outputFile:
        outputFile.write(buildKmlHeader())
        buildPoints(readings, outputFile)
        outputFile.write(buildKmlFooter())

class Span(Enum):
    WALK = 1
    RANGE = 2

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

def calculateRange(type, start, end, length):
    # print "TYPE: {} {} {}".format(type, Span.WALK, Span.RANGE)
    if type == Span.WALK:
        waypoints = []
        # print "Calculating walk"
        deltax = end.x - start.x
        deltay = end.y - start.y
        deltaz = end.z - start.z
        distance = math.sqrt((deltax * deltax) + (deltay * deltay) + (deltaz * deltaz))
        for i in range(1, int(distance / length) + 1):
            waypoints.append(Point(start.x + (i * length * deltax / distance),
                                   start.y + (i * length * deltay / distance),
                                   start.z + (i * length * deltaz / distance)))
        return waypoints
    elif type == Span.RANGE:
        return [end]

def buildDDSAWaypoints(rangeType, altitude, size, index, loops, radius, steplength):

    waypoints = []
    start = Point(0, 0, altitude)
    waypoints.append(start)
    previous = start
    for loop in range(0, loops):
        for corner in range(0, 4):

            if (loop == 0 and corner == 0):
                next = Point(0, index + 1, altitude)
            else:
                xoffset = 1 + index + (loop * size)
                yoffset = xoffset
                if (corner == 0):
                    xoffset = -(1 + index + ((loop - 1) * size))
                elif (corner == 3):
                    xoffset = -xoffset
                if (corner == 2 or corner == 3):
                    yoffset = -yoffset

                next = Point(xoffset, yoffset, altitude)

            # print "{}, {} -> {}, {}".format(previous.x, previous.y, next.x, next.y)

            for waypoint in calculateRange(rangeType, previous, next, steplength):
                waypoints.append(Point(waypoint.x * radius, waypoint.y * radius, waypoint.z))

            previous = next

    return waypoints

def lookupIndex(ddsa, x, y):
    for i in range(0, len(ddsa)):
        if ddsa[i].x == x and ddsa[i].y == y:
            return i

    return -1

def buildCSV(input, output, image, kmlfile):
    reading = []
    center = None

    with open(input, 'r') as inputFile:
        line = "incoming"
        zeroing = False

        index = None
        readingsum = 0
        readingcount = 0

        while line:
            line = inputFile.readline()
            lineparts = line.split()

            if line == 'LOG: data: "Finished zeroing"\n':
                zeroing = False
            elif line == 'LOG: data: "Zeroing"\n':
                zeroing = True

            if not zeroing:
                if len(lineparts) == 8:
                    if not index == None:
                        reading.append(readingsum / readingcount)
                        readingsum = 0
                        readingcount = 0
                    index = int(lineparts[4][0:len(lineparts[4])-1])
                elif len(lineparts) == 19 and lineparts[4] == '"M':
                    # print "reading: {}".format(lineparts[7])
                    readingsum = readingsum + float(lineparts[7])
                    readingcount = readingcount + 1

                    if center == None:
                        center = (float(lineparts[16]), float(lineparts[17]), float(lineparts[18]))

        reading.append(readingsum / readingcount)
        print "ddsa @ {} {} : {}".format(len(reading), index, (readingsum / readingcount))

    ddsa = []

    loops = 1
    while(len(ddsa) < len(reading)):
        ddsa = buildDDSAWaypoints(Span.WALK, 0, 1, 0, loops, 1, 1)
        loops = loops + 1

    ddsa = ddsa[0:len(reading)]

    x_min = int(min([waypoint.x for waypoint in ddsa]))
    x_max = int(max([waypoint.x for waypoint in ddsa])) + 1
    y_min = int(min([waypoint.y for waypoint in ddsa]))
    y_max = int(max([waypoint.y for waypoint in ddsa])) + 1

    xspace = np.linspace(x_min, x_max, (x_max - x_min))
    yspace = np.linspace(y_min, y_max, (y_max - y_min))

    X, Y = np.meshgrid(xspace, yspace)
    Z = np.zeros(((y_max - y_min), (x_max - x_min)))

    average = sum(reading) / len(reading)

    for x in range(x_min, x_max):
        for y in range(y_min, y_max):

            index = lookupIndex(ddsa, y, -x)
            if not index == -1 and index < len(reading):
                Z[y - y_min][x - x_min] = reading[index]
            else:
                Z[y - y_min][x - x_min] = average


    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                 cmap='viridis', edgecolor='none')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    ax.view_init(azim=0, elev=90)

    dpi = 300
    plt.savefig(image, dpi=dpi)


    with open(output, 'w') as outputFile:
        for x in range(x_min, x_max):
            for y in range(y_min, y_max):
                index = lookupIndex(ddsa, y, -x)
                if not index == -1 and index < len(reading):
                    outputFile.write("{}, ".format(reading[index]))
                    # outputFile.write("{}, ".format(index))
                else:
                    outputFile.write("\"\", ")
            outputFile.write("\n")

    readingList = []

    print "min index: {}".format(reading.index(min(reading)))

    for x in range(x_min, x_max):
        for y in range(y_min, y_max):

            index = lookupIndex(ddsa, y, -x)
            if not index == -1 and index < len(reading):
                readingList.append(Reading(reading[index], center[0] - (x / 111358.0), center[1] + (y / 111358.0), center[2] + 20))
                # readingList.append(Reading(index, center[0] + (y / 111358.0), center[1] - (x / 111358.0), center[2] + 20))

    writeKml(readingList, kmlfile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Convert Dragonfly log into KML')
    parser.add_argument('input', type=str, help='Input Dragonfly log.')
    parser.add_argument('output', type=str, help='Output CSV file.')
    parser.add_argument('image', type=str, help='Output image file.')
    parser.add_argument('kmloutput', type=str, help='Output KML file.')
    args = parser.parse_args()

    buildCSV(args.input, args.output, args.image, args.kmloutput)
