import liblas
from osgeo import gdal
import subprocess
import os


class Preperation:
    def __init__(self, data, filepath):
        self.data = data
        self.filepath = filepath+'/'

        os.chdir(self.filepath)

    def classify_above_100_as_noise(self):
        os.chdir(self.filepath)
        com = "/usr/local/bin/wine ~/LAStools/bin/lasheight -i {} -ignore_class 2 3 4 5 6 7 9 10 11 13" \
              "-classify_above 100.0 7 -do_not_store_in_user_data -drop_y_below 1 -odir klassifisert_stoy -olaz -cores 7".format(self.data)

        subprocess.call(com, shell=True)

    def classify_ground(self):
        os.chdir(self.filepath+"klassifisert_stoy")
        ground = "/usr/local/bin/wine ~/LAStools/bin/lasground.exe -i {} -o {} -odir ground_classified".format(self.data, self.data)
        subprocess.call(ground, shell=True)

    def make_dem(self):
        os.chdir(self.filepath+"klassifisert_stoy/"+"ground_classified")
        dem = "/usr/local/bin/wine ~/LAStools/bin/las2dem -i {} -step 2.0 -otif -keep_class 2 -elevation -odir {}".format(self.data, "DEM_2m")
        #int_dem = "/usr/local/bin/wine ~/LAStools/bin/las2dem -i {} -step 2.0 -otif -keep_class 2 -intensity -odir {}".format(self.data, "INT_DEM_2m")
        int_dem_keep_double = "/usr/local/bin/wine ~/LAStools/bin/las2dem -i {} -step 2.0 -otif -keep_double -intensity -odir {}".format(self.data, "keep_double")
        subprocess.call(dem, shell=True)
        #subprocess.call(int_dem, shell=True)
        subprocess.call(int_dem_keep_double, shell=True)

    def run_all(self):
        self.classify_above_100_as_noise()
        self.classify_ground()
        self.make_dem()

    def return_dems(self):
        elevation_data = self.filepath+"klassifisert_stoy/ground_classified/DEM_2m/{}".format(self.data.replace(".laz", ".tif"))
        int_data = self.filepath+"klassifisert_stoy/ground_classified/keep_double/{}".format(self.data.replace(".laz", ".tif"))
        return elevation_data, int_data
