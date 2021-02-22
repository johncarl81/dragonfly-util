#!/usr/bin/env python

import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import math, pulp
from enum import Enum
from geometry_msgs.msg import PoseStamped, Point

class Span(Enum):
    WALK = 1
    RANGE = 2

def calculateRange(type, start, end, length):
    if type == Span.WALK:
        waypoints = []
        print "Calculating walk"
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

def build3DDDSAWaypoints(rangeType, stacks, size, index, loops, radius, stepLength):
    waypoints = []
    toggleReverse = False
    for stack in range(0, stacks):

        ddsaWaypoints = buildDDSAWaypoints(rangeType, stack, size, index, loops, radius, stepLength)
        if toggleReverse:
            ddsaWaypoints = ddsaWaypoints[::-1]
        waypoints = waypoints + ddsaWaypoints

        toggleReverse = not toggleReverse

    return waypoints

def buildDDSAWaypoints(rangeType, altitude, size, index, loops, radius, stepLength):

    waypoints = []
    start = Point(-index, 0, altitude)
    waypoints.append(start)
    previous = start
    for loop in range(loops):
        for corner in range(4):

            xoffset = loop * size + index + 1
            yoffset = xoffset
            if corner == 0:
                xoffset = -size * loop - index
            if corner == 2 or corner == 3:
                yoffset = -yoffset
            if corner == 3:
                xoffset = -xoffset - (size - 1)
                # Ends loop square with the last corner
                if loop == loops - 1:
                    xoffset += index  + 1


            next = Point(xoffset, yoffset, altitude)

            for waypoint in calculateRange(rangeType, previous, next, stepLength):
                waypoints.append(Point(waypoint.x * radius, waypoint.y * radius, waypoint.z))

            previous = next

    return waypoints

def plotPath(ax, index, color, style, name):
    waypoints = build3DDDSAWaypoints(Span.RANGE, 3, 3, index, 2, 1, 1)

    lat = [w.y for w in waypoints]
    lon = [w.x for w in waypoints]
    alt = [w.z for w in waypoints]

    ax.plot(lon, lat, alt, color + style, label=name, zorder=-index)
    ax.scatter(lon[0], lat[0], alt[0], color = color, marker = 'o', s = 50, zorder=-index)
    ax.scatter(lon[len(lon)-1], lat[len(lat)-1], alt[len(alt)-1], color = color, marker='X', s = 50, zorder=-index)

def main():

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    plotPath(ax, 0, "C0", '-', 'Agent 1')
    plotPath(ax, 1, "C1", '--', 'Agent 2')
    plotPath(ax, 2, "C2", '-.', 'Agent 3')

    ax.legend()

    ax.view_init(12.6889020071, -58.2591559544)

    ax.set_xlabel('Y Offset (meters)')
    ax.set_xlim(6, -6)
    ax.set_ylim(6, -6)
    ax.set_zlim(-0.5, 2.5)
    ax.set_ylabel('X Offset (meters)')
    ax.set_zlabel('Altitude Offset (meters)')
    ax.set_xticks(range(-14, 15, 2))
    ax.set_yticks(range(-14, 15, 2))
    ax.set_zticks(range(0, 3))


    plt.tight_layout()
    plt.savefig('Multilayer_DDSA.pdf', dpi=300, bbox_inches='tight')
    # plt.show()
    #
    # xlm=ax.get_xlim3d() #These are two tupples
    # ylm=ax.get_ylim3d() #we use them in the next
    # zlm=ax.get_zlim3d() #graph to reproduce the magnification from mousing
    # # axx=ax.get_axes()
    # azm=ax.azim
    # ele=ax.elev

    # print "{} {} {} {} {}".format(xlm, ylm, zlm, azm, ele)

if __name__ == '__main__':
    main()
