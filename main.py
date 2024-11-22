import cv2
import os
import sys
import getopt
from camera_manager import CameraManager
from model_manager import ModelManager
from serial_manager import SerialManager

def seed_processing(modelManager, camera):
    image = camera.takePicture()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Converte a imagem para RGB
    
    results = modelManager.classifyImage(image)
    modelManager.saveImage(image)                   # Debug
       
    camera.releaseCamera()
    modelManager.releaseRunner()

    return data

def classify_seed(modelManager, camera, serialManager):
    results = seed_processing(modelManager, camera)
    max_value = 0
    choice = ""
    for key, value in results: 
        if(value > max_value):
            max_value = value
            choice = key
    if(max_value < 0.5):
        serialManager.sendMessage("unknown")
        return "unknown"
    elif(choice == "pure"):
        serialManager.sendMessage("regular")
        return choice
    else: 
        serialManager.sendMessage("irregular")
        return choice

def main(argv):
    # try:
    #     opts, args = getopt.getopt(argv, "h", ["--help"])
    # except getopt.GetoptError:
    #     help()
    #     sys.exit(2)

    # for opt, arg in opts:
    #     if opt in ('-h', '--help'):
    #         help()
    #         sys.exit()

    # if len(args) != 1:
    #     help()
    #     sys.exit(2)

    dir_path = None
    modelfile = None
    camera = None
    modelManager = None 
    data = {
        "pure": 0,
        "silkcut": 0,
        "discolored": 0,
        "broken": 0,
        "unknown": 0
    }

    state = ["boot", "idle", "sync", "ready", "processing", "saving"]
    state_it = 0
    model = "modelfile.eim"

    serialManager = SerialManager()
    # seed_processing(model)

    while True:
        if(state[it] == "boot"):
            serialManager.sendMessage("set_idle")
            state_it = 1

        if(state[it] == "idle"):
            message = serialManager.receiveMessage()
            if(message == "set_ready"):
                state_it = 3
            # TODO: IMPLEMENT BLUETOOTH
            # ELIF if(device is connected) sendMessage("set_sync") and state_it=2

        if(state[it] == "sync"):
            print("Sync State")
            # TODO: implement retrieve data from internal storage.
            # TODO: encode data 
            # TODO: send data using bluetooth
            # TODO: if(data was sended):
            # TODO:     delete data stored on raspberry pi -> state_it = 1

        if(state[it] == "ready"):
            dir_path = os.path.dirname(os.path.realpath(__file__))
            modelfile = os.path.join(dir_path, model)
            camera = CameraManager(camera_type="picamera")
            modelManager = ModelManager(modelfile) 
            data = {
                "pure": 0,
                "silkcut": 0,
                "discolored": 0,
                "broken": 0,
                "unknown": 0
            }
            message = serialManager.receiveMessage()
            if(message == "set_idle"):
                state_it = 1
            elif(message == "set_processing"):
                state_it = 4

        if(state[it] == "processing"):
            data[classify_seed(modelManager, camera, serialManager)] += 1
            message = serialManager.receiveMessage()
            while(message == None):
                message = serialManager.receiveMessage()
            if(message != "detected" and message == "set_saving"):
                state_it = 5
        
        if(state[it] == "saving"):
            # TODO: save data in json.
            serialManager.sendMessage("set_idle")
            state_it = 1


if __name__ == "__main__":
   main()
