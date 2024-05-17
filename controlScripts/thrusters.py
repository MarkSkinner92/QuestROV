import serial
import socketio, time
import zmq
import sys
import json
import signal
import numpy as np
    
signal.signal(signal.SIGINT, signal.SIG_DFL)

context = zmq.Context()

# Create a ZeroMQ subscriber
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://127.0.0.1:5555")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "man/")

# assume each thruster (1-6) is hooked up correctly. If not, replace that thruster with -1
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

while True:
    stringData = subscriber.recv_string()

    print(stringData)
    data = stringData.split(' ',1)
    message = data[0]
    value = float(data[1])

    if(message == 'man/forward'):
        inputVector[0,0] = deadZone(value, radius)

    if(message == 'man/rightTurn'):
        inputVector[1,0] = deadZone(value, radius)

    if(message == 'man/up'):
        inputVector[2,0] = deadZone(value, radius)

    print(computeThrustVector(inputVector))