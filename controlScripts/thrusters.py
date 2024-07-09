import time
import zmq
import signal
import json
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

signal.signal(signal.SIGINT, signal.SIG_DFL)

context = zmq.Context()

# Create a ZeroMQ subscriber
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://127.0.0.1:5555")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "man/")

# The config file will overwrite the directions of the thrusters defined above
try:
    with open('configuration/config.json') as configFile:
        configJson = json.load(configFile)
        print("Thruster direction pulled from Config File")
except:
    print("couldn't open config file, or thrusters : directions [] doesn't exist")

# put our raw axis inputs through this function to ensure the output is actually 0 when the joystick is released.
radius = 0.06
def deadZone(value, radius):
    if(-radius < value < radius):
        return(0)
    return(value)


# Set up motors from addresses
addresses = configJson['thrusters']['addresses']
motors = {}
for motorName in addresses:
    motors[motorName] = Motor(bus, int(addresses[motorName], 16))


mixerMatrix = configJson['thrusters']['mixer']
for direciton in mixerMatrix:
    print(direciton)


def mixInputs(inputs):
    output = {}
    for direction in inputs:
        inputValue = inputs[direction]
        contributions = mixerMatrix[direction]
        for thruster in contributions:
            weightedContribution = contributions[thruster] * inputValue
            print("wc",thruster,weightedContribution)
            if(output.get(thruster,False)):
                output[thruster] += weightedContribution
            else:
                output[thruster] = weightedContribution

        # print("direction",direction, "raw value",inputs[direction],mixerMatrix[direction])
    return output






# # multiply our input vector by the transformation matrix, and keep each output in the bounds of [-1,1]
# def computeThrustVector(inputVector):
#     return []

# thrustVector = np.array([0,0,0,0,0,0])
inputs = {}

while True:
    stringData = subscriber.recv_string()

    data = stringData.split(' ',1)
    message = data[0]

    print(message,data[0])


    if(message != "man/keepalive"):
        value = float(data[1])

        if(message == 'man/forward'):
            if(value >= 0):
                inputs["forward"] = value
            if(value <= 0):
                inputs["backwards"] = abs(value)

        if(message == 'man/right'):
            if(value >= 0):
                inputs["right"] = value
            if(value <= 0):
                inputs["left"] = abs(value)

        if(message == 'man/up'):
            if(value >= 0):
                inputs["up"] = value
            if(value <= 0):
                inputs["down"] = abs(value)

        if(message == 'man/yawRight'):
            if(value >= 0):
                inputs["yawRight"] = value
            if(value <= 0):
                inputs["yawLeft"] = abs(value)

        if(message == 'man/rollRight'):
            if(value >= 0):
                inputs["rollRight"] = value
            if(value <= 0):
                inputs["rollLeft"] = abs(value)

        print(mixInputs(inputs))

        # if(message == 'man/forward'):
        #     if(value >= 0):
        #         inputs["forward"] = value
        #     if(value <= 0):
        #         inputs["backwards"] = value

        # else:
            # print(stringData)
        
#         # thrustVector = computeThrustVector(inputVector)

#     else: # If message is a man/keepalive
#         print("keep alive")
    

#     for i, value in enumerate(thrustVector):
#         motors[i].setSpeed(value*20)
#         print(i,value)

    # print(computeThrustVector(inputVector))