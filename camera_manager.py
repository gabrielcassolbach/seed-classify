from picamera2 import Picamera2, Preview
import cv2
import sys
import numpy as np

class CameraManager:
    def __init__(self, camera_type = "usb", usb_camera_index=0):
        self.camera_type = camera_type.lower()    
        self.usb_camera_index = usb_camera_index
        #self.camera = None
        if(camera_type == "usb"):
            self.camera = cv2.VideoCapture(self.usb_camera_index) #self.usb_camera_index
        elif (camera_type == "picamera"):
            self.camera = Picamera2()
            preview_config = self.camera.create_still_configuration({'format': 'RGB888'})
            preview_config['size'] = (50, 50)  # Set resolution to 1920x1080
            self.camera.configure(preview_config)
        else:
            raise ValueError("no camera!")
            # print("No camera")
        

    def takePicture(self):
        if(self.camera_type == "usb"):
            ret, image = self.camera.read()
            if not ret:
                print("Erro ao capturar a imagem da câmera.")
                sys.exit(1)
            return image   
        else:
            self.camera.start()
            image = self.camera.capture_array()
            self.camera.stop()
            return image
        
    def releaseCamera(self):
        if(self.camera_type == "usb"):
            self.camera.release()
            self.camera = None
        else:
            print("implementar")

    def cropImage(self, image):
        height = image.shape[0]
        width = image.shape[1]
        if len(image.shape) == 2:
            gray_input_image = image.copy()
        else:
            gray_input_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        upper_threshold, thresh_input_image = cv2.threshold(
            gray_input_image, thresh=0, maxval=255, type=cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        lower_threshold = 0.5 * upper_threshold
        canny = cv2.Canny(image, lower_threshold, upper_threshold)
        pts = np.argwhere(canny > 0)

        y1, x1 = pts.min(axis=0)
        y2, x2 = pts.max(axis=0)
        # Give a little more edge to the image
        margin = 40  # Adjust this value to control how much extra edge to include
        y1 = max(0, y1 - margin)
        x1 = max(0, x1 - margin)
        y2 = min(height, y2 + margin)
        x2 = min(width, x2 + margin)

        output_image = image[y1:y2, x1:x2]
        return output_image

    # def cropImage(self, image):
    #     height, width = image.shape[:2]

    #     # Convert image to grayscale
    #     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #     # Apply GaussianBlur to reduce noise
    #     blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)

    #     # Apply Otsu's thresholding
    #     _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    #     # Invert the image if necessary (ensuring the seed is white)
    #     if np.mean(binary) > 127:
    #         binary = cv2.bitwise_not(binary)

    #     # Perform morphological opening to remove small noise
    #     kernel = np.ones((5,5), np.uint8)
    #     clean_binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)

    #     # Find contours
    #     contours, _ = cv2.findContours(clean_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #     if not contours:
    #         print("No seed detected!")
    #         return image  # Return original image if no seed is found

    #     # Find the largest contour (assuming it's the seed)
    #     largest_contour = max(contours, key=cv2.contourArea)

    #     # Get bounding box
    #     x, y, w, h = cv2.boundingRect(largest_contour)

    #     # Add margin
    #     margin = 40
    #     x1 = max(0, x - margin)
    #     y1 = max(0, y - margin)
    #     x2 = min(width, x + w + margin)
    #     y2 = min(height, y + h + margin)

    #     # Crop the image
    #     output_image = image[y1:y2, x1:x2]

    #     return output_image

    # def cropImage(self, image):
    #     height, width = image.shape[:2]

    #     # Convert to grayscale
    #     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #     # Apply Gaussian Blur to remove noise
    #     blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)

    #     # Apply Adaptive Thresholding
    #     binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                                 cv2.THRESH_BINARY, 11, 2)

    #     # Invert if needed
    #     if np.mean(binary) > 127:
    #         binary = cv2.bitwise_not(binary)

    #     # Perform morphological opening
    #     kernel = np.ones((5,5), np.uint8)
    #     clean_binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)

    #     # Find contours
    #     contours, _ = cv2.findContours(clean_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #     if not contours:
    #         print("No seed detected!")
    #         return image  # Return original if no seed found

    #     # Select the largest contour (if it's large enough)
    #     contours = [c for c in contours if cv2.contourArea(c) > 500]  # Ignore small noise
    #     if not contours:
    #         print("No valid seed detected!")
    #         return image

    #     largest_contour = max(contours, key=cv2.contourArea)
    #     x, y, w, h = cv2.boundingRect(largest_contour)

    #     # Apply margin and ensure within bounds
    #     margin = 40
    #     x1, y1 = max(0, x - margin), max(0, y - margin)
    #     x2, y2 = min(width - 1, x + w + margin), min(height - 1, y + h + margin)

    #     # Crop and return
    #     output_image = image[y1:y2, x1:x2]
        
    #     return output_image

    # def cropImage(self, image):
    #     height, width = image.shape[:2]

    #     # Convert to grayscale
    #     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #     # Apply Gaussian Blur to remove noise
    #     blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)

    #     # Apply Adaptive Thresholding
    #     binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                                 cv2.THRESH_BINARY, 11, 2)

    #     # Invert if needed
    #     if np.mean(binary) > 127:
    #         binary = cv2.bitwise_not(binary)

    #     # Perform morphological opening
    #     kernel = np.ones((5,5), np.uint8)
    #     clean_binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)

    #     # Find contours
    #     contours, _ = cv2.findContours(clean_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #     if not contours:
    #         print("No seed detected!")
    #         return image  # Return original if no seed found

    #     # Select the largest contour (if it's large enough)
    #     contours = [c for c in contours if cv2.contourArea(c) > 500]  # Ignore small noise
    #     if not contours:
    #         print("No valid seed detected!")
    #         return image

    #     largest_contour = max(contours, key=cv2.contourArea)
    #     x, y, w, h = cv2.boundingRect(largest_contour)

    #     # Reduce margin for a tighter crop
    #     margin = 20  # Smaller margin means more zoom
    #     x1, y1 = max(0, x - margin), max(0, y - margin)
    #     x2, y2 = min(width - 1, x + w + margin), min(height - 1, y + h + margin)

    #     # Crop the image
    #     cropped_image = image[y1:y2, x1:x2]

    #     # Resize to make it appear more zoomed-in (scale by 1.5x)
    #     zoomed_image = cv2.resize(cropped_image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    #     return zoomed_image

