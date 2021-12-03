#!/usr/bin/env python

import argparse, datetime

from .reading import Reading

class LogEntry:

    def __init__(self, type, line, date, data):
        self.type = type
        self.line = line
        self.date = date
        self.data = data

def parse_log(input, skip_zeroing):
    readings = []
    line_num = 0
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
            try:
                if len(lineparts) > 1:
                    reading_time = datetime.datetime.strptime("{} {}".format(lineparts[0], lineparts[1]), '%Y-%m-%d %H:%M:%S.%f')
                    if not skip_zeroing or not zeroing:
                        if len(lineparts) == 19 and lineparts[4] == '"M' and float(lineparts[7]) > 409:
                            readings.append(LogEntry('reading', line_num, reading_time, Reading(reading_time, lineparts[7], lineparts[16], lineparts[17], lineparts[18])))
                        elif len(lineparts) == 15 and lineparts[2] == 'co2:':
                            readings.append(LogEntry('reading', line_num, reading_time, Reading(reading_time, lineparts[3], lineparts[12], lineparts[13], lineparts[14])))
                        elif len(lineparts) > 3 and lineparts[2] == 'LOG:':
                            readings.append(LogEntry('log', line_num, reading_time, line))
                        else:
                            readings.append(LogEntry('unknown', line_num, reading_time, line))

                    else:
                        readings.append(LogEntry('zeroing', line_num, reading_time, line))

            except ValueError as e:
                readings.append(LogEntry('error', line_num, None, line))

            line_num = line_num + 1


    return readings

def writecsv(input, output):
    readings = parse_log(input, False)
    with open(output, 'w') as outputFile:
        outputFile.write("{}, {}, {}, {}, {}\n".format("time", "co2", "lat", "lon", "alt"))
        for reading in readings:
            outputFile.write("{}, {}, {}, {}, {}\n".format(reading.time, reading.value, reading.lat, reading.lon, reading.alt))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Convert Dragonfly log into CSV')
    parser.add_argument('--input', type=str, help='Input Dragonfly log.')
    parser.add_argument('--output', type=str, help='Output CSV file.')
    args = parser.parse_args()

    writecsv(args.input, args.output)
