#!/usr/bin/env python

import argparse

class Reading:
    def __init__(self, value, lat, lon, alt):
        self.value = value
        self.lat = lat
        self.lon = lon
        self.alt = float(alt) + 20

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
                        <coordinates>''')
    for reading in readings:
        outputFile.write(buildEntry(reading))
    outputFile.write('''</coordinates>
                    </LineString>
                    <Style> 
                      <LineStyle>  
                       <color>#ff0000ff</color>
                       <width>3</width>
                      </LineStyle> 
                     </Style>
                </Placemark>''')

def buildReadings(input):
    readings = []
    with open(input, 'r') as inputFile:
        line = inputFile.readline()
        while line:
            line = inputFile.readline()
            lineparts = line.split()

            if len(lineparts) == 19 and lineparts[4] == '"M':
                readings.append(Reading(lineparts[7], lineparts[16], lineparts[17], lineparts[18]))
            

    return readings

def writeKml(input, output):
    readings = buildReadings(input)
    with open(output, 'w') as outputFile:
        outputFile.write(buildKmlHeader())
        buildLine(readings, outputFile)
        outputFile.write(buildKmlFooter())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Convert Dragonfly log into KML')
    parser.add_argument('input', type=str, help='Input Dragonfly log.')
    parser.add_argument('output', type=str, help='Output KML file.')
    args = parser.parse_args()

    writeKml(args.input, args.output)
