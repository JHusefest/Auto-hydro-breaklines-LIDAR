from skimage.external.tifffile import imshow
import matplotlib.pyplot as plt
from load_hist import return_data, search_coords_by_key
from analyze_peaks import range_peaks, gaussian

import numpy as np
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border, mark_boundaries, find_boundaries, relabel_sequential
from skimage.measure import label, find_contours, regionprops
from skimage.morphology import closing, square, remove_small_holes, remove_small_objects
from skimage.restoration import denoise_bilateral
from skimage.color import label2rgb


data, scale = return_data()

gaussian_filter, new_hist = gaussian(data)


def without_threshold_with_contours():
    range_peaks1, range_peaks2 = range_peaks(data)
    #apply threshold

    #remove artifacts connected to image border
    cleared = gaussian_filter.copy()
    clear_border(cleared)

    #Insert peaks_left1 from analyze peaks

    for peak in range_peaks1:
        print(peak)
        for k in peak[1]:
            try:
                hey = search_coords_by_key(k)
                for i, j in hey:
                    cleared[i, j] = 0
            except KeyError:
                print('Elevation finnes ikke', peak)

    for peak in range_peaks2:
        print(peak)
        for k in peak[1]:
            try:
                hey = search_coords_by_key(k)
                for i, j in hey:
                    cleared[i, j] = 0
            except KeyError:
                print('Elevation finnes ikke', peak)


    # Denoising DEM
    denoised = denoise_bilateral(cleared, win_size=20, multichannel=False)

    # Finds countours within 6 meteres elevation.
    contours = find_contours(denoised, level=6, fully_connected='high')

    # Put all of the countours as HIGH VALUE. This will make threshold in elev_reomve_spikes() better. #

    for i in contours:
        for j, k in i.astype(int):
            denoised[j, k] = 100

    return denoised


### Removes artifacts like spikes and small holes in image ###
def elev_remove_spikes():
    denoised = without_threshold_with_contours()
    thresh = threshold_otsu(denoised)
    closed = closing(denoised > thresh, square(3))

    labeled = label(closed, connectivity=2)

    regions = regionprops(labeled, denoised)

    #### Removes areas which is greater than an acre ###
    for region in regions:
        area = region.area * 2 * 2
        if (area < 4026):
            labeled = np.where(labeled == region.label, 0, labeled)

    remove_holes = remove_small_holes(labeled, 1000, connectivity=2)

    binary_labeled = label(remove_holes, background=1)
    # label image regions

    breaklines_elevation = find_boundaries(binary_labeled, connectivity=2, background=0) ## USE FIND_BOUNDARIES IN FUTURE WORK

    imshow(binary_labeled, 'Labeled')
    plt.show()

    return remove_holes


if __name__ == "__main__":
    elev_remove_spikes()