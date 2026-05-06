from enum import Enum
import cv2
import numpy as np
from PIL import Image as img

class Filter(Enum):
    BRIGHT_OBSTRUCTION = 0
    MOTION_BLUR = 1
    DARK_CURRENT_NOISE = 2

# img_path: path to the image to be blurred
# output_path: path to save the result image
# kernel_size: size of the motion blur kernel (larger kernel means stronger effect)
# angle (optional): defaults to 0, which is horizontal. Angle of motion blur,
#   in degrees, ccw from horizontal
def motion_blur(img_path: str, output_path: str, kernel_size: int, angle: float = 0):
  img = cv2.imread(img_path)

  kernel = np.zeros((kernel_size, kernel_size))
  kernel[int((kernel_size - 1) / 2)] = np.ones(kernel_size)

  center = (kernel_size / 2, kernel_size / 2)

  rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale=1)
  kernel = cv2.warpAffine(src=kernel, M=rotation_matrix, dsize=(kernel_size, kernel_size))
  kernel = (1 / kernel.sum()) * kernel

  result = cv2.filter2D(img, -1, kernel)
  cv2.imwrite(output_path, result)

"""
Dark Current Shot Noise
    We're given the equation σD_SHOT = sqrt(D), where D = t1DR,(Janesick, 167-168)

Sources
    James R Janesick, Photon Transfer
"""
# img_path: path to the image to have dark current noise added
# output_path: path to save the result image
# exposure (seconds): the exposure time on the photo
# dark_current_rate (electron/pixel/second): The dark current rate provided by the sensor manufacturer
# gain (optional, electron/pixel): The gain provided by the sensor manufacturer
# dark_current_fpn (optional, %): dark current FPN quality factor
def dark_current_noise_generator(img_path: str, output_path: str, exposure: float, dark_current_rate: float, gain: float = 1, dark_current_fpn: float = 0.25):
    # Opens image
    image = img.open(img_path)
    image_array = np.asarray(image)

    # Dark Current Shot Noise
    # Calculate poisson distribution for dark current shot noise
    dc_shot_lambda = exposure * dark_current_rate
    dc_shot_distribution = np.random.poisson(dc_shot_lambda, image_array.shape)
    # Need to factor in gain to convert electrons to pixel
    dc_shot_distribution = dc_shot_distribution/gain

    # Dark Current FPN
    # Calculate poisson distribution for dark current FPN
    # Using 0.25 because it's the average of 0.1 and 0.4, see page 168 of Photon Transfer
    dc_fpn_lambda = (exposure * dark_current_rate * dark_current_fpn) ** 2
    # FPN follows gaussian distribution https://pmc.ncbi.nlm.nih.gov/articles/PMC12653213/
    dc_fpn_distribution = np.random.normal(0, dc_fpn_lambda, image_array.shape)
    # Need to factor in gain to convert electrons to pixel
    dc_fpn_distribution = dc_fpn_distribution/gain

    # Generate noise pixels where poisson distribution
    dark_current_array = image_array.astype(np.float32) + dc_shot_distribution.astype(np.float32) + dc_fpn_distribution.astype(np.float32)
    dark_current_array = np.clip(dark_current_array, 0, 255).astype(np.uint8)

    # Save the darkened image
    dark_current_image = img.fromarray(dark_current_array)
    dark_current_image.save(output_path)

# Future image processing functions would go here