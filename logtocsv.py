#!/usr/bin/env python

import argparse

class Reading:
    def __init__(self, value, lat, lon, alt):
        self.value = float(value)
        self.lat = float(lat)
        self.lon = float(lon)
        self.alt = float(alt)

    def add(self, latadd, lonadd):
        return Reading(self.value, self.lat + latadd, self.lon + lonadd, self.alt)

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

def writecsv(input, output):
    readings = buildReadings(input, False)
    with open(output, 'w') as outputFile:
        for reading in readings:
            outputFile.write("{}, {}, {}, {}\n".format(reading.value, reading.lat, reading.lon, reading.alt))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Convert Dragonfly log into CSV')
    parser.add_argument('input', type=str, help='Input Dragonfly log.')
    parser.add_argument('output', type=str, help='Output CSV file.')
    args = parser.parse_args()

    writecsv(args.input, args.output)
