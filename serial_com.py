import serial
import zmq
import sys
import time

print("Starting ZMQ serial node")

# Serial port configuration
ser = serial.Serial('/dev/ttyS0', 9600)  # Change to 'COM3' and adjust the baud rate as per your setup

# ZeroMQ setup
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")  # Change the address and port as needed
socket.setsockopt_string(zmq.SUBSCRIBE, "data")  # Subscribe to zeroG data topic

try:
    while True:
        try:
            # Receive zeroG data with timeout
            data = socket.recv_string(flags=zmq.NOBLOCK)
            
            # Send data over serial
            ser.write(data.encode('utf-8'))
            ser.write(b'\n')  # Add a newline character if needed for proper termination
        
        except zmq.Again as e:
            pass  # No data received within the timeout period
        
        except KeyboardInterrupt:
            print("Program terminated by user.")
            break

finally:
    ser.close()
