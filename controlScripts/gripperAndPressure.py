import time
import zmq
import signal
import time
import json
import sys
import RPi.GPIO as GPIO
import json
import ms5837


configJson = {}
try:
    with open('configuration/config.json') as configFile:
        configJson = json.load(configFile)
        print("Config File Loaded")
except:
    print("couldn't open config file, or thrusters : directions [] doesn't exist")
    sys.exit(1)

signal.signal(signal.SIGINT, signal.SIG_DFL)

context = zmq.Context()

# Create a ZeroMQ subscriber
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://127.0.0.1:5555")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

publisher = context.socket(zmq.PUB)
publisher.connect("tcp://127.0.0.1:5556")


wristState = "stop"
clawState = "stop"

clawSettings = configJson["gripper"]["claw"]
wristSettings = configJson["gripper"]["wrist"]

defaults = {
        "useSaltwater" : 0,
		"useModel_30BA" : 1
    }
pressureSensorJSON = configJson.get("pressureSensor", defaults)
useSaltwater = pressureSensorJSON["useSaltwater"]
sensorModel = pressureSensorJSON["useModel_30BA"]

pressureSensor = ms5837.MS5837(sensorModel, 4)
sensorActive = False
try:
	pressureSensor.init()
	sensorActive = True
except:
	print("Pressure sensor error")

if(useSaltwater == 1):
	pressureSensor.setFluidDensity(ms5837.DENSITY_SALTWATER)
else:
	pressureSensor.setFluidDensity(ms5837.DENSITY_FRESHWATER)

while True:
	pressureSensor.read()
	# print(pressureSensor.depth(),pressureSensor.altitude())
	stringData = "Depth: "+str(round(pressureSensor.depth(), 2))+"m\nAltitude: " + str(round(pressureSensor.altitude(), 2))+"m"
	print(stringData)
	publisher.send_string("web/pressure " + stringData)
	time.sleep(2)
# data = pressureSensor.read(ms5837.OSR_256)
# print(data)
# def servoLoop():
#     while True:
#         print(clawState, wristState)
#         time.sleep(1)


# threading.Thread(target=servoLoop, daemon=True).start()

# while True:
#     stringData = subscriber.recv_string()

#     data = stringData.split(' ',1)
#     message = data[0]

#     # print(message,data[0])

#     if(message == "man/gripperClaw"):
#         if(data[1] == "1"):
#             clawState = "up"

#         if(data[1] == "-1"):
#             clawState = "down"

#         if(data[1] == "0"):
#             clawState = "stop"

#     elif(message == "man/gripperWrist"):
#         if(data[1] == "1"):
#             wristState = "right"

#         if(data[1] == "-1"):
#             wristState = "left"

#         if(data[1] == "0"):
#             wristState = "stop"
    

#     # print(wristState, clawState)
