from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit

import zmq
import time
import json
import threading
import configManager
import requests

# Before anything, we need to check the contents of configuration and make sure a config file exists. If it doesn't, copy the default
configManager.initConfigJSON()

context = zmq.Context()

# Create a ZeroMQ publisher
publisher = context.socket(zmq.PUB)
publisher.bind("tcp://*:5555")

# Create a ZeroMQ subscriber
subscriber = context.socket(zmq.SUB)
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
subscriber.bind("tcp://*:5556")

# def publishJSON(topic,data):
#     global publisher
#     publisher.send_string(topic + " " + json.dumps(data))

def publishMessage(topic,message):
    global publisher
    publisher.send_string(topic + " " + message)

app = Flask(__name__, static_url_path="/static", static_folder="static")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/console')
def index():
    return render_template('index.html')

@app.route('/')
def config():
    return render_template('config.html')

@app.route("/register_service")
def register_service():
   return app.send_static_file("register_service.json")

@app.route("/config_data",methods=['GET'])
def get_config():
   return send_from_directory("configuration/", "config.json")

@app.route("/default_config_data",methods=['GET'])
def get_default_config():
   return send_from_directory("defaultConfiguration/", "defaultConfig.json")

@app.route('/config_data',methods=['POST'])            
def save_config():                                           
    if request.is_json:
        data = request.json
        with open("configuration/config.json", 'w') as file:
            json.dump(data, file, indent=4)
    return 'success'

# @app.route("/info",methods=['GET'])
# def getInfo():
#    return {"battery":"12.5v"}

@socketio.on('man')
def handle_message(name, value):
    publishMessage("man/"+name,str(value))
    print(name, value)

def backgroundThread():
    global socketio
    while True:

        data = subscriber.recv_string()
        parts = data.split(" ", 1)
        message = parts[1]
        path = parts[0]

        splitPath = path.split('/', 1)
        protocol = splitPath[0]
        subPath = splitPath[1] if len(splitPath) > 1 else ""

        if(protocol == 'web'):
            print("sending webdata: topic = " + subPath + "; message = " + message)
            socketio.emit(subPath, message)

        if(protocol == 'serial'):
            print("recieved serial data: " + message)
            if(message[0] == "$"):
                parts = message.split("=")
                if(parts[0] == "$$SCREEN" and parts[1] == "3"):
                    print("screen changed to",parts[1])

                    displayString = "ip: waiting"
                    serialcmd = "$$screen=3=" + displayString.ljust(20) + "\r\n"
                    publishMessage("serial",serialcmd)

                    # address = str(subprocess.check_output(['hostname', '-I'])).split(' ')[0].replace("b'", "")
                    try:
                        response = requests.get("http://host.docker.internal:9090/v1.0/ethernet")
                        jdata = response.json()
                        if(len(jdata) > 0):
                            address = jdata[0]['addresses'][0]['ip']
                            print(address)
                        else:
                            address = "no-devices"
                    except:
                        address = "None Found"
                    
                    displayString = "ip: " + address

                    serialcmd = "$$screen=3=" + displayString.ljust(20) + "\r\n"
                    publishMessage("serial",serialcmd)
                
                # TELEM parsing
                # parts = voltage current volt mincell volt maxcell temp charging
                elif(parts[0] == "$$TELEM"):
                    telemString = ""
                    telemString += "Voltage: " + parts[1] + '\n'
                    telemString += "Current: " + parts[2] + '\n'
                    telemString += "Mincell: " + parts[3] + '\n'
                    telemString += "Maxcell: " + parts[4] + '\n'
                    telemString += "Temperature: " + parts[5] + '\n'
                    telemString += "charging: " + parts[6].strip()

                    print(telemString)
                    socketio.emit("telem", telemString)
            # recieve screen 3
            # send IP

if __name__ == '__main__':
    # threading.Thread(target=sendIPToScreen, daemon=True).start()
    threading.Thread(target=backgroundThread, daemon=True).start()
    socketio.run(app, allow_unsafe_werkzeug=True, host="0.0.0.0", port=5000)