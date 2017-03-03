from osgeo import gdal
import pylab as pl
import numpy as np
from lidar_prep import Preperation
from skimage.external.tifffile import imshow
import matplotlib.pyplot as plt
from osgeo import gdal
import osgeo.osr as osr

#### Classification of water breaklines using LIDAR ####


class Loaddems:
    def __init__(self, elevation_data, int_data):
        self.elevation_file = gdal.Open(elevation_data)
        open_int_data = gdal.Open(int_data)

        band_elev = self.elevation_file.GetRasterBand(1)
        band_int = open_int_data.GetRasterBand(1)

        self.elevation_data = band_elev.ReadAsArray()
        self.int_data = band_int.ReadAsArray()
        print(self.elevation_data.dtype)

        print('Shape', self.elevation_data.shape)

        highest_elevation = self.elevation_data.max()
        lowest_elevation = self.elevation_data.min()
        print('storste verdi DEM: '+str(highest_elevation))
        print('minste verdi DEM: {}'.format(str(lowest_elevation)))

        scale = 1023/highest_elevation
        self.original_scale = scale
        print('ORIGINAL SCALE', self.original_scale)
        if scale <= 8:
            self.scale = 8
        elif scale >= 25:
            self.scale = 25
        else:
            self.scale = scale

        print('Scale', self.scale)


    ### Replaces all no-return with 0 and returns DEM File as array ###

    @staticmethod
    def fill_novalue(data):
        fill_novalue = np.where(data < 0, 0, data)
        return fill_novalue

    def return_data(self):
        elev_data_array = self.fill_novalue(self.elevation_data)
        int_data_array = self.fill_novalue(self.int_data)
        max_value = abs(elev_data_array.max())
        min_value = abs(elev_data_array.min())
        if abs(self.original_scale) > 1500:
            print('Her var det veeeldig flatt..')
            pass
        else:

            return elev_data_array, int_data_array, self.scale

    ### Makes a scaled histogram with associated coords in pixels. Every bin is a elevation ####
    def scaled_with_coords(self, data):
        data = self.fill_novalue(data)
        num_rows, num_col = data.shape

        histogram = {}

        for rows in range(num_rows):
            for col in range(num_col):
                elevation = int(data[rows, col])
                mod_elevation = int(elevation * self.scale)
                try:
                    coord = rows, col
                    histogram.setdefault(mod_elevation, [])
                    histogram[mod_elevation].append(coord)
                except KeyError:
                    histogram[mod_elevation] = 1 #Frequency of elevation_analyze
        return histogram

    ## Help function which returns coords to chosen bin.
    def search_coords_by_key(self, index):
        scaled_with_coord = self.scaled_with_coords(self.elevation_data)
        coord_elevation = scaled_with_coord[index]
        return coord_elevation

    ### Returns an unscaled histogram ####
    def no_scaled_with_coords(self, data):

        data = self.fill_novalue(data)
        num_rows, num_col = data.shape

        histogram = {}

        for rows in range(num_rows):
            for col in range(num_col):
                elevation = int(data[rows, col])
                try:
                    coord = (rows, col)
                    histogram.setdefault(elevation, [])
                    histogram[elevation].append(coord)
                except KeyError:
                    histogram[elevation] = 1 #Frequency of elevation_analyze
        return histogram


    ### Loads histogram without coords ###

    def load_histogram(self, data):
        hist = self.scaled_with_coords(self.elevation_data)
        histogram = {}
        for elev in hist.keys():
            try:
                histogram[elev] = len(hist[elev]) #Frequency of elevation_analyze
            except KeyError:
                histogram[elev] = 1 #Frequency of elevation_analyze
        return histogram


    ### For fun, it loads normal unscaled histogram
    def load_noscaled_histogram(self, data):
        hist = self.no_scaled_with_coords(self.elevation_data)
        histogram = {}
        for elev in hist.keys():
            try:
                histogram[elev] = len(hist[elev]) #Frequency of elevation_analyze
            except KeyError:
                histogram[elev] = 1 #Frequency of elevation_analyze
        return histogram

    def make_mod_histogram(self, data, name):
        histogram = self.load_histogram(data)
        X = np.arange(len(histogram))
        pl.bar(X, histogram.values())
        pl.xlabel('Elevation from lowest point')
        pl.ylabel('Frequency')
        pl.title('Histogram '+name)
        ymax = max(histogram.values()) + 1
        pl.ylim(0, ymax)
        pl.show()

    ### Finds coordinates in original coordinate system - ESPSG-25833 - Euref89 ###

    def pixel2coord(self, x, y, z):
        xoff, a, b, yoff, d, e = self.elevation_file.GetGeoTransform()
        xp = a * x + b * y + xoff
        yp = d * x + e * y + yoff
        return xp, yp, z

#elev_data_array, int_data_array, scale = l.return_data()



