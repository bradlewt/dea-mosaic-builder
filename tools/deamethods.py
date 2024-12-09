from scipy.ndimage import uniform_filter
from scipy.ndimage import variance


# Function to apply lee filtering on S1 image. Speckle Filter
def lee_filter(da, size):
    """
    Apply lee filter of specified window size.
    Adapted from https://stackoverflow.com/questions/39785970/speckle-lee-filter-in-python

    """
    img = da.values
    img_mean = uniform_filter(img, size)
    img_sqr_mean = uniform_filter(img**2, size)
    img_variance = img_sqr_mean - img_mean**2

    overall_variance = variance(img)

    img_weights = img_variance / (img_variance + overall_variance)
    img_output = img_mean + img_weights * (img - img_mean)

    return img_output


# Classifier Function
def S1_water_classifier(da, threshold):
    water_data_array = da < threshold
    return water_data_array.to_dataset(name="s1_water")
