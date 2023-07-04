print("Sensors and Actuators")

import time
import serial.tools.list_ports

try:
    ser = serial.Serial(port="COM8", baudrate=115200)
except:
    print("Can not open the port")

def sendCommand(cmd):
    global ser
    ser.write(cmd.encode())
    
while True: 
    print("Testing commands")
    sendCommand("2")
    time.sleep(2)
    sendCommand("3")
    time.sleep(2)
    sendCommand("4")
    time.sleep(2)
    sendCommand("5")
    time.sleep(2)    