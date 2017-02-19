#### A NOVEL METHOD FOR AUTOMATION OF HYDRO BREAKLINE GENERATION FROM LIDAR DATA USING PYTHON

from skimage import filters
from load_hist import return_data, load_histogram, make_mod_histogram

data, scale = return_data()


### Return histogram based on data array in load_hist ###
def get_histogram(data):
    hist = load_histogram(data)
    return hist


### Loads and displays scaled histogram  ###
def load_normal_hist(data_array):
    no_smooth_hist = load_histogram(data_array)
    make_mod_histogram(data_array, 'Normal scale')
    return no_smooth_hist


### Makes the gaussian filter on data array ###
def gaussian(data):
    gaussian_filter = filters.gaussian(data, sigma=[0.25, 0.5])
    new_hist = get_histogram(gaussian_filter)

    return gaussian_filter, new_hist


### Loads and displays gaussian histogram ###
def load_gaussian_hist(data):
    gaussian_filter, new_hist = gaussian(data)
    make_mod_histogram(gaussian_filter, 'Gassian')


### Detects peaks based in Toscanos criteria. Returns which value in gaussian histogram that is a peak ###
### It turns out only key_left1 detects correct peaks. Why? ###

def detect_peaks(data):
    list_values = []
    list_keys = []
    gaussian_filter, hist = gaussian(data)
    print('Histogram', hist)
    newsorted = sorted(hist.items(), key=lambda t:t[0])

    for i,j in newsorted:
        list_values.append(j)
        list_keys.append(i)

    print('keys', list_keys)
    print('values', list_values)

    width_left1 = [list_values[n] for n in range(1, len(list_values)) if ((list_values[n-1] < list_values[n]*0.7071) == True and (((abs(list_values[n-1] - list_values[n]))*0.7071) > 1.4142*scale) == True)]
    width_right1 = [list_values[n] for n in range(1, len(list_values)-1) if ((list_values[n+1] < list_values[n]*0.7071) == True and (((abs(list_values[n+1] - list_values[n]))*0.7071) > 1.4142*scale) == True)]
    #width_right2 = [list_values[n] for n in range(1, len(list_values)-2) if ((list_values[n+2] < list_values[n]*0.7071) == True and (((abs(list_values[n+2] - list_values[n]))*0.7071) > 1.4142*scale) == True)]
    #width_left2 = [list_values[n] for n in range(1, len(list_values)-2) if ((list_values[n-2] < list_values[n]*0.7071) == True and (((abs(list_values[n-2] - list_values[n]))*0.7071) > 1.4142*scale) == True)]

    key_left1 = get_keys_to_values(width_left1)
    key_right1 = get_keys_to_values(width_right1)
    #key_left2 = get_keys_to_values(width_left2)
    #width_left2 = get_keys_to_values(width_right2)

    return key_left1, key_right1


### Returns which bin in the histogram that contains the selected value peak from detect_peaks function ###
def get_keys_to_values(valueslist):
    which_bin = []
    gaussian_filter, hist = gaussian(data)
    for i in valueslist:
        keys = [key for key, value in hist.iteritems() if value == i] #Finner ut hvilke bins som har gitte verdi.
        which_bin.append(keys)
    return which_bin


### Make ranges to each peak to detect the areas around each bin ###
def range_peaks(data):

    key_left1, key_right1 = detect_peaks(data)

    key_left1_r = [[peak[0], range(peak[0] - int(scale/3), peak[0] + int(scale/4))] for peak in key_left1]
    key_right1_r = [[peak[0], range(peak[0] - int(scale/3), peak[0] + int(scale/4))] for peak in key_right1]
    return key_left1_r, key_right1_r