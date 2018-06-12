#!/usr/bin/env python3
# Copyright (C) 2018 Quick2Space.org under the MIT License (MIT)
# See the LICENSE.txt file in the project root for more information.

import time

import argparse
import metalcore as mc
from MCP25625_hal import MCP25625_hal
from MCP25625_hal_mock import MCP25625_hal_mock
from MCP25625_registers import *
from MCP25625_api import MCP25625_api

class MCP25625_cli(object):

    def __init__(self, reg, hal_hw, loopbackMode, verbosePrint):
        self.reg = reg
        self.hal_hw = hal_hw
        self.loopbackMode = loopbackMode
        self.verbosePrint = verbosePrint

    def __enter__(self):
        self.api = MCP25625_api(reg, self.verbosePrint).__enter__()
        self.api.Initialize()

        # reset CANINTE - disable interrupts for all buffers
        self.reg.CANINTE.Zero()

        self.reg.CANINTF.Zero()

        if self.verbosePrint:
            self.reg.CANINTE.Print()
            self.reg.CANINTF.Print()

        return self

    def EnterLoopbackOrNormalMode(self):
        if self.loopbackMode:
            self.api.SetLoopbackMode()
        else:
            self.api.SetNormalMode()


    def __exit__(self, type, value, traceback):
        self.api.__exit__(type, value, traceback)


    def TestTx(self, toStandardId, data):

        self.Transmit_Tx0_Std(toStandardId, data)


    def TestRx(self, waitTimeSeconds):

        print("- Setup receive in buffer 0 ...")

        self.reg.RXB0CTRL.Zero()
        self.reg.RXB1CTRL.Zero()
        self.reg.RXM0ID.Zero()
        self.reg.RXM1ID.Zero()
        self.reg.RXF0ID.Zero()
        self.reg.RXF1ID.Zero()
        self.reg.RXF2ID.Zero()
        self.reg.RXF3ID.Zero()
        self.reg.RXF4ID.Zero()
        self.reg.RXF5ID.Zero()

        self.reg.CANINTF.Zero()

        all1 = 0b11111111111
        all0 = 0b00000000000

        # Enable RX buffer 0 for all messages

        # Control register
        with self.reg.RXB0CTRL as rxb0ctrl:
            rxb0ctrl.RXM = self.reg.RXB0CTRL.RXM_StandardFramesOnly

        # Mask register
        with self.reg.RXM0ID as rxm0id:
            # Setting a all-zero mask will accept anything
            rxm0id.SID = all0

        # Acceptance Filter registers

        with self.reg.RXF0ID as rxf0id:
            rxf0id.EXIDE = self.reg.RXF0ID.EXIDE_StandardFramesFilter
            rxf0id.SID = all0

        with self.reg.RXF1ID as rxf1id:
            rxf1id.EXIDE = self.reg.RXF0ID.EXIDE_StandardFramesFilter
            rxf1id.SID = all0


        # Enable RX buffer 1 only for "all-one" ID messages

        # Control register
        with self.reg.RXB1CTRL as rxb1ctrl:
            rxb1ctrl.RXM = self.reg.RXB0CTRL.RXM_StandardFramesOnly

        print("- Setting mask register RXM1ID = 0b11111111111 ...")

        # Mask register
        with self.reg.RXM1ID as rxm1id:
            # Setting a all-one mask will accept only filtered msgs
            rxm1id.SID = all1
            rxm1id.EID = 0b101010101010101010

        self.reg.RXM1ID.Print()

        # Acceptance Filter registers

        print("- Setting mask register RXF2ID = 0b11111111111 ...")

        with self.reg.RXF2ID as rxf2id:
            rxf2id.EXIDE = self.reg.RXF0ID.EXIDE_StandardFramesFilter
            rxf2id.SID = all1
            rxf2id.EID = 0b101010101010101010

        self.reg.RXF2ID.Print()

        with self.reg.RXF3ID as rxf3id:
            rxf3id.EXIDE = self.reg.RXF0ID.EXIDE_StandardFramesFilter
            rxf3id.SID = all1

        with self.reg.RXF4ID as rxf4id:
            rxf4id.EXIDE = self.reg.RXF0ID.EXIDE_StandardFramesFilter
            rxf4id.SID = all1

        with self.reg.RXF5ID as rxf5id:
            rxf5id.EXIDE = self.reg.RXF0ID.EXIDE_StandardFramesFilter
            rxf5id.SID = all1

        # input("Entering loopback/normal. Press Enter to continue...")

        self.EnterLoopbackOrNormalMode()

        input("Entered loopback/normal. Press Enter to continue...")

        while(True):
            self.reg.CANINTF.Print()

            if self.verbosePrint:
                self.reg.RXB0ID.Print()
                self.reg.RXB0DLC.Print()
                self.reg.RXB0DATA.Print()

            with self.reg.RXB0ID as rxb0id:
                print("ID=", bin(rxb0id.SID))

            with self.reg.RXB0DLC as rxb0dlc:
                dataLen = rxb0dlc.DLC
                print("Data found of length ", dataLen)
                self.reg.CANINTF.Print()

                with self.reg.RXB0DATA as rxb0data:
                    data = list(rxb0data.DATA_bytes)[:dataLen]
                    print("data = ", [hex(x) for x in data])

            input("end of loop. Press Enter to continue...")

                # if (dataLen > 0):
                #    break

            if self.verbosePrint:
                self.reg.TEC.Print()
                self.reg.REC.Print()
                self.reg.EFLG.Print()

            if (waitTimeSeconds <= 0):
                print("##### No data found. Timeout expired. Exiting ... ")
                break

            waitTimeSeconds -= 1
            time.sleep(1)

    def Transmit_Tx0_Std(self, toStandardId, data):

        self.EnterLoopbackOrNormalMode()

        self.reg.CANINTF.Zero()

        if self.verbosePrint:
            self.reg.TXB0CTRL.Print()

        print("- Reset CANINTF - remove transmission flags ...")
        with self.reg.CANINTF as canintf:
            canintf.TX0IF = 0

        with self.reg.TXB0CTRL as txb0ctrl:
            if txb0ctrl.TXREQ != self.reg.TXB0CTRL.TXREQ_NotPending:
                raise "Error - txb0ctrl.TXREQ not clear!"

        # Set ID
        with self.reg.TXB0ID as txb0id:
            txb0id.SID = toStandardId
            txb0id.EXIDE = self.reg.TXB0ID.EXIDE_Disabled 

        # Set Data Len
        maxBytes = 8
        assert len(data) <= maxBytes
        with self.reg.TXB0DLC as txb0dlc:
            txb0dlc.RTR = self.reg.TXB0DLC.RTR_DataFrame
            txb0dlc.DLC = len(data)

        # Set Data
        with self.reg.TXB0DATA as txb0data:
            serializedVal = 0
            for i in range(maxBytes):
                byteVal = 0
                if (i < len(data)):
                    byteVal = data[i]
                serializedVal = (serializedVal << 8) + byteVal
            txb0data.DATA = serializedVal

        if self.verbosePrint:
            self.reg.TXB0ID.Print()
            self.reg.TXB0DLC.Print()
            self.reg.TXB0DATA.Print()

            self.reg.CANINTF.Print()
            self.reg.TXB0CTRL.Print()

        # Set TX priority
        with self.reg.TXB0CTRL as txb0ctrl:
            txb0ctrl.TXP = self.reg.TXB0CTRL.TXP_HighestMessagePriority

        # initiate Tx in buffer 0
        with self.reg.TXB0CTRL as txb0ctrl:
            txb0ctrl.TXREQ = self.reg.TXB0CTRL.TXREQ_BufferPending

        if self.verbosePrint:
            self.reg.TXB0CTRL.Print()
            self.reg.CANINTF.Print()

        self.reg.TEC.Print()
        self.reg.REC.Print()
        self.reg.EFLG.Print()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tx', action='store_true', 
        help='transmission test')
    parser.add_argument('-r', '--rx', action='store_true', 
        help='receive test')
    parser.add_argument('-l', '--loopback', action='store_true', 
        help='loopback mode')
    parser.add_argument('-z', '--reset', action='store_true', 
        help='Reset state')
    parser.add_argument('-v', '--verbose', action='store_true', 
        help='Verbose output')
    args = parser.parse_args()

    hal_hw = MCP25625_hal()
    reg = MCP25625_RegisterGroup()

    print("--- start test ---")


    if args.reset:

        # TODO - add better reset logic
        # (eventually pull down the RST pin?)
        # Transmit an empty buffer to reset Rx state
        with MCP25625_cli(reg, hal_hw, True, args.verbose) as test:

            test.TestTx(0b00000000000, [])
            test.TestRx(0)    

    with MCP25625_cli(reg, hal_hw, args.loopback, args.verbose) as test:

        if args.tx:
            stdId = 0b10100101101
            data = [0x13, 0x24, 0x37, 0x99]
            print("tx(id={0:b},{1}) ...".format(stdId, data))
            test.TestTx(stdId, data)

        if args.rx:
            test.TestRx(0)
