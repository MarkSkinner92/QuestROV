import time
import zmq
import json
import math

context = zmq.Context()

publisher = context.socket(zmq.PUB)
publisher.connect("tcp://127.0.0.1:5556")

def sendJSON(topic,data):
    stringToSend = topic + " " + json.dumps(data)
    publisher.send_string(stringToSend)
    print("sent IMU data: " + stringToSend)

counter = 0
while True:
    data = {
        "pitch" : 20*math.sin(counter/10),
        "roll" : 50*math.sin(counter/10)
    }
    sendJSON("web/imu",data)
    counter += 1
    time.sleep(1/20)