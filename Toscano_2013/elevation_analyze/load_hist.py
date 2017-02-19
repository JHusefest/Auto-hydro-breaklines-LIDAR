from osgeo import gdal
import pylab as pl
import numpy as np
from skimage.external.tifffile import TiffFile

#### Classification of water breaklines using LIDAR ####

dir = "/Users/joakimtveithusefest/Documents/master_env/Fjell/data/testdata/ground/DENOISED/DEM_r4/"
filename = "70_ground_denoised_r4.tif"

dem_file = gdal.Open(dir+filename)

band = dem_file.GetRasterBand(1)
data = band.ReadAsArray()

rows, cols = data.shape
print('rows, cols DEM', rows, cols)

highest_elevation = data.max()
lowest_elevation = data.min()
print('storste verdi DEM: '+str(highest_elevation))
print('minste verdi DEM:,', str(lowest_elevation))

scale = 1023/highest_elevation
if scale <= 8:
    scale = 8
elif scale >= 25:
    scale = 25
else:
    scale = scale

print('scale: '+str(scale))


### Replaces all no-return with 0 and returns DEM File as array ###
def return_data():
    dem_file = fill_novalue(data)
    return dem_file, scale


def fill_novalue(data):
    fill_novalue = np.where(data == -9999, 0, data)
    return fill_novalue


### Makes a scaled histogram with associated coords in pixels. Every bin is a elevation ####
def scaled_with_coords(data):
    data = fill_novalue(data)
    num_rows, num_col = data.shape

    histogram = {}

    for rows in range(num_rows):
        for col in range(num_col):
            elevation = int(data[rows, col])
            mod_elevation = int(elevation * scale)
            try:
                coord = rows, col
                histogram.setdefault(mod_elevation, [])
                histogram[mod_elevation].append(coord)
            except KeyError:
                histogram[mod_elevation] = 1 #Frequency of elevation_analyze
    return histogram


## Help function which returns coords to chosen bin.
def search_coords_by_key(index):
    scaled_with_coord = scaled_with_coords(data)
    coord_elevation = scaled_with_coord[index]
    return coord_elevation


### Returns an unscaled histogram ####
def no_scaled_with_coords(data):

    data = fill_novalue(data)
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

def load_histogram(data):
    hist = scaled_with_coords(data)
    histogram = {}
    for elev in hist.keys():
        try:
            histogram[elev] = len(hist[elev]) #Frequency of elevation_analyze
        except KeyError:
            histogram[elev] = 1 #Frequency of elevation_analyze
    return histogram


### For fun, it loads normal unscaled histogram
def load_noscaled_histogram(data):
    hist = no_scaled_with_coords(data)
    histogram = {}
    for elev in hist.keys():
        try:
            histogram[elev] = len(hist[elev]) #Frequency of elevation_analyze
        except KeyError:
            histogram[elev] = 1 #Frequency of elevation_analyze
    return histogram


def make_mod_histogram(data, name):
    histogram = load_histogram(data)
    lowest_key = sorted(histogram.iterkeys())[0]
    X = np.arange(len(histogram))
    print('lowest_key', lowest_key)
    pl.bar(X, histogram.values(), width=0.5)
    pl.xlabel('Elevation from lowest point')
    pl.ylabel('Frequency')
    pl.title('Histogram '+name)
    ymax = max(histogram.values()) + 1
    pl.ylim(0, ymax)
    pl.show()


### Finds coordinates in original coordinate system - ESPSG-25833 - Euref89 ###

def pixel2coord(x, y):

    xoff, a, b, yoff, d, e = dem_file.GetGeoTransform()
    xp = a * x + b * y + xoff
    yp = d * x + e * y + yoff
    return xp, yp