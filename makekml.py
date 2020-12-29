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
    radius = 0.000003
    i = 0
    minreading = min(reading.value for reading in readings)
    maxreading = max(reading.value for reading in readings)
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
       <color>#{}0000ff</color>
      <outline>0</outline>
      </PolyStyle> 
     </Style>
    </Placemark>
    '''.format(hexreading))

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

def writeKml(input, output):
    readings = buildReadings(input, False)
    readingsWithoutZeroing = buildReadings(input, True)
    with open(output, 'w') as outputFile:
        outputFile.write(buildKmlHeader())
        buildLine(readings, outputFile)
        buildPoints(readingsWithoutZeroing, outputFile)
        outputFile.write(buildKmlFooter())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Convert Dragonfly log into KML')
    parser.add_argument('input', type=str, help='Input Dragonfly log.')
    parser.add_argument('output', type=str, help='Output KML file.')
    args = parser.parse_args()

    writeKml(args.input, args.output)
