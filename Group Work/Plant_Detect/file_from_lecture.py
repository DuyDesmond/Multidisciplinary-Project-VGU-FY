import time
from keras.models import load_model  # TensorFlow is required for Keras to work
from PIL import Image, ImageOps  # Install pillow instead of PIL
import numpy as np
import cv2

# Load the model
model = load_model("keras_Model.h5", compile=False)

# Load the labels
class_names = open("labels.txt", "r").readlines()

camera = cv2.VideoCapture(0)

def plant_detector():
    
    ret, image = camera.read()
    
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
    
    cv2.imshow("Plant Detector", image)
    
    image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
    
    image = (image / 127.5) - 1
    
    prediction = model.predict(image)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]
    
    print("Class:", class_name[2:], end="")
    print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")
    
while True:
    plant_detector()
    time.sleep(1)
    
