#!/usr/bin/env python

import argparse, datetime, math

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

VIRTUAL_SOURCE = dotdict({
    "latitude": 35.19465,
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

    if x >= 0 or y > 20 or y < -20:
        return 420

    Q = 5000
    K = 2
    H = 2
    u = 1

    value = (Q / (2 * math.pi * K * -x)) * math.exp(- (u * ((pow(y, 2) + pow(H, 2))) / (4 * K * -x)))

    if value < 0:
        return 420
    else:
        return 420 + value

class Reading:
    def __init__(self, time, value, lat, lon, alt):
        self.time = time
        self.value = float(value)
        self.lat = float(lat)
        self.lon = float(lon)
        self.alt = float(alt)

    def add(self, latadd, lonadd):
        return Reading(self.time, self.value, self.lat + latadd, self.lon + lonadd, self.alt)

def buildReadings(input, start_time):
    readings = []
    time_diff = 0

    with open(input, 'r') as inputFile:
        line = inputFile.readline()
        while line:
            line = inputFile.readline()
            if line.startswith('GPS,'):
                lineparts = line.split(', ')

                position = dotdict({
                    "latitude": float(lineparts[7]),
                    "longitude": float(lineparts[8])
                })

                readings.append(Reading(start_time + datetime.timedelta(0,time_diff), calculateCO2(position), lineparts[7], lineparts[8], lineparts[9]))

                time_diff += 1



    return readings

def writecsv(input, output, start_time):
    readings = buildReadings(input, start_time)
    with open(output, 'w') as outputFile:
        outputFile.write("{},{},{},{},{}\n".format("time", "co2", "lat", "lon", "alt"))
        for reading in readings:
            outputFile.write("{},{},{},{},{}\n".format(reading.time, reading.value, reading.lat, reading.lon, reading.alt))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Convert Dragonfly log into CSV')
    parser.add_argument('--input', type=str, help='Input Dragonfly log.')
    parser.add_argument('--output', type=str, help='Output CSV file.')
    parser.add_argument('--start', type=str)
    args = parser.parse_args()

    start_time = datetime.datetime.strptime(args.start, '%Y-%m-%d %H:%M:%S.%f')

    writecsv(args.input, args.output, start_time)
