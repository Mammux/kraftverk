import zmq
import time
import sys
import cmd
# from  multiprocessing import Process

port = 5556
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%s" % port)

class PowerPlantShell(cmd.Cmd):
    intro = "Welcome to the power plant interactive interface"
    prompt = "POWER: "

    print ("Connecting to server with port %s" % port)

    # Basic commands
    def do_get_hz(self, arg):
        'Get the frequency of the running power plant: get_hz'
        socket.send_string ("get_hz")
        message = socket.recv()
        print ("Response: ", message.decode('utf-8'))

    def do_set_hz_bump(self, arg):
        'Set the modifier of the frequency of the running power plant: set_hz -5'
        socket.send_string ("set_hz_bump %d" % int(arg))
        message = socket.recv()
        print ("Response: ", message.decode('utf-8'))

    def do_get_hz_bump(self, arg):
        'Get the modifier of the frequency of the running power plant: set_hz -5'
        socket.send_string ("get_hz_bump %d" % int(arg))
        message = socket.recv()
        print ("Response: ", message.decode('utf-8'))

    def do_get_vfd(self, arg):
        'Get the ac level of the running power plant: get_hz'
        socket.send_string ("get_vfd")
        message = socket.recv()
        print ("Response: ", message.decode('utf-8'))

    def do_set_vfd(self, arg):
        'Set the ac level of the running power plant: set_vfd 200'
        socket.send_string ("set_vfd %d" % int(arg))
        message = socket.recv()
        print ("Response: ", message.decode('utf-8'))

    def do_get_water(self, arg):
        'Get the water supply of the running power plant: get_water'
        socket.send_string ("get_water")
        message = socket.recv()
        print ("Response: ", message.decode('utf-8'))

    def do_set_water(self, arg):
        'Set the water supply of the running power plant: set_water 200'
        socket.send_string ("set_water %d" % float(arg))
        message = socket.recv()
        print ("Response: ", message.decode('utf-8'))

    def do_set_creaking(self, arg):
        'Set the level of creaking of the running power plant: creaking 0.5'
        socket.send_string ("set_creaking %f" % float(arg))
        message = socket.recv()
        print ("Response: ", message.decode('utf-8'))

    def do_set_damming(self, arg):
        'Set the level of damming of the running power plant: damming 0,5'
        socket.send_string ("set_damming %f" % float(arg))
        message = socket.recv()
        print ("Response: ", message.decode('utf-8'))

    def do_get_creaking(self, arg):
        'Get the level of creaking of the running power plant: get_creaking'
        socket.send_string ("get_creaking")
        message = socket.recv()
        print ("Response: ", message.decode('utf-8'))

    def do_get_damming(self, arg):
        'Get the level of damming of the running power plant: get_damming'
        socket.send_string ("get_damming")
        message = socket.recv()
        print ("Response: ", message.decode('utf-8'))

    def do_get_state(self, arg):
        'Get the state of the engine: get_state'
        socket.send_string ("get_state")
        message = socket.recv()
        print ("Response: ", message.decode('utf-8'))

    def do_exit(self, arg):
        'Leave the application'
        sys.exit()

    # Processing
    def precmd(self, line):
        return line.lower()

def main():

    PowerPlantShell().cmdloop()    

    # socket.send_string ("set_vfd 255")
    # message = socket.recv()
    # print ("Received reply ", "[", message, "]")

# Now we can connect a client 
# Process(target=client).start()

if __name__ == '__main__':
    main()
    
