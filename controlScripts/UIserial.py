import serial
from time import sleep
import subprocess

#get the current IP address
ser = serial.Serial ("/dev/ttyAMA1", 9600)    #Open port with baud rate

#send it to the UI board to show on the screen. Update every 5 seconds
# while True:
address = str(subprocess.check_output(['hostname', '-I'])).split(' ')[0].replace("b'", "")
serialcmd = "$$screen=3=" + address + "\r\n"
# serialcmd = "$$screen=3=" + "test" + "\r\n"
print("serialcmd")
ser.write(serialcmd.encode())
    # sleep(5)


# import zmq

# context = zmq.Context()

# # Create a ZeroMQ publisher
# publisher = context.socket(zmq.PUB)
# publisher.bind("tcp://*:5555")