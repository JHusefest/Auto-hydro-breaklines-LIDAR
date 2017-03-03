import matplotlib.pyplot as plt
import numpy as np
from skimage.segmentation import clear_border
from skimage.measure import label, find_contours, regionprops
from skimage.morphology import remove_small_holes
from skimage.restoration import denoise_bilateral, denoise_tv_chambolle
from analyze_elevation import range_peaks
from load_dem_hist import Loaddems
from lidar_prep import Preperation
from skimage.external.tifffile import imshow


class Analyze_Elevation:
    def __init__(self, elevation_data, int_data, scale):
        self.elevation_data = elevation_data.astype(float)
        self.int_data = int_data
        self.scale = scale

    def without_threshold_with_contours(self):

        #remove artifacts connected to image border
        cleared = self.elevation_data.copy()
        clear_border(cleared)

        #Insert peaks_left1 from analyze peaks

        range_peaks1, range_peaks2, range_peaks3, range_peaks4 = range_peaks(elevation_array, scale)

        for peak in range_peaks1:
            print(peak)
            for k in peak[1]:
                try:
                    hey = l.search_coords_by_key(k)
                    for i, j in hey:
                       cleared[i, j] = 0
                except KeyError:
                    print('Elevation finnes ikke', peak)

        #Denoising DEM
        denoised = denoise_bilateral(cleared, win_size=20, multichannel=False)

        # Finds countours within 6 meteres elevation.
        contours = find_contours(denoised, level=6, fully_connected='high')

        # Put all of the countours as HIGH VALUE. This will make threshold in elev_reomve_spikes() better. #

        for i in contours:
            for j, k in i.astype(int):
                denoised[j, k] = 100

        labeled = label(denoised)

        remove_holes = remove_small_holes(labeled, 1000)

        new_labeled = label(remove_holes, background=1)

        return new_labeled


### Removes artifacts like spikes and small holes in image ###
    def elev_remove_spikes(self):
        region_labeled = self.without_threshold_with_contours()

        regions = regionprops(region_labeled, self.elevation_data)

        for region in regions:
            area = region.area * 2 * 2
            if (area < 4026):
                region_labeled = np.where(region_labeled == region.label, 0, region_labeled)

        zero_area = np.unique(region_labeled)
        if len(zero_area) == 1:
            return None
        else:
            final_elev = remove_small_holes(region_labeled, 50)
            return final_elev


class Analyze_Int:
    def __init__(self, int_data):
        self.int_data = int_data

    def show_int(self):
        cleared = self.int_data.copy()
        clear_border(cleared)
        hey = np.where(cleared < 20, 0, cleared)
        h = np.where(cleared > 200, 800, hey)
        champ = denoise_tv_chambolle(h, weight=0.002, multichannel=False)
        yeah = np.where(champ < 0.002, 0, champ)

        contours = find_contours(yeah, level=0.001, fully_connected='high')
        for i in contours:
            for j, k in i.astype(int):
                hey[j, k] = 100

        region_labeled = label(hey)

        regions = regionprops(region_labeled, intensity_image=self.int_data)

        for region in regions:
            area = region.area * 2 * 2
            if area < 2026/3:
                region_labeled = np.where(region_labeled == region.label, 0, region_labeled)

        zero_area = np.unique(region_labeled)
        if len(zero_area) == 1:
            return None
        else:
            imshow(region_labeled)
            return region_labeled

    def show_keep_double(self):
        cleared = self.int_data.copy()
        clear_border(cleared)

        contours = find_contours(cleared, level=0.1, fully_connected='high')
        for i in contours:
            for j, k in i.astype(int):
                cleared[j, k] = 1000

        labeled = label(cleared)

        remove_holes = remove_small_holes(labeled, 300, connectivity=2)

        labeled2 = label(remove_holes, background=1)

        rm_inner_holes = remove_small_holes(labeled2, 400, connectivity=2)

        plt.show()

        return rm_inner_holes


class CombineData:
    def __init__(self, int_regions, elev_regions):
        #self.int_regions = int_regions
        #self.elev_regions = elev_regions

        if elev_regions is None:
            self.elev_regions = int_regions
        elif elev_regions is None and int_regions is None:
            print('Ingen funker..')
            pass
        else:
            self.elev_regions = elev_regions
            self.int_regions = int_regions

    def show_regions(self):
        imshow(self.elev_regions, 'Elevation Regions')
        imshow(self.int_regions, 'Intensity Regions')
        plt.show()


if __name__ == "__main__":
    p = Preperation("32-1-503-109-11.laz", "/Users/joakimtveithusefest/Documents/master_env/kragero_drangeland/422/data")
    #p.run_all()

    elev_file, int_file = p.return_dems()

    l = Loaddems(elev_file, int_file)

    try:
        elevation_array, int_data_array, scale = l.return_data()

        a = Analyze_Elevation(elevation_array, int_data_array, scale)

        elev_regions = a.elev_remove_spikes()

        j = Analyze_Int(int_data_array)

        int_regions = j.show_keep_double()

        combined = CombineData(int_regions, elev_regions)

        combined.show_regions()

    except TypeError:
        print('Her er det BARE vann', str(elev_file))

    #a = Analyze_Elevation(elevation_array, int_data_array, scale)

    #elev_regions = a.elev_remove_spikes()

    #j = Analyze_Int(int_data_array)

    #int_regions = j.show_keep_double()

    #combined = CombineData(int_regions, elev_regions)

    #combined.show_regions()