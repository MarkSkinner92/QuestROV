import time
import zmq
import json
import math

context = zmq.Context()

publisher = context.socket(zmq.PUB)
publisher.connect("tcp://127.0.0.1:5556")

def sendString(topic,data):
    stringToSend = topic + " " + str(data)
    publisher.send_string(stringToSend)

counter = 0
while True:
    sendString("web/telem",counter)
   
    print("sent voltage")
    counter += 1
    time.sleep(1)