import serial
from time import sleep
import subprocess

ser = serial.Serial ("/dev/ttyAMA1", 9600)    #Open port with baud rate


while True:
    address = str(subprocess.check_output(['hostname', '-I'])).split(' ')[0].replace("b'", "")
    serialcmd = "$$screen=2=" + address + "\r\n"
    ser.write(serialcmd.encode())
    sleep(5)