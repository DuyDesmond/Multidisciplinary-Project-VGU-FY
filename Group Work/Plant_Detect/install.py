print("========================")
print("Starting up...")
print("========================", end="\n\n")

enablePushBullet = True if input("We support Pushbullet for sending notification. Do you want to enable Pushbullet (y/n)? ") == "y" else False
print()

from time import sleep
from platform import python_version_tuple
import os
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

librariesName = ["adafruit-io", "tensorflow", "keras", "opencv-python", "pyserial"]
TIME_DELAY = 0.3
flag = False

if enablePushBullet == True:
    librariesName.append("pushbullet.py")

librariesStatus = [True for _ in range(len(librariesName))]

try:
    import Adafruit_IO
except:
    librariesStatus[0] = False
    flag = True

try:
    import tensorflow
except:
    librariesStatus[1] = False
    flag = True

try:
    import keras
except:
    librariesStatus[2] = False
    flag = True

try: 
    import cv2
except:
    librariesStatus[3] = False
    flag = True

try:
    import serial
except:
    librariesStatus[4] = False
    flag = True

if enablePushBullet == True:
    try: 
        from pushbullet import PushBullet
    except:
        librariesStatus[5] = False
        flag = True

sleep(TIME_DELAY) #slowing down the script

print("Checking Python version...")

sleep(TIME_DELAY)

pythonVersion = python_version_tuple()
print(f"Python {'.'.join(pythonVersion)}", end=" - ")

if pythonVersion[0] == "3" and pythonVersion[1] == "11":
    print("OK", end="\n\n")
else:
    print("Mismatched Python version, expected Python 3.11", end="\n\n")
    flag = True

sleep(TIME_DELAY)

print("Checking Python libraries...")

sleep(TIME_DELAY)

for index in range(len(librariesName)):
    print(f"{librariesName[index]} - {'OK' if librariesStatus[index] == True else 'Not found. Please check if you have installed this library correctly.'}")
    sleep(TIME_DELAY)

print()

if flag:
    print("Please resolve the issue(s) above before trying again. Exiting...")
    sys.exit()

print("========================")
print("Configuring system...")
print("========================", end="\n\n")

adaUsername = input("Please enter your Adafruit IO username: ")
adaKey = input("Please enter your Adafruit IO key: ")
portName = input("Please enter the name of the port that the AIoT Kit is connected to: ")

if enablePushBullet == True:   
    while True:
        pushbulletKey = input("Please enter your Pushbullet key: ")
    
        try:
            pb = PushBullet(pushbulletKey)
            break
        except:
            print("Invalid Pushbullet key. Please try again.", end="\n")
    
    devices = pb.devices

    print()
    print("List of devices associated with this Pushbullet key:")
    
    for index in range(len(devices)):
        print(f"[{index}]: {devices[index].nickname}")
    
    print()    
    selectedPBDevice = pb.devices[int(input(f"Please enter the index of the device you want the notifications to be sent to (0 - {len(devices)-1}): "))].nickname

try:
    settingFile = open("config", "w")
except:
    print("Cannot write settings! Please ensure that write permission is allowed.")
    print("Alternatively, you can open the 'config' file with these:")
    print()
    print("AIO_USERNAME=[your Adafruit IO username]")
    print("AIO_KEY=[Your Adafruit IO Key]")
    print("PORT=[Name of the port that the AIoT Kit is connected to]")
    print("ENABLE_PUSH_BULLET=[true/false]")
    print("PUSH_BULLET_TOKEN=[your Pushbullet token]")
    print("PUSH_BULLET_DEVICE=[the nickname of the device you want Pushbullet notification to be sent to]")
    print()
    print("Exiting...")
    sys.exit()

settingFile.write(f"AIO_USERNAME={adaUsername}\n")
settingFile.write(f"AIO_KEY={adaKey}\n")
settingFile.write(f"PORT={portName}\n")

if enablePushBullet == True:
    settingFile.write(f"ENABLE_PUSH_BULLET=true\n")
    settingFile.write(f"PUSH_BULLET_TOKEN={pushbulletKey}\n")
    settingFile.write(f"PUSH_BULLET_DEVICE={selectedPBDevice}\n")
else:
    settingFile.write(f"ENABLE_PUSH_BULLET=false\n")
    settingFile.write(f"PUSH_BULLET_TOKEN=\n")
    settingFile.write(f"PUSH_BULLET_DEVICE=\n")

settingFile.close()

sleep(TIME_DELAY)
print()
print("Setup complete! Exiting...")