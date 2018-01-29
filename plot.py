from PIL import Image, ImageDraw, ImageFont
from PIL.ImageColor import getrgb
from region import Point
from region import Region
import math

class Plot:

    """
    Provides the ability to map, draw and color regions in a long/lat
    bounding box onto a proportionally scaled image.
    """
    @staticmethod
    def interpolate(x_1, x_2, x_3, newlength):
        """
        linearly interpolates x_2 <= x_1 <= x_3 into newlength
        x_2 and x_3 define a line segment, and x2 falls somewhere between them
        scale the width of the line segment to newlength, and return where
        x_1 falls on the scaled line.
        """
        return ((x_1-x_2)/(x_3-x_2))*newlength
    @staticmethod
    def proportional_height(new_width, width, height):
        """
        return a height
         for new_width that is
        proportional to height with respect to width
        Yields:
            int: a new height
        """
        return int(height*(new_width/width))

    def __init__(self, min_long, min_lat, max_long, max_lat):
        """
        Create a width x height image where height is proportional to width
        with respect to the long/lat coordinates.
        """
        self.width = 1024
        self.min_long = min_long
        self.min_lat = min_lat
        self.max_long = max_long
        self.max_lat = max_lat
        self.height = Plot.proportional_height(self.width, self.max_long-self.min_long, self.max_lat-self.min_lat)
        self.image = Image.new("RGB",(self.width, self.height+200), (255,255,255))
        #image height adjusted to allow space for legend
    def trans_long(self, longi):
        '''
        returns interpolated longitudinal value
        '''
        return Plot.interpolate(longi,self.min_long,self.max_long,self.width)
    def trans_lat(self, lati):
        '''
        returns interpolated latitudinal value
        '''
        return self.height - Plot.interpolate(lati,self.min_lat, self.max_lat, self.height)
    def save(self, filename):
        """save the current image to 'filename'"""
        self.image.save(filename, "PNG")
    def draw(self, region, color, border=None):
        """
        Draws 'region' in the given 'style' at the correct position on the
        current image filled with color
        Args:
            region (Region): a Region object with a set of coordinates
            color (str): determines fill of polygon
            border (str): border color
        """

        coords = [(self.trans_long(x), self.trans_lat(y)) for x,y in zip(region.longs(), region.lats())]
        ImageDraw.Draw(self.image).polygon(coords, color, border)
    def draw_arrow(self, reg, windspeed, winddirection, color, width):
        '''
        draws an arrow from point start to point end, where point1 and point2
        are the points of the arrow
        '''
        SPEEDSCALE = 5
        #SPEEDSCALE used to scale size of wind vectors

        def rotate(p1,p2, angle):
            '''returns the coordinates of a point p2 rotated about another point p1'''
            radangle = math.radians(angle)
            rotated_p = Point(p1.getx() + (p2.getx()-p1.getx())*math.cos(radangle)+(p2.gety()-p1.gety())*math.sin(radangle),
                        p1.gety() - (p2.getx()-p1.getx())*math.sin(radangle)+(p2.gety()-p1.gety())*math.cos(radangle))
            return rotated_p
        start = Point(reg.midpoint()[0], reg.midpoint()[1])
        #starting point of vector
        transstart = Point(self.trans_long(start.getx()), self.trans_lat(start.gety()))
        #starting point interpolated
        scaler = Point(transstart.getx(),transstart.gety()+windspeed*SPEEDSCALE)
        #point vertical from starting point, with distance based on wind speed
        end = rotate(transstart, scaler ,-winddirection)
        #scaler rotated about starting point
        transpoint1 = rotate(transstart, Point(scaler.getx()+transstart.distance(scaler)/10, scaler.gety()-(transstart.distance(scaler)/10)),-winddirection)
        transpoint2 = rotate(transstart, Point(scaler.getx()-transstart.distance(scaler)/10, scaler.gety()-(transstart.distance(scaler)/10)),-winddirection)
        #points used to create a triangle where one point is the end point of the vector,
        #and other points are shifted along the line to form an arrow when plotted
        #constants are for scaling the visualization
        ImageDraw.Draw(self.image).line([(transstart.getx(),transstart.gety()),(end.getx(),end.gety())], color, width)
        #drawing line portion of vector
        ImageDraw.Draw(self.image).polygon([(transpoint1.getx(),transpoint1.gety()),(end.getx(),end.gety()),
        (transpoint2.getx(),transpoint2.gety())],color,color)
        #drawing triangle arrowhead of vector

    def draw_legend(self, section, timedate, colorscale):
        '''
        draws a legend at base of image to describe data displayed
        '''
        ImageDraw.Draw(self.image).rectangle([0,self.height, self.width, self.height+200], 'WHITE')
        #white rectangle used to eliminate arrow vectors that have passed beyond the southern
        #border of the map to avoid ugliness
        SHIFT = (750//len(colorscale))
        #value used to draw rectangles for each color in the color gradient and some
        #corresponding temperature values from colorscale
        X0 = 100
        Y0 = self.height + 100
        fontsize = 20
        font = ImageFont.truetype('FreeSans.ttf', fontsize)
        ImageDraw.Draw(self.image).text((15,Y0+35),text = 'Temp(C):', font = font, fill = 'BLACK')
        for num in sorted(colorscale):
            if int(num)%5 == 0:
            #temperature values divisible by 5 are displayed to make color scale
            #more comprehensible
                ImageDraw.Draw(self.image).text((X0,Y0+35),text = str(num), font = font, fill = 'BLACK')
            ImageDraw.Draw(self.image).rectangle([(X0,Y0),(X0+SHIFT),(Y0+30)], colorscale[num])
            X0+=SHIFT
        ImageDraw.Draw(self.image).text((20,self.height+5), text = timedate, font = font, fill = 'BLACK')
        #drawing time and date
        if '_' in str(section):
            no_underscore = ' '.join(section.split('_'))
            ImageDraw.Draw(self.image).text([(self.width/2)-200 ,(self.height+5)], text = 'Location:' + no_underscore, font = font, fill = 'BLACK')
        else:
            ImageDraw.Draw(self.image).text([(self.width/2)-200 ,(self.height+5)], text = 'Location:' + section, font = font, fill = 'BLACK')
        #drawing section, replacing the underscore separating names with two words with a space if applicable
        ImageDraw.Draw(self.image).text((675,self.height+5),text = 'The wind direction and magnitude are \n displayed in vector form.', font = font, fill = 'BLACK')
        #drawing information about vectors
        ImageDraw.Draw(self.image).text((715,self.height+170),text = 'Source: http://aviationweather.gov/', font = font, fill = 'BLACK')
        #drawing credit for source of data
