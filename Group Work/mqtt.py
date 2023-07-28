import time
import random
import sys
from Adafruit_IO import MQTTClient
from keras.models import load_model  # TensorFlow is required for Keras to work
from PIL import Image, ImageOps  # Install pillow instead of PIL
import numpy as np
import cv2
from plant_detect_webcam import plant_detector

# # Load the model
# model = load_model("keras_Model.h5", compile=False)

# # Load the labels
# class_names = open("labels.txt", "r").readlines()

# camera = cv2.VideoCapture(0)

# def plant_detector():
#     ret, image = camera.read()
    
#     image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
    
#     cv2.imshow("Plant Detector", image)
    
#     image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
#     image = (image / 127.5) - 1
    
#     prediction = model.predict(image)
#     index = np.argmax(prediction)    
#     class_name = class_names[index]
#     confidence_score = prediction[0][index]
    
#     print("Class:", class_name[2:], end="")
#     print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

configFile = open("config")
config = configFile.read().split("\n")

AIO_USERNAME = config[0].strip().split("=")[-1]
AIO_KEY = config[1].strip().split("=")[-1]
PUSH_BULLET_TOGGLE = True if config[3].strip().split("=")[-1] == "true" else False

if PUSH_BULLET_TOGGLE:
    #Imports Pushbullet library if the user wishes to have notifications
    from pushbullet import PushBullet 
    DEVICE_ACCESS_TOKEN = config[4].strip().split("=")[-1]

    #Create a PushBullet Instance with the access token
    pb = PushBullet(DEVICE_ACCESS_TOKEN)

    # Get the device you want to push to
    device = pb.get_device(config[5].strip().split("=")[-1])

configFile.close()

def connected(client):
    client.subscribe("lightsensor")
    client.subscribe("moistsensor")
    client.subscribe("on-slash-off")
    client.subscribe("rainsensor")
    client.subscribe("reservoir")
    client.subscribe("tempsensor")
    client.subscribe("schedule")
    client.subscribe("plant_detect")
    print("Server connected ...")

def subscribe(client , userdata , mid , granted_qos):
    print("Subscribed!")

def disconnected(client):
    print("Disconnected from the server!")
    sys.exit (1)

def message(client , feed_id , payload):
    print(f"Received payload from \"{feed_id}\": {payload}")
    if (feed_id == "schedule"):
        print(f"Manual timeout override: \"{payload}\"")
        time.sleep(int(payload))

client = MQTTClient(AIO_USERNAME , AIO_KEY)

client.on_connect = connected  #callback
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe

client.connect()
client.loop_background()

#Detect which sensor has malfunctioned
def Sensor_Checkup(sun_sensor_check, rain_sensor_check, moist_sensor_check, temp_sensor_check):
    sensor_list = []
    if sun_sensor_check == False:
        sensor_list.append("Sun sensor")
    if rain_sensor_check == False:
        sensor_list.append("Rain sensor")
    if moist_sensor_check == False:
        sensor_list.append("Moist sensor")
    if temp_sensor_check == False:
        sensor_list.append("Temp sensor")
    return sensor_list

moisture = 0
reservoir = 100
malfunctionNotified = False
is_daytime = True
is_rainy = False
plantDetected = plant_detector()

while True:
    # Call plant_detector function to capture images and make predictions
    plant_detector()
    client.publish("plant_detector", plantDetected)
    time.sleep(1)
    
    # Reservoir amount
    client.publish("reservoir", reservoir)
    time.sleep(2)
    # Whether it's day or night/ raining or not.
    sun = random.randint(0,1) # Day (5am - 7pm)/Night (7pm - 5am).
    rain =random.randint(0,1) # Rain
    client.publish("lightsensor", sun)
    client.publish("rainsensor", rain)
    time.sleep(3)
    
    #Check if sensors work
    
    #sun sensor
    if (isinstance(sun, int)): 
        Sun_sensor_check = True
    else: Sun_sensor_check = False
    
    #rain sensor
    if (isinstance(rain, int)): 
        Rain_sensor_check = True
    else: Rain_sensor_check = False


    # Daytime  
    if sun == 1:  
        temp = random.randint(30, 35)
    # Nighttime
    else:
        temp = random.randint(25,29)
        is_daytime = False
        #Should add a line to keep the pump from functioning here

    #temperature sensor
    if (isinstance(temp, int)): 
        Temp_sensor_check = True
    else: Temp_sensor_check = False

    # Rain
    if rain == 1:
        client.publish("tempsensor", temp-2)
        time.sleep(1)
        client.publish("moistsensor", 100)
        time.sleep(1)
        client.publish("on-slash-off", 0)
        time.sleep(1)
        is_rainy = True
    # No rain
    else:
        client.publish("tempsensor", temp)
        time.sleep(1)   
        moisture = random.randint(50,99)
        client.publish("on-slash-off", 1)
        time.sleep(1)
        client.publish("moistsensor", moisture)
        time.sleep(1)
    
    #When moisture data comes in
    #moisture sensor
    if (isinstance(moisture, int)): 
        Moist_sensor_check = True
    else: Moist_sensor_check = False

    #Notification with PushBullet
    if PUSH_BULLET_TOGGLE:
        if(reservoir <= 0):
            pb.push_note("Water ran out, ", "Requesting refill", device=device)
    
        #Rain-detection notification 
        if is_rainy:
            pb.push_note("Rain detected", "Pump will stop functioning", device=device)

        #Plant detection notification
        if not plantDetected:
            pb.push_note("No plant detected", "The system has stopped", device=device)
        
        #Nighttime turn off (It is recommended that smart watering systems turn off at night)
        if not is_daytime:
            pb.push_note("Nighttime mode", "Sunlight undetected, stop watering for the night", device=device)

        #Sensor malfunction notification
        if not malfunctionNotified: 
            if (Sun_sensor_check == False or Rain_sensor_check == False or Moist_sensor_check == False or Temp_sensor_check == False):
                pb.push_note("One or more of the sensors may not be functioning correctly", "Request checkup", device=device)
                print("Detected System Anomaly, Locating Abnormal Sensor(s)...")
                AbnormalSensorList = Sensor_Checkup(Sun_sensor_check, Rain_sensor_check, Moist_sensor_check, Temp_sensor_check)
                for index in AbnormalSensorList: print("Abnormal sensor(s) include: " + ', '.join(AbnormalSensorList))
                malfunctionNotified = True

    #Pause for 12 seconds
    time.sleep(12)
