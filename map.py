import sys
import csv
import math
import re
import PIL.ImageColor
import requests
import io
from region import Region
from region import Point
from plot import Plot
from PIL import Image, ImageDraw

STATES = ['Alabama','Arizona','Arkansas','California','Colorado','Connecticut','Delaware',
'Florida','Georgia','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky', 'Louisiana',
'Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri',
'Montana','Nebraska','Nevada','New_Hampshire','New_Jersey','New_Mexico','New_York',
'North_Carolina','North_Dakota','Ohio','Oklahoma','Oregon','Pennsylvania',
'Rhode_Island','South_Carolina','South_Dakota','Tennessee','Texas','Utah','Vermont'
'Virginia','Washington','West_Virginia','Wisconsin','Wyoming']

REGIONS = {'New_England':['Massachusetts','Connecticut', 'Rhode_Island','Maine',
'Vermont','New_Hampshire'], 'Mid_Atlantic': ['New_York','Pennsylvania','New_Jersey'
,'Maryland','Delaware','West_Virginia','Virginia'], 'Southeast' : ['North_Carolina'
,'South_Carolina','Georgia','Florida','Alabama','Mississippi','Kentucky','Tennessee'
,'Louisiana', 'Arkansas'], 'Midwest' : ['Ohio','Michigan','Indiana','Illinois','Wisconsin',
'Minnesota','Iowa','Missouri'], 'Great_Plains' : ['North_Dakota','South_Dakota','Nebraska'
,'Kansas','Oklahoma','Texas','Wyoming','Colorado'], 'Northwest' : ['Montana',
'Washington','Oregon','Idaho'], 'Southwest' : ['California', 'Utah', 'Nevada',
'Arizona', 'New_Mexico']}


COLORS = {-30 : '#5700FF', -29 : '#5700FF', -28 : '#5700FF', -27 : '#5700FF', -26 : '#4100FF', -25 : '#4100FF',
-24 : '#4100FF', -23 : '#4100FF', -22 : '#2A00FF', -21 : '#2A00FF', -20 : '#2A00FF', -19 : '#2A00FF', -18 : '#1300FF',
-17 : '#1300FF', -16 : '#1300FF', -15 : '#0003FF', -14 : '#0019FF', -13 : '#0030FF', -12 : '#0047FF', -11 : '#005EFF',
-10 : '#0075FF', -9 : '#008BFF', -8 : '#00A2FF', -7 : '#00B9FF', -6 : '#00D0FF', -5 : '#00E6FF', -4 : '#00FDFF', -3 : '#00FFE9',
 -2 : '#00FFD2', -1 : '#00FFBB', 0 : '#00FFA5', 1 : '#00FF8E', 2 : '#00FF77', 3 : '#00FF60', 4 : '#00FF4A', 5 : '#00FF33', 6 : '#00FF1C',
  7 : '#00FF05', 8 : '#11FF00', 9 : '#27FF00', 10 : '#3EFF00', 11 : '#55FF00', 12 : '#6CFF00', 13 : '#82FF00', 14 : '#99FF00', 15 : '#B0FF00',
   16 : '#C7FF00', 17 : '#DEFF00', 18 : '#F4FF00', 19 : '#FFF200', 20 : '#FFDB00', 21 : '#FFC400', 22 : '#FFAE00', 23 : '#FF9700', 24 : '#FF8000',
    25 : '#FF6900', 26 : '#FF5200', 27 : '#FF3C00', 28 : '#FF2500', 29 : '#FF0E00', 30 : '#FF0008', 31 : '#FF001E', 32 : '#FF0035', 33 : '#FF004C',
     34 : '#FF0063', 35 : '#FF007A', 36 : '#FF0090', 37 : '#FF00A7', 38 : '#FF00BE', 39 : '#FF00D5', 40 : '#FF00EB', 41 : '#FF00EB', 42 : '#FB00FF',
      43 : '#FB00FF', 44 : '#FB00FF', 45 : '#E400FF', 46 : '#E400FF', 47 : '#CD00FF', 48 : '#CD00FF', 49 : '#B600FF', 50 : '#B600FF'}

URL = 'http://aviationweather.gov/adds/dataserver_current/current/metars.cache.csv'

def mercator(lat):
    """project latitude 'lat' according to Mercator"""
    lat_rad = (lat * math.pi) / 180
    projection = math.log(math.tan((math.pi / 4) + (lat_rad / 2)))
    return (180 * projection) / math.pi

def grid(minlong, maxlong, minlat, maxlat, wind=True):
    '''
    Partitions area given by long and lat values into X*Y rectangles of uniform size.
    A coarser grid is used when plotting wind values in order to avoid visual clutter.

    '''
    if wind:
        X = 20
        Y = 20
        VALX = (maxlong-minlong)/X
        VALY = (maxlat-minlat)/Y
    else:
        X = 70
        Y = 70
        VALX = (maxlong-minlong)/X
        VALY = (maxlat - minlat)/Y
    #VALX and VALY are the width and height, respectively, of each rectangle in the grid
    grids = []
    currlong = minlong
    currlat = minlat
    #begin at bottom left corner of given area
    while currlat < maxlat:
    #iterate bottom to top by row
        if (currlat + VALY) < maxlat:
        #consideration given if the current row is the uppermost row to avoid
        #going out of bounds
            while currlong < maxlong:
            #iterate left to right by column
                if (currlong + VALX) < maxlong:
                #consideration given if the current column is the rightmost column
                #to avoid going out of bounds
                    grids.append(Region([(currlong, currlat), (currlong + VALX, currlat), (currlong + VALX, currlat + VALY), (currlong, currlat + VALY)]))
                else:
                    grids.append(Region([(currlong, currlat), (maxlong, currlat), (maxlong, currlat + VALY), (currlong, currlat+VALY)]))
                currlong=currlong + VALX
        else:
            while currlong < maxlong:
                if (currlong + VALX) < maxlong:
                #consideration given if the current column is the rightmost column
                #to avoid going out of bounds
                    grids.append(Region([(currlong, currlat), (currlong + VALX, currlat), (currlong + VALX, maxlat), (currlong, maxlat)]))
                else:
                    grids.append(Region([(currlong, currlat), (maxlong, currlat), (maxlong, maxlat), (currlong, maxlat)]))
                currlong = currlong + VALX
        currlong=minlong
        currlat+=VALY
        #after a row is completed, return to the furthest left column and the next row up,
        #repeating until the map is filled
    return grids

def time_and_date(tdstr):
    '''
    Extracts the date and time from a timestamp of format 'YYYY-MM-DDTHH:MM:SSZ"
    and converts the given time from Z time to EST.
    '''
    regextime = '([0-9]{2}):([0-9]{2}):[0-9]{2}Z'
    timestr = re.findall(regextime,tdstr)
    timeZ = int(timestr[0][0])
    regexdate = '([0-9]{4})-([0-9]{2})-([0-9]{2})'
    datestr = re.findall(regexdate, tdstr)
    dateint = int(datestr[0][2])
    if timeZ<5:
    #Consideration given if time in Z should actually yield a time on the previous
    #date in EST
        timeEST = 24-(5-timeZ)
        dateint-=1
    else:
        timeEST = timeZ-5
    date = '{}-{}-{}'.format(datestr[0][1],dateint,datestr[0][0][2:])
    time = '{}:{} EST'.format(timeEST,timestr[0][1])
    return '{} {}'.format(time,date)
def main(boundaries, output, section=None, filename = 'metars.cache.csv'):
    """
    Draws an image.
    This function creates an image object, constructs Region objects by reading
    in data from csv files, and draws polygons on the image based on those Regions,
    filling in image with colors based on temperature and vectors based on wind direction
    and speed.
    Args:
        boundaries (str): name of a csv file of geographic information
        output (str): name of a file to save the image
        section: area of US that the user wishes to map
        filename: name of file to draw weather data from
    """
    def to_point(lst):
        '''
        creates a list of tuples from a line of lat / lon values and converts to mercator
        '''
        coords = []
        i=2
        j=3
        while i<len(lst) and j<len(lst):
            coords.append([float(lst[i]),mercator(float(lst[j]))])
            i+=2
            j+=2
        return coords

    with open(boundaries, 'r') as fin2:
        parsedfin2 = list(csv.reader(fin2))
        boundarylist = []
        #section is compared to key values in both STATES and REGIONS
        #if it is not in either, the entire US is plotted
        if section in STATES:
            for row in parsedfin2:
                if row[0] == section:
                    boundarylist.append(to_point(row))
        elif section in REGIONS:
            for state in REGIONS[section]:
                for row in parsedfin2:
                    if row[0] == state:
                        boundarylist.append(to_point(row))
        else:
            for row in parsedfin2:
                boundarylist.append(to_point(row))
            section = 'USA'
        regions=[Region(coords) for coords in boundarylist]
    MINLONG=min([r.min_long() for r in regions])
    MAXLONG=max([r.max_long() for r in regions])
    MINLAT=min([r.min_lat() for r in regions])
    MAXLAT=max([r.max_lat() for r in regions])
    p = Plot(MINLONG, MINLAT, MAXLONG, MAXLAT)
    g = grid(MINLONG,MAXLONG,MINLAT,MAXLAT,False)
    #g is grid to be used for temperature plotting
    h=grid(MINLONG,MAXLONG,MINLAT,MAXLAT)
    #h is coarser grid to be used for wind plotting
    r = requests.get(URL)
    #retrieving the weather data file
    parsedfin = list(csv.reader(io.StringIO(r.text)))
    #converting the weather data into an iterable format
    unsorted = []
    for line in parsedfin[6:]:
    #Some rows in file do not yield proper values. Removing stations
    #from consideration set that do not have proper long, lat, temp,
    #wind speed, or wind direction values.
        try:
            float(line[8])
            float(line[7])
            float(line[5])
            float(line[4])
            float(line[3])
            unsorted.append(line)
        except ValueError as b:
            continue
    for c in unsorted:
    #modifying all latitude values into mercator form
        c[3] = mercator(float(c[3]))
    stations = sorted(unsorted, key=lambda row: float(row[4]), reverse = True)
    #sorting list of stations by longitude to improve efficiency
    timedate = time_and_date(stations[1][2])
    #time and date for the data from each station are relatively consistent
    #across all stations; thus the values from a station near the start of the
    #list are used
    for square in g:
        t=int(square.temp_and_wind(stations)[0])
        #temp value of square
        #t is cast to an int to yield closest color value for temperature
        #value in COLORS
        p.draw(square, COLORS[t])
    for windsquare in h:
        #arrows are drawn with respect to their wind speed and direction,
        #with color black and width of 1 used for visibility purposes
        w_speed = windsquare.temp_and_wind(stations)[1]
        w_direction = windsquare.temp_and_wind(stations)[2]
        p.draw_arrow(windsquare, w_speed, w_direction, 'BLACK', 1)
    for r in regions:
        p.draw(r, None, border=(0,0,0))
    p.draw_legend(section,timedate, COLORS)
    p.save(output)

if __name__ == '__main__':
    boundaries = sys.argv[1]
    output = sys.argv[2]
    section = sys.argv[3]
    main(boundaries, output, section)
