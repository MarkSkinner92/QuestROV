import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
# accept all topics (prefixed) - default is none
socket.setsockopt_string(zmq.SUBSCRIBE, "")
socket.bind("tcp://*:5556")

while True:
    message = socket.recv_string()
    print(message)