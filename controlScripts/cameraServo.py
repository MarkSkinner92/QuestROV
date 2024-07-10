import RPi.GPIO as GPIO
import time
import zmq
import sys
import json

context = zmq.Context()

# Create a ZeroMQ subscriber
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://127.0.0.1:5555")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "man/")

state = 0
cycle = 4

cameraServoPin = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(cameraServoPin, GPIO.OUT)

try:
    with open('configuration/config.json') as configFile:
        configJson = json.load(configFile)
        print("Config File Loaded")
except:
    print("couldn't open config file, or thrusters : directions [] doesn't exist")
    p.stop()
    GPIO.cleanup()
    sys.exit()

defaultCamSettings = {
        "highPulse": 4,
        "midPulse" : 7,
        "lowPulse" : 10
    }
camSettings = configJson.get("cameraServo", defaultCamSettings)
camHighPulse = camSettings.get("highPulse",4)
camMidPulse = camSettings.get("midPulse",7)
camLowPulse = camSettings.get("lowPulse",10)

print("starting camera servo")
p = GPIO.PWM(cameraServoPin, 50)
p.start(camMidPulse)

print("started camera servo at pulse length:", camMidPulse)
p.ChangeDutyCycle(camMidPulse)
time.sleep(0.5)
p.ChangeDutyCycle(0)

# time.sleep(5)

# def moveServo():
#     global state
#     global cycle
#     while True:
#         if(state > 0):
#             cycle += 0.5
#         if(state < 0):
#             cycle -= 0.5
#         p.ChangeDutyCycle(cycle)
#         print(cycle)
#         time.sleep(0.2)

while True:
    stringData = subscriber.recv_string()

    data = stringData.split(' ',1)
    message = data[0]

    print(message,data[0])


    if(message == "man/moveCamera"):
        value = float(data[1])
        
        if(value == 1):
            p.ChangeDutyCycle(camHighPulse)
            time.sleep(0.2)
            p.ChangeDutyCycle(0)
            print(camHighPulse)

        if(value == 0):
            p.ChangeDutyCycle(camMidPulse)
            time.sleep(0.2)
            p.ChangeDutyCycle(0)
            print(camMidPulse)
        
        if(value == -1):
            p.ChangeDutyCycle(camLowPulse)
            time.sleep(0.2)
            p.ChangeDutyCycle(0)
            print(camLowPulse)
