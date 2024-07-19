import serial
import socketio, time
import zmq
import json
import threading
import sys

context = zmq.Context()

subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://127.0.0.1:5555")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "serial")

publisher = context.socket(zmq.PUB)
publisher.connect("tcp://127.0.0.1:5556")

killIfWaitingTooLong = True
startTime = time.time()

# Get config settings
configSettings = {}
with open("configuration/config.json", "r") as configData:
    # Load the JSON data
    configSettings = json.load(configData)
    print("Loaded config data")

time.sleep(2)

# Serial port configuration
def connect():
    try:
        print("Attempting to connect")
        ser = serial.Serial(configSettings.get('serialPort', '/dev/ttyAMA1'), 9600) #/dev/ttyAMA1 is the default, if config doesn't have it
        print("serial/out connected")
        connected = True

        thread = threading.Thread(target=write_to_port, args=(ser,))
        thread.daemon = True
        thread.start()

        ser.write("$$screen=3=Serial Connected\r\n".encode())

        return ser

    except serial.SerialException:
        publisher.send_string("serial failedToConnect")
        print("Failed to connect to serial port. Exiting...")
        sys.exit()

def write_to_port(ser):
    global killIfWaitingTooLong
    while True:
        data = subscriber.recv_string()
        killIfWaitingTooLong = False
        if(data != "serial alive"):
            parts = data.split(" ")
            parts.pop(0)
            data = " ".join(parts)
            # print(data)
            print(f"Sending {data} out the serial port")
            ser.write(data.encode())

ser = connect()
# Receive and process messages
while True:
    i=0
    while True:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8')
                # line = ser.readline()
                print("Received:", line)
                publisher.send_string("serial/out " + line)
            except:
                print("error parsing")
        time.sleep(0.02)

        if(killIfWaitingTooLong and time.time() - startTime > 5):
            print("waited too long without hearing from ZMQ")
            sys.exit()
