#!/usr/bin/env python

import math

class Reading:
    def __init__(self, time, value, lat, lon, alt):
        self.time = time
        self.value = float(value)
        self.lat = float(lat)
        self.lon = float(lon)
        self.alt = float(alt)

    def add(self, latadd, lonadd):
        return Reading(self.time, self.value, self.lat + latadd, self.lon + lonadd, self.alt)

    def distance(self, other):
        deltax = self.lat - other.lat
        deltay = self.lon - other.lon
        return math.sqrt((deltax * deltax) + (deltay * deltay))

    def distance_in_meters(self, other):
        earthCircumference = 40008000
        deltay = (self.lon - other.lon) * (earthCircumference / 360) * math.cos(self.lat * 0.01745)
        deltax = (self.lat - other.lat)  * (earthCircumference / 360)
        return math.sqrt((deltax * deltax) + (deltay * deltay))