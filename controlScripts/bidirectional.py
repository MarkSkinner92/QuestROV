import serial
import socketio, time
import zmq
import json
import signal
import math

signal.signal(signal.SIGINT, signal.SIG_DFL)

context = zmq.Context()

subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://127.0.0.1:5555")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

publisher = context.socket(zmq.PUB)
publisher.connect("tcp://127.0.0.1:5556")

def sendJSON(topic,data):
    stringToSend = topic + " " + json.dumps(data)
    publisher.send_string(stringToSend)
    print("sent IMU data: " + stringToSend)

counter = 0
while True:
    stringData = subscriber.recv_string()
    print(stringData)

    data = {
        "pitch" : 20*math.sin(counter/10),
        "roll" : 50*math.sin(counter/10)
    }
    sendJSON("web/imu",data)
    counter += 1