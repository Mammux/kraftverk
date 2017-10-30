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
                ["vfd_level", "i"],
                ["error", ""]]

    a = PyCmdMessenger.ArduinoBoard(serial_device,baud_rate=57600)
    c = PyCmdMessenger.CmdMessenger(a, commands)

    while True:

        level = int(255*(random.random()))

        print("vfd_level {}".format(level))
        c.send("vfd_level",level)
            
        sleep(10)

if __name__ == "__main__":
    main()
