#!/usr/bin/env python3
# Copyright (C) 2018 Quick2Space.org under the MIT License (MIT)
# See the LICENSE.txt file in the project root for more information.

from time import sleep
from MCP25625_api import MCP25625_api, Message

class can_sample(object):

    def __init__(self):
        # Setup CAN API
        self.can = MCP25625_api() #verbosePrint = True) # - Set this to get more debugging information.
        self.can.Initialize()
        
        #self.can.SetNormalMode() # Uncomment for normal mode.
        self.can.SetLoopbackMode() # Uncomment for loopback (debug) mode.
            
    def Start(self):

        # Reader writer with reader priority (reader can starve the writer):
        while(True):
            while (self.can.Peek() == True):
                self.Read()

            # In loopback mode this works because one message gets buffered in RXB0 and another in MAB.
            # If more than 2 messages are sent here, the receive loop above will only see the first (in RXB0)
            # and the last message that was held in MAB.
            for i in range(0, 2):
                self.Send(i)

            sleep(1)

    def Read(self):
        try:
            recvMsg = self.can.Recv()
            print("RECV: {0}".format(recvMsg))
        except TimeoutError as e:
            print("RECV: Timeout receiving message. <{0}>".format(e))

    def Send(self, i):
        arbitration_id = 0b10010010010010010011111111111 # Extended Mode, 29bit
        data = [i, 0xDE, 0xAD, 0xCA, 0xFE]
        msg = Message(arbitration_id, data) #, extended_id=False)

        try:
            self.can.Send(msg, timeoutMilliseconds=1000)
            print("SEND: {0}".format(msg))
        except TimeoutError as e:
            print("SEND: Timeout sending message. <{0}>".format(e))

if __name__ == "__main__":
    sample = can_sample()
    sample.Start()
