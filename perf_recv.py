#!/usr/bin/env python3
# Copyright (C) 2018 Quick2Space.org under the MIT License (MIT)
# See the LICENSE.txt file in the project root for more information.

from time import sleep
from MCP25625_api import MCP25625_api, Message

class perf_recv(object):

    def __init__(self):
        # Setup CAN API
        self.can = MCP25625_api() #verbosePrint = True) # - Set this to get more debugging information.

        self.can.SetFilterIdF0(0x122801F0)
        self.can.Initialize()
        
        self.can.SetNormalMode() # Uncomment for normal mode.
        #self.can.SetLoopbackMode() # Uncomment for loopback (debug) mode.

        self.lastData = 0
            
    def Start(self):
        i = 0

        while(True):
            self.Read()

    def Read(self):
        try:
            recvMsg = self.can.Recv(timeoutMilliseconds=10000)
            if (recvMsg.data[0] != self.lastData + 1):
                print("!!! RECV: {0}".format(recvMsg))
            else:
                print("    RECV: {0}".format(recvMsg))
            self.lastData = recvMsg.data[0]
            
        except TimeoutError as e:
            print("    RECV: Timeout receiving message. <{0}>".format(e))

    def Send(self, i):
        arbitration_id = 0b10000010010010010011111111111 # Extended Mode, 29bit
        data = [i, 0xDE, 0xAD, 0xCA, 0xFE]
        msg = Message(arbitration_id, data) #, extended_id=False)

        try:
            self.can.Send(msg, timeoutMilliseconds=1000)
            print("    SEND: {0}".format(msg))
        except TimeoutError as e:
            print("    SEND: Timeout sending message. <{0}>".format(e))

if __name__ == "__main__":
    sample = perf_recv()
    sample.Start()
