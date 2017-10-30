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
        serial_device = argv[0]
    except IndexError:
        err = "Incorrect arguments. Usage:\n\n{}\n\n".format(__usage__)
        raise IndexError(err)

    commands = [["set_voltage", "i"],
                ["error", ""]]

    a = PyCmdMessenger.ArduinoBoard(serial_device,baud_rate=57600)
    c = PyCmdMessenger.CmdMessenger(a, commands)

    while True:

        value = int(255*(random.random()))
        print("set_voltage {}".format(value))
        c.send("set_voltage",value)
        sleep(10)

if __name__ == "__main__":
    main()
