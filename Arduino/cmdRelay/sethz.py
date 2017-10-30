#!/usr/bin/env python3
__description__ = \
"""
Test ability to send duplex data (e.g. read args while sending them out with
an unterminated command).
"""

import random, sys
import PyCmdMessenger
from time import sleep

def main(argv=None):
    
    if argv == None:
        argv = sys.argv[1:] 

    try:
        serial_device = "COM6"
    except IndexError:
        err = "Incorrect arguments. Usage:\n\n{}\n\n".format(__usage__)
        raise IndexError(err)

    commands = [["relay_on", "i"],
                ["relay_off", "i"],
                ["set_hz", "i"],
                ["error", ""]]

    a = PyCmdMessenger.ArduinoBoard(serial_device,baud_rate=57600)
    c = PyCmdMessenger.CmdMessenger(a, commands)

    while True:

        # channel = int(6*(random.random())+1)
        # onOff = int(2*(random.random()))
        hz = 45 + int(10*(random.random()))

        #if (onOff):
        #    print("relay_on {}".format(channel))
        #    c.send("relay_on",channel)
        #else:
        #    print("relay_off {}".format(channel))
        #    c.send("relay_off",channel)

        print("set_hz {}".format(hz))
        c.send("set_hz",hz)
            
        sleep(10)

if __name__ == "__main__":
    main()
