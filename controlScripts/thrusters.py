import time
import zmq
import signal
import numpy as np

import smbus
import time

bus = smbus.SMBus(1)

class Motor:
    def __init__(self, bus, address):
        self.bus = bus
        self.address = address
        self.lastWriteTime = 0
        self.lastWrittenSpeed = 0

        self.upperSpeedLimit = 20
        self.lowerSpeedLimit = -20

        self.setSpeed(0)

    def writeBus(self,speed):
        
        try:
            requestedSpeed = max(self.lowerSpeedLimit, min(speed, self.upperSpeedLimit))
            bus.write_word_data(self.address, 0, round(requestedSpeed))
            self.lastWrittenSpeed = requestedSpeed
        except OSError as e:
            print(f"Error occurred: {e}")

    def setSpeed(self, speed):
        if(time.time() - self.lastWriteTime > 5):
            self.writeBus(0)

        # TODO: Do something to ramp if the requested speed is much different than self.lastWrittenSpeed

        self.writeBus(speed)
        self.lastWriteTime = time.time()

# Register Motors
motors = [Motor(bus, 0x2a),Motor(bus, 0x2b),Motor(bus, 0x2c),Motor(bus, 0x2d),Motor(bus, 0x2e),Motor(bus, 0x2f)]
    
signal.signal(signal.SIGINT, signal.SIG_DFL)

context = zmq.Context()

# Create a ZeroMQ subscriber
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://127.0.0.1:5555")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "man/")

# To change the direction of a particular thruster, change this number
thrusterDirection = np.array([1,1,1,1,1,1])

# 6x3 transformation matrix
# columns represent: forward, right-turn, up
# rows 1-6 represent thrusters 1-6 in frame.png
thrusterMatrix = np.matrix([
    [1, -1,0],
    [1, 1, 0],
    [-1,-1,0],
    [-1,1, 0],
    [0, 0, 1],
    [0, 0, 1]
])

# put our raw axis inputs through this function to ensure the output is actually 0 when the joystick is released.
radius = 0.06
def deadZone(value, radius):
    if(-radius < value < radius):
        return(0)
    return(value)

# multiply our input vector by the transformation matrix, and keep each output in the bounds of [-1,1]
def computeThrustVector(inputVector):
    matrix = np.matmul(thrusterMatrix, inputVector).clip(-1,1)
    thrusterSpeeds = np.squeeze(np.asarray(matrix)) * thrusterDirection
    return thrusterSpeeds

inputVector = np.matrix([[0.0],[0.0],[0.0]])
thrustVector = np.array([0,0,0,0,0,0])

while True:
    stringData = subscriber.recv_string()

    data = stringData.split(' ',1)
    message = data[0]


    if(message != "man/keepalive"):
        value = float(data[1])

        if(message == 'man/forward'):
            inputVector[0,0] = deadZone(value, radius)

        elif(message == 'man/rightTurn'):
            inputVector[1,0] = deadZone(value, radius)

        elif(message == 'man/up'):
            inputVector[2,0] = deadZone(value, radius)

        else:
            print(stringData)
        
        thrustVector = computeThrustVector(inputVector)

    else: # If message is a man/keepalive
        print("keep alive")
    

    for i, value in enumerate(thrustVector):
        motors[i].setSpeed(value*20)
        print(i,value)

    # print(computeThrustVector(inputVector))