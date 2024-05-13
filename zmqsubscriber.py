import serial
import socketio, time
import zmq
import sys
import json
import signal
    
signal.signal(signal.SIGINT, signal.SIG_DFL)
# any pyzmq-related code, such as `reply = socket.recv()`

context = zmq.Context()

# Create a ZeroMQ subscriber
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://127.0.0.1:5555")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "axis")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "key")

# Receive and process messages
while True:
    # Receive a message
    data = subscriber.recv_string()
    # try:
    print(f"raw input '{data}'")
    # except:
    #     print("error")