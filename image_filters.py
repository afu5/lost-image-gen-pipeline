import cv2
import numpy as np

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

# Future image processing functions would go here