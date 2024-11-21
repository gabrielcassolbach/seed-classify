import cv2
import os
import sys
import getopt
from camera_manager import CameraManager
from model_manager import ModelManager

def help():
    print('Uso: python classify_camera.py <path_to_model.eim>')

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "h", ["--help"])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit()

    if len(args) != 1:
        help()
        sys.exit(2)

    model = args[0]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)

    camera = CameraManager(camera_type="picamera")
    modelManager = ModelManager(modelfile)
    
    image = camera.takePicture()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Converte a imagem para RGB
    
    modelManager.classifyImage(image)
    modelManager.saveImage(image)
       
    camera.releaseCamera()
    modelManager.releaseRunner()

if __name__ == "__main__":
   main(sys.argv[1:])
