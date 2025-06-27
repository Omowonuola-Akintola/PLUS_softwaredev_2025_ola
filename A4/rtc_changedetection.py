"""

This script will allow users compute change detection with radiometrically and corrected (RTC) SAR image. The change detection will be 
performed by stacking the RTC into a multiband image that allows user to display different times of the year at the same time, 
using the color bands to highlight areas that differ in radar backscatter.

The script accept SAR image in .tiff format and an Area of interest (aoi) data in geojson format.

The script requires rioxarray, numpy, matplotb

This file can be imported as a module and contain the following functions:

load_rtc_image
normalize_image
crop_to_common_extent
stack_rtc_image
colorize_rtc_band
display_change

"""
import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt

def load_rtc_image(file_path):
    """
    Loads a single RTC backscatter GeoTIFF image.

    This function uses rasterio to read the first band of the given GeoTIFF file
    and returns it as a numpy array.

    Arguments:
        file_path (str): Path to the RTC GeoTIFF file.

    Returns:
        np.ndarray: 2D array containing the RTC backscatter values.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        rasterio.errors.RasterioIOError: If the file cannot be read as a raster.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found.")
    with rasterio.open(file_path) as src:
        data = src.read(1)
    return data

def normalize_image(img, minval=-20, maxval=0):
    """
    Normalizes a 2D backscatter array to the 0–1 range for visualization.

    This function clips the input array based on specified min and max values
    (or uses the 2nd and 98th percentiles by default), then scales the data
    linearly to fit between 0 and 1.

    Arguments:
        img (np.ndarray): 2D input array.
        minval (float, optional): Minimum value for scaling. Defaults to 2nd percentile.
        maxval (float, optional): Maximum value for scaling. Defaults to 98th percentile.

    Returns:
        np.ndarray: Normalized 2D array with values between 0 and 1.
    """
    if minval is None:
        minval = np.percentile(img, 2)
    if maxval is None:
        maxval = np.percentile(img, 98)
    norm = np.clip((img - minval) / (maxval - minval), 0, 1)
    return norm

def crop_to_common_extent(*images):
    """
    Crops multiple 2D arrays to their smallest shared extent.

    This ensures all images have the same shape for stacking.
    Images are cropped from their top-left corner to match
    the minimum number of rows and columns found across inputs.

    Arguments:
        *images: Variable number of 2D numpy arrays.

    Returns:
        list: A list of cropped 2D numpy arrays with identical shapes.
    """
    min_rows = min(img.shape[0] for img in images)
    min_cols = min(img.shape[1] for img in images)
    return [img[0:min_rows, 0:min_cols] for img in images]

def stack_rtc_images(img1, img2, img3):
    """
    Stacks three normalized RTC images into a 3-band composite.

    The images will be assigned to separate bands (R, G, B) in the order provided.
    This is useful for visualizing seasonal change.

    Arguments:
        img1 (np.ndarray): Normalized image for the first year (e.g., assigned to Red).
        img2 (np.ndarray): Normalized image for the second year (e.g., assigned to Green).
        img3 (np.ndarray): Normalized image for the third year (e.g., assigned to Blue).

    Returns:
        np.ndarray: 3D array with shape (3, height, width) representing the stacked RGB image.
    """
    return np.stack([img1, img2, img3], axis=0)

def colorize_rtc_stack(stack):
    """
    Converts a stacked RTC multiband array into an RGB display image.

    This function rearranges the dimensions from (bands, height, width)
    to (height, width, bands) to match image display expectations.

    Arguments:
        stack (np.ndarray): 3D array with shape (3, height, width).

    Returns:
        np.ndarray: RGB image with shape (height, width, 3), suitable for plotting.
    """
    return np.transpose(stack, (1, 2, 0))

def display_change(rgb_img, title="Seasonal Change Visualization"):
    """
    Displays a color composite image showing seasonal change across three years.

    Uses matplotlib to render the RGB image with a specified title.

    Arguments:
        rgb_img (np.ndarray): 3D array with shape (height, width, 3) containing RGB data.
        title (str): Title for the plot window.
    """
    plt.figure(figsize=(10, 10))
    plt.imshow(rgb_img)
    plt.title(title)
    plt.axis('off')
    plt.show()

 
