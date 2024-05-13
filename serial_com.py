import serial
import socketio, time
import zmq
import sys
import json

context = zmq.Context()

# Create a ZeroMQ subscriber
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://0.0.0.0:5555")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

# Create a ZeroMQ publisher
publisher = context.socket(zmq.PUB)
publisher.bind("tcp://*:5556")

print("allow time for zmq to connect")
time.sleep(1)

publisher.send_string("serial starting")

# Serial port configuration
try:
    ser = serial.Serial('/dev/ttyACM0', 115200)
    publisher.send_string("serial active")
    print("serial connected")

except serial.SerialException:
    publisher.send_string("serial failedToConnect")
    print("Failed to connect to serial port. Exiting...")
    sys.exit(1)

# Receive and process messages
while True:
    # Receive a message
    data = subscriber.recv_string()
    # try:
    print(f"raw input '{data}'")
    value = json.loads(data.split(' ',1)[1])['value']
    # print(f"Received value '{value}'")
    print(round(value*90 + 90))
    ser.write(str(round(value*90 + 90)).encode())
    ser.write(b'\n')
    # except:
    #     print("error")