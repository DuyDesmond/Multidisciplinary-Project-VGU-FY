import sys
import time
import random
import requests
import ast
from Adafruit_IO import MQTTClient

# Go here for the key: https://io.adafruit.com/DDesmond/overview

AIO_FEED_ID = "Multidisciplinary_Project"
AIO_USERNAME = "DDesmond"
AIO_KEY = "aio_aFLY82nfNdy2eIFMsIHq4ezLRZSs"

def modify_value(x1, x2, x3):
    global global_equation
    print("Equation: ", global_equation)
    result = eval(global_equation)
    print(result)
    return result

def connected(client):
    print("Server connected...")
    client.subscribe("button1")
    client.subscribe("button2")
    client.subscribe("equation")
    
global_equation = "x1 + x2 + x3" #global variable

def subscribe(client , userdata , mid , granted_qos):
    print("Subscribe thanh cong ...")

def disconnected(client):
    print("Ngat ket noi ...")
    sys.exit (1)
    
def message(client , feed_id , payload):
    global global_equation
    print("Received: " + payload)
    if(feed_id == "equation"):
        global_equation = payload
        print(global_equation)
        
def is_valid_expression(expr):
    try:
        ast.parse(expr)
        return True
    except SyntaxError:
        return False

def init_global_equation():
    global global_equation
    headers = {}
    aio_url = "https://io.adafruit.com/api/v2/DDesmond/feeds/equation"
    x = requests.get(url=aio_url, headers=headers, verify=False)
    data = x.json()
    global_equation = data["last_value"]
    
client = MQTTClient(AIO_USERNAME , AIO_KEY)

client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe

client.connect()
client.loop_background()

init_global_equation()

while True:
    time.sleep(5)
    s1 = random.randint(0,250)
    s2 = random.randint(0,150)
    s3 = random.randint(0,2000)
    client.publish("sensor1", s1)
    client.publish("sensor2", s2)
    client.publish("sensor3", s3)
    s4 = modify_value(s1, s2, s3)
    print(s4)
    client.publish("result of total sum",s4)
    
    pass
