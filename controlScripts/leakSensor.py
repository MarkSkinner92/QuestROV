import time
import zmq
import json
import RPi.GPIO as GPIO

print("Starting Leak Sensor Node...")

leakPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(leakPIN, GPIO.IN)

context = zmq.Context()

publisher = context.socket(zmq.PUB)
publisher.connect("tcp://127.0.0.1:5556")

print("Ready to Detect Leaks at 1hz")

counter = 0
while True:
    if(GPIO.input(leakPIN)):
        publisher.send_string("web/leak 1")
        time.sleep(3)
    time.sleep(0.5)
