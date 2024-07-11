import serial
import socketio, time
import zmq
import json
import signal
import threading

# Ensures the program gets shut down and doesn't hang on waiting for serial data
signal.signal(signal.SIGINT, signal.SIG_DFL)

print("allow time for zmq to connect")
time.sleep(2)

# Get config settings
configSettings = {}
with open("configuration/config.json", "r") as configData:
    # Load the JSON data
    configSettings = json.load(configData)

context = zmq.Context()

subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://127.0.0.1:5555")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "serial")

publisher = context.socket(zmq.PUB)
publisher.connect("tcp://127.0.0.1:5556")

time.sleep(2)

# Serial port configuration
try:
    ser = serial.Serial(configSettings.get('serialPort', '/dev/ttyAMA1'), 9600) #/dev/ttyAMA1 is the default, if config doesn't have it
    print("serial/out connected")
    ser.write("$$screen=3=Serial Connected\r\n".encode())

except serial.SerialException:
    publisher.send_string("serial failedToConnect")
    print("Failed to connect to serial port. Exiting...")
    ser.write("$$screen=3=Serial Can't Connect\r\n".encode())

def read_from_port(ser):
    while True:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8')
                # line = ser.readline()
                print("Received:", line)
                publisher.send_string("serial/out " + line)
            except:
                print("error parsing")

thread = threading.Thread(target=read_from_port, args=(ser,))
thread.daemon = True
thread.start()

# Receive and process messages
while True:
    # Maybe there's a ZMQ message to send to serial?
    data = subscriber.recv_string()
    parts = data.split(" ")
    parts.pop(0)
    data = " ".join(parts)
    print(data)
    print(f"Sending {data} out the serial port")
    ser.write(data.encode())