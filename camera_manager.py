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
