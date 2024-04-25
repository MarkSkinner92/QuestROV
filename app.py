from flask import Flask, render_template
#from flask_socketio import SocketIO, emit

#import zmq
import time

#context = zmq.Context()
#socket = context.socket(zmq.PUB)
#socket.bind("tcp://localhost:5555")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
#socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

#@socketio.on('btn')
#def handle_message(msg):
#    print('button: ' + str(msg[0]) + '   ' + str(msg[1]))
#    #socket.send_string("data: hi")

#@socketio.on('key')
#def handle_message(msg):
#    print('key: ' + str(msg[0]) + '   ' + str(msg[1]))
#    #socket.send_string("data: hi")

#@socketio.on('axi')
#def handle_message(msg):
#    print('axis: ' + str(msg[0]) + '   ' + str(msg[1]))


if __name__ == '__main__':
#    socketio.run(app, allow_unsafe_werkzeug=True, host="0.0.0.0")
    app.run(debug=True,host="0.0.0.0")
