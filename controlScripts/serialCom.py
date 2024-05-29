import serial
import socketio, time
import zmq
import sys
import json
import signal
import threading

# Ensures the program gets shut down and doesn't hang on waiting for serial data
signal.signal(signal.SIGINT, signal.SIG_DFL)

context = zmq.Context()

subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://127.0.0.1:5555")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "serial")

publisher = context.socket(zmq.PUB)
publisher.connect("tcp://127.0.0.1:5556")

print("allow time for zmq to connect")
time.sleep(1)

# Get config settings
configSettings = {}
with open("configuration/config.json", "r") as configData:
    # Load the JSON data
    configSettings = json.load(configData)

# Serial port configuration
try:
    ser = serial.Serial(configSettings.get('serialPort', '/dev/ttyACM0'), 115200) #/dev/ttyACM0 is the default, if config doesn't have it

    publisher.send_string("serial active")
    print("serial/out connected")

except serial.SerialException:
    publisher.send_string("serial failedToConnect")
    print("Failed to connect to serial port. Exiting...")
    sys.exit(1)

def read_from_port(ser):
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print("Received:", line)
            publisher.send_string("serial/out " + line)

thread = threading.Thread(target=read_from_port, args=(ser,))
thread.daemon = True
thread.start()

# Receive and process messages
while True:
    # Maybe there's a ZMQ message to send to serial?
    data = subscriber.recv_string()

    # OK. It didn't throw an error, so we'll use the data we got

    print(f"Received value '{data}'")
    ser.write(data.encode())
    ser.write(b'\n')