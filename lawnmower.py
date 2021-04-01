#!/usr/bin/env python

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import math, pulp
from enum import Enum
from geometry_msgs.msg import PoseStamped, Point

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class Span(Enum):
    WALK = 1
    RANGE = 2

def createWaypoint(x, y, altitude):
    waypoint = PoseStamped()
    waypoint.pose.position.x = x
    waypoint.pose.position.y = y
    waypoint.pose.position.z = altitude

    return waypoint

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

def buildRelativeWaypoint(waypoint, altitude):
    return [waypoint.longitude, waypoint.latitude, altitude]

def createLatLon(localwaypoint, localposition, position):
    earthCircumference = 40008000
    latitude = position.latitude - (localposition.y - localwaypoint.y) * 360 / earthCircumference
    longitude= position.longitude - (localposition.x - localwaypoint.x) * 360 / (earthCircumference * math.cos(latitude * 0.01745))

    return LatLon(latitude = latitude, longitude = longitude, relativeAltitude = localwaypoint.z)

def linearXRange(points, setY, type):

    problem = pulp.LpProblem('range', type)

    x = pulp.LpVariable('x', cat='Continuous')
    y = pulp.LpVariable('y', cat='Continuous')

    # Objective function
    problem += x

    def buildLineEquation(index1, index2):
        a = -(points[index2][1] - points[index1][1])
        b = points[index2][0] - points[index1][0]
        c = (a * points[index1][0]) + (b * points[index1][1])
        # print '(', a, 'x+',b,'y >=',c,'),'
        return (a * x) + (b * y) >= c

    for i in range(1, len(points)):
        problem +=buildLineEquation(i-1, i)

    problem += buildLineEquation(len(points)-1, 0)

    problem += y == setY

    # print problem
    pulp.GLPK_CMD(msg=0).solve(problem)

    return x.value()

def linearYRange(points, type):

    problem = pulp.LpProblem('range', type)

    x = pulp.LpVariable('x', cat='Continuous')
    y = pulp.LpVariable('y', cat='Continuous')

    # Objective function
    problem += y

    def buildLineEquation(index1, index2):
        a = -(points[index2][1] - points[index1][1])
        b = points[index2][0] - points[index1][0]
        c = (a * points[index1][0]) + (b * points[index1][1])
        # print '(', a, 'x+',b,'y >=',c,'),'
        return (a * x) + (b * y) >= c

    for i in range(1, len(points)):
        problem +=buildLineEquation(i-1, i)

    problem += buildLineEquation(len(points)-1, 0)

    # print problem
    pulp.GLPK_CMD(msg=0).solve(problem)

    return y.value()

def build3DLawnmowerWaypoints(rangeType, stacks, boundary, stepLength):
    waypoints = []
    toggleReverse = False
    for stack in range(0, stacks):

        lawnmowerWaypoints = buildLawnmowerWaypoints(rangeType, stack, boundary, stepLength)
        if toggleReverse:
            lawnmowerWaypoints = lawnmowerWaypoints[::-1]
        waypoints = waypoints + lawnmowerWaypoints

        toggleReverse = not toggleReverse

    return waypoints

def buildLawnmowerWaypoints(rangeType, altitude, boundary, stepLength):
    boundary_meters = []

    waypoints = []

    for waypoint in boundary:
        boundary_meters.append(buildRelativeWaypoint(waypoint, altitude))

    # Get minimum in Y dimension
    miny = linearYRange(boundary_meters, pulp.LpMinimize)
    # Get maximum in Y dimension
    maxy = linearYRange(boundary_meters, pulp.LpMaximize)



    stepdirection = 1 if miny < maxy else -1

    for y in range(int(math.ceil(miny)), int(math.floor(maxy)), int(2 * stepLength)):
        minx = linearXRange(boundary_meters, y, pulp.LpMinimize)
        maxx = linearXRange(boundary_meters, y, pulp.LpMaximize)
        waypoints.append(createWaypoint(minx, y, altitude))
        for point in calculateRange(rangeType, Point(minx, y, altitude), Point(maxx, y, altitude), stepLength):
            waypoints.append(createWaypoint(point.x, point.y, point.z))
        minx = linearXRange(boundary_meters, y + stepLength, pulp.LpMinimize)
        maxx = linearXRange(boundary_meters, y + stepLength, pulp.LpMaximize)
        waypoints.append(createWaypoint(maxx, y + stepLength, altitude))
        for point in calculateRange(rangeType, Point(maxx, y + (stepdirection * stepLength), altitude), Point(minx, y + (stepdirection * stepLength), altitude), stepLength):
            waypoints.append(createWaypoint(point.x, point.y, point.z))

    return waypoints

def latlons(input):
    output = []
    for coordinate in input:
        output.append( dotdict({"latitude": coordinate[1], "longitude": coordinate[0]}))
    return output

def plotPath(ax, boundary, color, style, name):
    stepLength = 1
    waypoints = build3DLawnmowerWaypoints(Span.RANGE, 3, boundary, stepLength)

    lat = [(w.pose.position.y) * -10 for w in waypoints]
    lon = [(w.pose.position.x - 5) * -10 for w in waypoints]
    alt = [(w.pose.position.z + 1) * 10 for w in waypoints]

    ax.plot(lon, lat, alt, color + style, label=name)
    ax.scatter(lon[0], lat[0], alt[0], color = color, marker = 'o', s = 50)
    ax.scatter(lon[len(lon)-1], lat[len(lat)-1], alt[len(alt)-1], color = color, marker='X', s = 50)

def plotBoundary(ax, boundary, color, style, name):
    boundary.append(boundary[0])
    ax.plot([(b.longitude - 5) * -10 for b in boundary], [(b.latitude) * -10 for b in boundary], [0.7 * 10] * len(boundary), color + style, label=name , zorder=-1)

def main():
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42

    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, projection='3d')
    boundary = latlons([[5,0], [-5,-5], [-5,-10], [0, -12], [5, -10]])

    plotPath(ax, boundary, "C0", '-', 'Dragonfly 1')

    plotBoundary(ax, boundary, 'k', '-.', 'Survey Boundary')


    # ax.legend(bbox_to_anchor = [1, .9], ncol = 3)

    ax.view_init(12.6889020071, -53)

    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_zlabel('z (m)')
    ax.set_xlim(110, 0)
    ax.set_ylim(120, 0)
    ax.set_zlim(5, 35)
    ax.set_xticks([0, 20, 40,  60, 80, 100])
    ax.set_yticks([100, 80, 60, 40, 20, 0])
    ax.set_xticklabels([0, '', 40, '', 80, ''])
    ax.set_yticklabels(['', 40, '', 80, ''])
    ax.set_zticks(range(10, 40, 10))


    plt.tight_layout()
    plt.savefig('Multilayer_Lawnmower_Final.png', dpi=300, bbox_inches='tight')
    # plt.show()
    # print ax.azim, ax.elev, ax.dist

if __name__ == '__main__':
    main()
