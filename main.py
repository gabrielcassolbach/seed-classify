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

def get_next_image_number(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return 0
    existing_files = [f for f in os.listdir(folder_path) if f.endswith(".jpg")]
    if not existing_files:
        return 0
    max_number = max([int(f.split(".")[0]) for f in existing_files])
    return max_number + 1

def seed_processing(modelManager, camera):
    image = camera.takePicture()
    try:
        image = camera.cropImage(image)
        results = modelManager.classifyImage(image)
    except Exception as e:
        print(f"Img unknown: {e}")
        return -1, None
    return results, image

def classify_seed(modelManager, camera, serialManager):
    results, image = seed_processing(modelManager, camera)
    if results == -1:
        return "unknown"
    
    max_value = 0
    choice = ""
    print(results)
    for key, value in results.items():
        if value > max_value:
            max_value = value
            choice = key

    # Apply the new rule: If "silkcut" and "broken" are both below 75%, classify as "pure"
    if results.get("silkcut", 0) < 0.96 and results.get("broken", 0) < 0.96:
        choice = "pure"
        max_value = 1.0  # Force high confidence for "pure"

    folder = "unknown"
    if max_value < 0.5:
        serialManager.sendMessage("unknown")
    elif choice == "pure":
        folder = "regular"
        serialManager.sendMessage("regular")
    else:
        folder = "irregular"
        serialManager.sendMessage("irregular")
    
    # Uncomment to save images and enhance model
    # next_image_number = get_next_image_number("images/"+folder)
    # cv2.imwrite(f"images/{folder}/{next_image_number}.jpg", image)
    return choice


def main():
    dir_path = None
    modelfile = None
    modelManager = None
    camera = None
    data = {
        "pure": 0,
        "silkcut": 0,
        "broken": 0,
        "unknown": 0
    }
    state = ["boot", "idle", "sync", "ready", "processing", "saving"]
    it = 0
    detected = False
    ble_thread = None
    serialManager = SerialManager()
    
    ble_server = BleApplication()
    ble_server.add_service(ProcessService(0))
    ble_server.register()
    ble_advertisement = MachineProcessAdvertisement(0)
    ble_advertisement.register()
    
    def start_ble_server():
        ble_server.run()

    while True:
        if state[it] == "boot":
            serialManager.sendMessage("set_idle")
            it = 1

        if state[it] == "idle":
            message = serialManager.receiveMessage()
            if message == "set_ready":
                it = 3
            if ble_thread is None or not ble_thread.is_alive():
                ble_thread = threading.Thread(target=start_ble_server, daemon=True)
                ble_thread.start()

        if state[it] == "ready":
            dir_path = os.path.dirname(os.path.realpath(__file__))
            modelfile = os.path.join(dir_path, "modelfile.eim")
            modelManager = ModelManager(modelfile)
            data = {
                "pure": 0,
                "silkcut": 0,
                "broken": 0,
                "unknown": 0
            }
            message = serialManager.receiveMessage()
            if message == "set_idle":
                it = 1
            elif message == "set_processing":
                detected = True
                it = 4

        if state[it] == "processing":
            if detected:
                camera = CameraManager(camera_type="usb", usb_camera_index=0)
                seed_type = classify_seed(modelManager, camera, serialManager)
                data[seed_type] += 1
                detected = False
                camera.releaseCamera()

            message = serialManager.receiveMessage()
            if message == "detected":
                detected = True
            elif message == "set_saving":
                it = 5

        if state[it] == "saving":
            modelManager.releaseRunner()
            storageManager = StorageManager(data)
            storageManager.insert_data()
            serialManager.sendMessage("set_idle")
            it = 1
            data = {
                "pure": 0,
                "silkcut": 0,
                "broken": 0,
                "unknown": 0
            }

if __name__ == "__main__":
   main()
