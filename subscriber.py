from network import WLAN
from machine import Pin, PWM, Timer
import time
import umqtt.robust as umqtt

import lab10_upb2 as lab10

wifi = WLAN(WLAN.IF_STA)
wifi.active(True) 

# Variable Connection info
ssid = "Dyln"
password = "eesy7794"
port_number = 80

# Function to connect to wifi
def connect(wifi_obj, ssid, password, timeout=10):
    wifi_obj.connect(ssid, password) 

    while timeout > 0: 
        if wifi_obj.status() != 3: 
            time.sleep(1) 
            timeout -= 1 
        else: 
            return True 
    return False

# Attempt to connect to the wifi
if not connect(wifi, ssid, password):
    print("Wifi Not Connected")
else:
    print("Connected") 

# Raspberry Pi info
BROKER_IP = '10.111.224.91'
PORT = 8080
TOPIC = 'temp/pico'

OUTPUT_PIN = machine.Pin.OUT

# Setting up of MQTT Subscriber
mqtt = umqtt.MQTTClient(
    client_id = b'subscribe',
    server = BROKER_IP.encode(),
    port = PORT,
    keepalive = 7000
)

# Function to receive message and turn on light
def callback(TOPIC, message):
    proto_message = lab10.MeowMessage()
    proto_message.parse(message)
    store_temp(proto_message)
    avg_temp = 0
    for key, (temp, time_) in global_temp.items():
        avg_temp += temp
    if len(global_temp) > 0:
       avg_temp /= len(global_temp)
    led = machine.Pin('LED', OUTPUT_PIN)
    print(float(avg_temp))
    if float(avg_temp) >= 25:
        led.value(1)
    else:
        led.value(0)

global_temp = {}

def store_temp(proto_message):
    global global_temp
    global_temp[proto_message.client_id._value] = (proto_message.temperature._value,
                                                        proto_message.time._value)
    curr_time = time.time()
    
    print(global_temp)
        
    for key, (temp, time_) in global_temp.items():
        print(curr_time - time_)
        if curr_time - time_ > 600:
            del global_temp[key]
            
    
    print(global_temp)

    

mqtt.connect() # Connecting to the broker
mqtt.set_callback(callback) # Calling callback function
mqtt.subscribe(TOPIC) # Subscribes to the Topic

# Constantly checking for message from the broker
while True:
    mqtt.check_msg()
