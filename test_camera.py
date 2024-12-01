import cv2
import os
from camera_manager import CameraManager
from model_manager import ModelManager

def seed_processing(modelManager, camera):
    # image = camera.takePicture()  # Capture an image using the camera
    # cv2.imwrite("raw_image.jpg", image)  # Save the original image for debugging purposes
    
    # for testing without camera
    image = cv2.imread("corn_image_sample.jpg")

    
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB for model processing (I guess it is not needed because turns the image blue)
    # cv2.imwrite("converted.jpg", image)

    image = camera.cropImage(image)
    cv2.imwrite("cropped/cropped.jpg",image)
    results = modelManager.classifyImage(image)  # Classify the image using the model

    return results

def classify_seed(modelManager, camera):
    results = seed_processing(modelManager, camera)
    max_value = 0
    choice = ""
    for key, value in results.items():  # Iterate through classification results
        if value > max_value:
            max_value = value
            choice = key
    print(max_value)
    if max_value < 0.7:
        return "unknown"
    else:
        return choice

def main():
    # Path to the model file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, "modelfile.eim")  # Change this to your actual model file
    
    # Initialize the camera and model manager
    camera = CameraManager(camera_type="usb")  # Modify this if using another camera
    modelManager = ModelManager(modelfile)
    
    # Capture and classify just one image
    classification_result = classify_seed(modelManager, camera)
    
    # Print the classification result
    print(f"Classification result: {classification_result}")

if __name__ == "__main__":
    main()
