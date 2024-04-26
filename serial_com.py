import serial
import socketio, time
import zmq
import sys

context = zmq.Context()

# Create a ZeroMQ subscriber
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://0.0.0.0:5555")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

# Create a ZeroMQ publisher
publisher = context.socket(zmq.PUB)
publisher.bind("tcp://*:5556")

#TODO use some kind of ack system instead of a blind delay
print("waiting for main app to acknowledge our serial node")
time.sleep(1)

publisher.send_string("serial starting")

# Serial port configuration
try:
    ser = serial.Serial('/dev/ttyACM0', 9600)
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
    print(f"Received content '{data}'")
    print(data)
    ser.write('e'.encode('utf-8'))
    ser.write(b'\n')  # Add a newline character if needed for proper termination