import math
import csv

class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return "({},{})".format(self.x,self.y)

    def getx(self):
        return self.x

    def gety(self):
        return self.y

    def distance(self,pt):
        "a distance formula between two points"
        return math.sqrt( (self.getx() - pt.getx())**2 + (self.gety() - pt.gety())**2 )

class Region:
    """
    A region represented by a list of long/lat coordinates.
    """

    def __init__(self, coords):
        self.coords = coords

    def lats(self):
        "Return a list of the latitudes of all the coordinates in the region"
        latslist = []
        for coord in self.coords:
            latslist.append(coord[1])
        return latslist
    def longs(self):
        "Return a list of the longitudes of all the coordinates in the region"
        longslist = []
        for coord in self.coords:
            longslist.append(coord[0])
        return longslist
    def min_lat(self):
        "Return the minimum latitude of the region"
        return min(self.lats())
    def min_long(self):
        "Return the minimum longitude of the region"
        return min(self.longs())
    def max_lat(self):
        "Return the maximum latitude of the region"
        return max(self.lats())
    def max_long(self):
        "Return the maximum longitude of the region"
        return max(self.longs())
    def midpoint(self):
        "Return a tuple of the coordinates of the midpoint of the region"
        return ((self.max_long() + self.min_long())/2, (self.max_lat() + self.min_lat())/2)
    #http://aviationweather.gov/adds/dataserver_current/current/metars.cache.csv
    def temp_and_wind(self, stations):
        "Return a list containing the average temperature, wind speed, and wind"
        "direction readings from the closest 3 stations to a region's midpoint"
        INITIALVAL = (1000, 1000)
        #extremely high value used for initial comparison purposes in finding closest
        #stations and as a general placeholder
        closestations = [Point(INITIALVAL[0],INITIALVAL[1]), Point(INITIALVAL[0],INITIALVAL[1]), Point(INITIALVAL[0],INITIALVAL[1])]
        #list to hold 3 closest stations to a region's midpoint
        temps = [0,0,0]
        #list to hold temperature readings for 3 closest stations
        wind_speeds = [INITIALVAL[0],INITIALVAL[0],INITIALVAL[0]]
        #list to hold wind speed readings for 3 closest stations
        wind_directions = [INITIALVAL[0],INITIALVAL[0],INITIALVAL[0]]
        #list to hold wind direction readings for 3 closest stations
        pointmid = Point(self.midpoint()[0],self.midpoint()[1])
        #midpoint of region to be used to find closest stations
        startindex = 0
        lowerbound = 0
        upperbound = len(stations)-1
        midindex = int(upperbound/2)
        #indices used for binary search
        while round(float(stations[midindex][4]), 0) != round(float(pointmid.getx()), 0) and midindex>0:
        #binary search algorithm used to insert into list at a station with longitude
        #value approximately that of the midpoint of the region
            if round(float(stations[midindex][4]), 0) > round(float(pointmid.getx()), 0):
                lowerbound = midindex+1
                midindex = int((lowerbound+upperbound)/2)
            else:
                upperbound =midindex-1
                midindex = int((lowerbound+upperbound)/2)
        startindex = midindex
        #index of station with closest longitude value
        startindexsub = 50
        startindexadd = 50
        #values used to determine reasonable bounds of search in terms of number
        #of stations to increase efficiency
        while (startindex - startindexsub < 0):
            startindexsub-=1
        while (startindex + startindexadd > len(stations)):
            startindexadd-=1
        #these loops are used to avoid indexing out of bounds in determining
        #the search radius within the list
        if startindex < 1:
            startindexsub=0
            startindexadd=len(stations)-2
        #if no stations with int value longitude of the midpoint are found, the
        #entire list will be used in comparison
        for station in stations[startindex - startindexsub:startindex + startindexadd]:
        #for each station in the determined search radius, the station's distance from
        #the midpoint of the region is compared to the distances of the points already
        #in the closestations list. The list is always length 3; whenever a new
        #point is added, the point at index 0 is popped and any points at lower indices
        #are shifted down. The data of the new station are added to their respective
        #lists at the same index that the station's coordinates are added to closestations
            pointcur = Point(station[4], station[3])
            if pointmid.distance(pointcur) < pointmid.distance(closestations[0]) and pointmid.distance(pointcur) < pointmid.distance(closestations[1]) and pointmid.distance(pointcur) < pointmid.distance(closestations[2]):
            #if the station is closer than all 3 points, it is appended to the list
            #and its corresponding data are added to their respective lists at the
            #same index
                closestations.pop(0)
                closestations.append(Point(pointcur.getx(),pointcur.gety()))
                temps.pop(0)
                temps.append(float(station[5]))
                wind_speeds.pop(0)
                wind_speeds.append(float(station[8]))
                wind_directions.pop(0)
                wind_directions.append(float(station[7]))
            elif pointmid.distance(pointcur) < pointmid.distance(closestations[0]) and pointmid.distance(pointcur) < pointmid.distance(closestations[1]):
            #if the station is closer than 2 of the 3 points, it is inserted at
            #index 1
                closestations.pop(0)
                closestations.insert(1,Point(pointcur.getx(),pointcur.gety()))
                temps.pop(0)
                temps.insert(1,float(station[5]))
                wind_speeds.pop(0)
                wind_speeds.insert(1,float(station[8]))
                wind_directions.pop(0)
                wind_directions.insert(1,float(station[7]))
            elif pointmid.distance(pointcur) < pointmid.distance(closestations[0]):
            #if the station is closer than 1 of the 3 points, it is inserted at index 0
                closestations.pop(0)
                closestations.insert(0,Point(pointcur.getx(),pointcur.gety()))
                temps.pop(0)
                temps.insert(0,float(station[5]))
                wind_speeds.pop(0)
                wind_speeds.insert(0,float(station[8]))
                wind_directions.pop(0)
                wind_directions.insert(0,float(station[7]))
            #if the station is not closer than any of the 3 points, the list remains
            #unchanged
        average_readings = [float(sum(temps)/3),float(sum(wind_speeds)/3),float(sum(wind_directions)/3)]
        return average_readings
        #temperature, wind speed, and wind direction values are averaged based on the 3 values
        #in their respective lists to gain a more accurate estimate of values at nearby points
