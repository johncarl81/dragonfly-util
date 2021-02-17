#! /usr/bin/env python
import math, pulp
from enum import Enum
from geometry_msgs.msg import PoseStamped, Point

class Span(Enum):
    WALK = 1
    RANGE = 2


def calculateRange(type, start, end, length):
    print "TYPE: {} {} {}".format(type, Span.WALK, Span.RANGE)
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

            print "{}, {} -> {}, {}".format(previous.x, previous.y, next.x, next.y)

            for waypoint in calculateRange(rangeType, previous, next, stepLength):
                waypoints.append(Point(waypoint.x * radius, waypoint.y * radius, waypoint.z))

            previous = next

    return waypoints
