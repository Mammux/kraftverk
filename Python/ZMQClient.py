import zmq
import time
import sys
from  multiprocessing import Process

def client():
    port = 5556
    context = zmq.Context()
    print ("Connecting to server with port %s" % port)
    socket = context.socket(zmq.REQ)
    socket.connect ("tcp://localhost:%s" % port)

#    socket.send_string ("set_water 255")
#    message = socket.recv()
#    print ("Received reply ", "[", message, "]")

    socket.send_string ("set_vfd 255")
    message = socket.recv()
    print ("Received reply ", "[", message, "]")
    
# Now we can connect a client 
Process(target=client).start()
    
