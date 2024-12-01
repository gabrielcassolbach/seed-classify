import cv2
import numpy as np

input_image = cv2.imread("captured_image.jpg", cv2.IMREAD_UNCHANGED)

height = input_image.shape[0]
width = input_image.shape[1]

if len(input_image.shape) == 2:
    gray_input_image = input_image.copy()
else:
    gray_input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)

upper_threshold, thresh_input_image = cv2.threshold(
    gray_input_image, thresh=0, maxval=255, type=cv2.THRESH_BINARY + cv2.THRESH_OTSU
)

lower_threshold = 0.5 * upper_threshold

canny = cv2.Canny(input_image, lower_threshold, upper_threshold)
pts = np.argwhere(canny > 0)

y1, x1 = pts.min(axis=0)
y2, x2 = pts.max(axis=0)

output_image = input_image[y1:y2, x1:x2]
output_path = 'savedImage.jpg'
cv2.imwrite( output_path,  output_image)
