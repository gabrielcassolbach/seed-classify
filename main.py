import cv2
import os
import sys
import getopt
import threading
from camera_manager import CameraManager
from model_manager import ModelManager
from serial_manager import SerialManager
from gatt_server_manager import BleApplication, MachineProcessAdvertisement, ProcessService
from storage_manager import StorageManager
from time import sleep

def seed_processing(modelManager, camera):
    image = camera.takePicture()
    
    # test if it is needed to convert the image
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Converte a imagem para RGB
    # modelManager.saveImage(image)                   # Debug

    image = camera.cropImage()
    cv2.imwrite("cropped_image.jpg", image)

    results = modelManager.classifyImage(image)
    return results

def classify_seed(modelManager, camera, serialManager):
    results = seed_processing(modelManager, camera)
    max_value = 0
    choice = ""
    print(results)
    for key, value in results.items(): 
        if(value > max_value):
            max_value = value
            choice = key
    
    if(max_value < 0.7):
        serialManager.sendMessage("unknown")
        return "unknown"
    elif(choice == "pure"):
        serialManager.sendMessage("regular")
        return choice
    else: 
        serialManager.sendMessage("irregular")
        return choice 

def main():
    dir_path = None
    modelfile = None  # Change this to your actual model file
    modelManager = None 
    camera = None
    data = {
        "pure": 0,
        "silkcut": 0,
        # "discolored": 0,
        "broken": 0,
        "unknown": 0
    }
    #          0        1      2        3         4           5 
    state = ["boot", "idle", "sync", "ready", "processing", "saving"]
    it = 0
    detected = False
    ble_thread = None

    serialManager = SerialManager()
    
    # ble server
    ble_server = BleApplication()
    ble_server.add_service(ProcessService(0))
    ble_server.register()
    ble_advertisement = MachineProcessAdvertisement(0)
    ble_advertisement.register()
    
    def start_ble_server():
        ble_server.run()

    while True:
        if(state[it] == "boot"):
            serialManager.sendMessage("set_idle")
            it = 1

        if(state[it] == "idle"):
            message = serialManager.receiveMessage()
            if(message == "set_ready"):
                it = 3
            if ble_thread is None or not ble_thread.is_alive():
                ble_thread = threading.Thread(target=start_ble_server, daemon=True)
                ble_thread.start()
            # ELIF if(device is connected) sendMessage("set_sync") and it=2
            # THIS WILL BE IMPLEMENTED INSIDE THE StartNotify function on "gatt_server_manager.py"

            # THIS IS IMPLEMENtED INSIDE THE gatt_server_manager
            # if(state[it] == "sync"):
            #     print("Sync State")
                # TODO: implement retrieve data from internal storage.
                # TODO: encode data 
                # TODO: send data using bluetooth
                # TODO: if(data was sended):
                # TODO:     delete data stored on raspberry pi -> it = 1

        if(state[it] == "ready"):
            dir_path = os.path.dirname(os.path.realpath(__file__))
            modelfile = os.path.join(dir_path, "modelfile.eim")  # Change this to your actual model file
            modelManager = ModelManager(modelfile) 
            data = {
                "pure": 0,
                "silkcut": 0,
                # "discolored": 0,
                "broken": 0,
                "unknown": 0
            }
            message = serialManager.receiveMessage() 
            if(message == "set_idle"):
                it = 1
            elif(message == "set_processing"):
                print("set_processing")
                detected = True
                camera = CameraManager(camera_type="usb", usb_camera_index=0)
                it = 4


        if(state[it] == "processing"):
            if detected:
                seed_type = classify_seed(modelManager, camera, serialManager)
                data[seed_type] += 1
                detected = False

            message = serialManager.receiveMessage()
            if message == "detected":
                detected = True
            elif message == "set_saving":
                it = 5
        
        if(state[it] == "saving"):
            camera.releaseCamera()
            modelManager.releaseRunner()
            storageManager = StorageManager(data)
            storageManager.insert_data()
            serialManager.sendMessage("set_idle")
            it = 1
            data = {
                "pure": 0,
                "silkcut": 0,
                # "discolored": 0,
                "broken": 0,
                "unknown": 0
            }
           

    
if __name__ == "__main__":
   main()
   
