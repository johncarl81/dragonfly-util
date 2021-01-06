#!/usr/bin/env python

import argparse, datetime

class Reading:
    def __init__(self, time, value, lat, lon, alt):
        self.time = time
        self.value = float(value)
        self.lat = float(lat)
        self.lon = float(lon)
        self.alt = float(alt)

    def add(self, latadd, lonadd):
        return Reading(self.time, self.value, self.lat + latadd, self.lon + lonadd, self.alt)

def buildReadings(input, skipZeroing, start_time):
    readings = []
    time_diff = None
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
                if len(lineparts) == 19 and lineparts[4] == '"M' and float(lineparts[7]) > 420:
                    if time_diff is None:
                        first_time = datetime.datetime.strptime("{} {}".format(lineparts[0], lineparts[1]), '%Y-%m-%d %H:%M:%S.%f')
                        time_diff = start_time - first_time
                        print time_diff
                    reading_time = datetime.datetime.strptime("{} {}".format(lineparts[0], lineparts[1]), '%Y-%m-%d %H:%M:%S.%f')
                    readings.append(Reading(reading_time + time_diff, lineparts[7], lineparts[16], lineparts[17], float(lineparts[18])))
            

    return readings

def writecsv(input, output, start_time):
    readings = buildReadings(input, False, start_time)
    with open(output, 'w') as outputFile:
        outputFile.write("{}, {}, {}, {}, {}\n".format("time", "co2", "lat", "lon", "alt"))
        for reading in readings:
            outputFile.write("{}, {}, {}, {}, {}\n".format(reading.time, reading.value, reading.lat, reading.lon, reading.alt))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Convert Dragonfly log into CSV')
    parser.add_argument('--input', type=str, help='Input Dragonfly log.')
    parser.add_argument('--output', type=str, help='Output CSV file.')
    parser.add_argument('--start', type=str)
    args = parser.parse_args()

    start_time = datetime.datetime.strptime(args.start, '%Y-%m-%d %H:%M:%S.%f')

    writecsv(args.input, args.output, start_time)
