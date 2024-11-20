import cv2
import sys

class CameraManager:
    def __init__(self, camera_type = "usb", usb_camera_index=0):
        self.camera_type = camera_type.lower()    
        self.usb_camera_index = usb_camera_index
        self.camera = None
        if(camera_type == "usb"):
            self.camera = cv2.VideoCapture(self.usb_camera_index) 
        elif (camera_type == "picamera"):
            # ---- add code.
            raise ValueError("no camera!") 
        else:
            raise ValueError("no camera!") 
        

    def takePicture(self):
        if(self.camera_type == "usb"):
            ret, image = self.camera.read()
            if not ret:
                print("Erro ao capturar a imagem da câmera.")
                sys.exit(1)
            return image   
        else:
            print("implementar")
        
    def releaseCamera(self):
        if(self.camera_type == "usb"):
            self.camera.release()
            self.camera = None
        else:
            print("implementar")