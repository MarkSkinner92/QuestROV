import time
import zmq
import signal
import json
import smbus
import time
import pca9554

bus = smbus.SMBus(1)

class Motor:
    def __init__(self, bus, address):
        self.bus = bus
        self.address = address
        self.lastWriteTime = 0
        self.lastWrittenSpeed = 0

        self.upperSpeedLimit = 32000
        self.lowerSpeedLimit = -32000

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
        print("Config File Loaded")
except:
    print("couldn't open config file, or thrusters : directions [] doesn't exist")

# This also turns on the fan
def thrustersOn():
    i2c_address = 0x38
    pca_driver = pca9554.Pca9554(i2c_address)
    # enable all as be outputs and set low
    for i in range(0, 8):
        pca_driver.write_config_port(i, pca9554.OUTPUT)
        pca_driver.write_port(i,1)

# put our raw axis inputs through this function to ensure the output is actually 0 when the joystick is released.
def deadZone(value, distance):
    if(-distance < value < distance):
        return(0)
    return(value)

print("Turning thrusters on...")
thrustersOn()
time.sleep(1)
print("Thrusters On")

addresses = configJson['thrusters']['addresses']
mixerMatrix = configJson['thrusters']['mixer']
gain = configJson['thrusters']['gain']
constraints = configJson['thrusters']['constraints']
deadZoneDistance = configJson['deadZone']

# Set up motors from addresses
motors = {}
for motorName in addresses:
    motors[motorName] = Motor(bus, int(addresses[motorName], 16))

def mixInputs(inputs):
    output = {}

    # Compute the mixing of all directions
    for direction in inputs:
        inputValue = inputs[direction]
        contributions = mixerMatrix[direction]
        for thruster in contributions:
            weightedContribution = contributions[thruster] * inputValue
            if(output.get(thruster,False)):
                output[thruster] += weightedContribution
            else:
                output[thruster] = weightedContribution

    
    # Clip the raw outputs to keep them in range, and apply gain
    # for thruster in output:
    for thruster in output:
        output[thruster] *= gain[thruster]
        
        output[thruster] = max(constraints["min"][thruster], min(output[thruster], constraints["max"][thruster]))

    return output






# # multiply our input vector by the transformation matrix, and keep each output in the bounds of [-1,1]
# def computeThrustVector(inputVector):
#     return []

# thrustVector = np.array([0,0,0,0,0,0])
inputs = {}
cleanOutputs = {}

while True:
    stringData = subscriber.recv_string()

    data = stringData.split(' ',1)
    message = data[0]

    print(message,data[0])


    if(message != "man/keepalive"):
        parts = message.split('_')

        value = float(data[1])
        value = deadZone(value, deadZoneDistance)

        print(parts)
        if(len(parts) > 0):
            if(parts[0] == "man/test"):
                thruster = parts[1]
                motors[thruster].setSpeed(value * (1 if gain[thruster] > 0 else -1))

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

        cleanOutputs = mixInputs(inputs)

    else: # If message is a man/keepalive
        print("keep alive")
    
    for thruster in cleanOutputs:
        motors[thruster].setSpeed(cleanOutputs[thruster])