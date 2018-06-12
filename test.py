#!/usr/bin/env python3
# Copyright (C) 2018 Quick2Space.org under the MIT License (MIT)
# See the LICENSE.txt file in the project root for more information.

import metalcore as mc
from MCP25625_hal import MCP25625_hal
from MCP25625_hal_mock import MCP25625_hal_mock
from MCP25625_registers import *
from MCP25625_api import MCP25625_api, Message

class MCP25625_test(object):

    def __init__(self, reg, hal_hw, hal_mock):
        self.reg = reg
        self.hal_hw = hal_hw
        self.hal_mock = hal_mock

    def MockHW_Test1(self):
        print("MockHW_Test1()")
        reg = self.reg
        hal = self.hal_mock
        reg.BindToHal(hal)
        hal.testData[reg.CANCTRL.address] = [0b10000111]
        print("{0:08b}".format(hal.testData[reg.CANCTRL.address][0]))
        with reg.CANCTRL as canctrl:
            print("canctrl.REQOP", canctrl.REQOP)
            canctrl.REQOP = reg.CANCTRL.REQOP_Configuration
            print("canctrl.REQOP", canctrl.REQOP)
        assert 0b10000111 == hal.testData[reg.CANCTRL.address][0]

        with reg.CANCTRL as canctrl:
            print("canctrl.REQOP", canctrl.REQOP)
            canctrl.REQOP = reg.CANCTRL.REQOP_Loopback
            print("canctrl.REQOP", canctrl.REQOP)
        print("{0:08b}".format(hal.testData[reg.CANCTRL.address][0]))
        assert 0b01000111 == hal.testData[reg.CANCTRL.address][0]

        hal.testData[reg.CNF1.address] = [0b00000000]
        with reg.CNF1 as cnf1:
            print("CNF1 = {0:08b}".format(cnf1.val))
            cnf1.SJW = 3

        with reg.CNF1 as cnf1:
            print("CNF1 = {0:08b}".format(cnf1.val))

        hal.testData[reg.CNF2.address] = [0b00000000]
        with reg.CNF2 as cnf2:
            print("CNF2 = {0:08b}".format(cnf2.val))
            cnf2.PHSEG1 = 3

        with reg.CNF2 as cnf2:
            print("CNF1 = {0:08b}".format(cnf2.val))

    def HwTestStat(self):
        print("HwTestStat()")
        reg = self.reg
        hal = self.hal_hw
        reg.BindToHal(hal)
        hal.Reset()

        with reg.CANCTRL as canctrl:
            print("canctrl = {0:08b}".format(canctrl.val))
            print("canctrl.REQOP", canctrl.REQOP)
            assert canctrl.REQOP == reg.CANCTRL.REQOP_Configuration
            canctrl.REQOP = 0b100
            print("canctrl.REQOP", canctrl.REQOP)
            assert canctrl.REQOP == reg.CANCTRL.REQOP_Configuration

        with reg.CANSTAT as canstat:
            print("canstat = {0:08b}".format(canstat.val))
            print("canstat.OPMOD", canstat.OPMOD)

        with reg.CANCTRL as canctrl:
            print("canctrl = {0:08b}".format(canctrl.val))
            print("canctrl.REQOP", canctrl.REQOP)
            assert canctrl.REQOP == reg.CANCTRL.REQOP_Configuration
            canctrl.REQOP = reg.CANCTRL.REQOP_Loopback
            print("canctrl.REQOP", canctrl.REQOP)
            assert canctrl.REQOP == reg.CANCTRL.REQOP_Loopback

        with reg.CANCTRL as canctrl:
            print("canctrl = {0:08b}".format(canctrl.val))
            print("canctrl.REQOP", canctrl.REQOP)
            assert canctrl.REQOP == reg.CANCTRL.REQOP_Loopback

        with reg.CANSTAT as canstat:
            print("canstat = {0:08b}".format(canstat.val))
            print("canstat.OPMOD", canstat.OPMOD)

        with reg.CNF1 as cnf1:
            print("CNF1 = {0:08b}".format(cnf1.val))

        with reg.CNF2 as cnf2:
            print("CNF2 = {0:08b}".format(cnf2.val))

        with reg.CNF3 as cnf3:
            print("CNF3 = {0:08b}".format(cnf3.val))
                
    def HwTestTx(self):
        print("HwTestTx()")
        reg = self.reg
        hal = self.hal_hw
        reg.BindToHal(hal)
        hal.Reset()

        with reg.TXRTSCTRL as txrtsctrl:
            print("txrtsctrl = {0:08b}".format(txrtsctrl.val))

        with reg.TXB0CTRL as txb0ctrl:
            print("txb0ctrl = {0:08b}".format(txb0ctrl.val))

        with reg.TXB1CTRL as txb1ctrl:
            print("txb0ctrl = {0:08b}".format(txb0ctrl.val))

        with reg.TXB2CTRL as txb2ctrl:
            print("txb0ctrl = {0:08b}".format(txb0ctrl.val))

        with reg.TXB0ID as txb0id:
            print("txb0id = {0:032b}".format(txb0id.val))

            txb0id.SID = 0b10101010111
            print("txb0id = 0b{0:032b}".format(txb0id.val))
            print("txb0id.SID = 0b{0:011b}".format(txb0id.SID))

            txb0id.EXIDE = 0b1
            print("txb0id = 0b{0:032b}".format(txb0id.val))
            print("txb0id.EXIDE = 0b{0:01b}".format(txb0id.EXIDE))

            txb0id.EID = 0b101010101111111100
            print("txb0id = 0b{0:032b}".format(txb0id.val))
            print("txb0id.EID = 0b{0:018b}".format(txb0id.EID))

        with reg.TXB1ID as txb1id:
            print("txb1id = {0:032b}".format(txb1id.val))

            txb1id.SID = 0b10101010111
            print("txb1id = 0b{0:032b}".format(txb1id.val))
            print("txb1id.SID = 0b{0:011b}".format(txb1id.SID))

            txb1id.EXIDE = 0b1
            print("txb1id = 0b{0:032b}".format(txb1id.val))
            print("txb1id.EXIDE = 0b{0:01b}".format(txb1id.EXIDE))

            txb1id.EID = 0b101010101111111101
            print("txb1id = 0b{0:032b}".format(txb1id.val))
            print("txb1id.EID = 0b{0:018b}".format(txb1id.EID))

        with reg.TXB2ID as txb2id:
            print("txb2id = {0:032b}".format(txb2id.val))

            txb2id.SID = 0b10101010111
            print("txb2id = 0b{0:032b}".format(txb2id.val))
            print("txb2id.SID = 0b{0:011b}".format(txb2id.SID))

            txb2id.EXIDE = 0b1
            print("txb2id = 0b{0:032b}".format(txb2id.val))
            print("txb2id.EXIDE = 0b{0:01b}".format(txb2id.EXIDE))

            txb2id.EID = 0b101010101111111110
            print("txb2id = 0b{0:032b}".format(txb2id.val))
            print("txb2id.EID = 0b{0:018b}".format(txb2id.EID))


        with reg.TXB0DLC as txb0dlc:
            txb0dlc.RTR = TXBnDLCx.RTR_RemoteTransmitRequest
            txb0dlc.DLC = 7

        with reg.TXB0DLC as txb0dlc:
            assert txb0dlc.RTR == TXBnDLCx.RTR_RemoteTransmitRequest
            assert txb0dlc.DLC == 7

        with reg.TXB0DLC as txb0dlc:
            txb0dlc.RTR = TXBnDLCx.RTR_DataFrame
            txb0dlc.DLC = 6

        with reg.TXB0DLC as txb0dlc:
            assert txb0dlc.RTR == TXBnDLCx.RTR_DataFrame
            assert txb0dlc.DLC == 6


        with reg.TXB1DLC as txb1dlc:
            txb1dlc.RTR = TXBnDLCx.RTR_RemoteTransmitRequest
            txb1dlc.DLC = 5

        with reg.TXB1DLC as txb1dlc:
            assert txb1dlc.RTR == TXBnDLCx.RTR_RemoteTransmitRequest
            assert txb1dlc.DLC == 5

        with reg.TXB1DLC as txb1dlc:
            txb1dlc.RTR = TXBnDLCx.RTR_DataFrame
            txb1dlc.DLC = 4

        with reg.TXB1DLC as txb1dlc:
            assert txb1dlc.RTR == TXBnDLCx.RTR_DataFrame
            assert txb1dlc.DLC == 4


        with reg.TXB2DLC as txb2dlc:
            txb2dlc.RTR = TXBnDLCx.RTR_RemoteTransmitRequest
            txb2dlc.DLC = 3

        with reg.TXB2DLC as txb2dlc:
            assert txb2dlc.RTR == TXBnDLCx.RTR_RemoteTransmitRequest
            assert txb2dlc.DLC == 3

        with reg.TXB2DLC as txb2dlc:
            txb2dlc.RTR = TXBnDLCx.RTR_DataFrame
            txb2dlc.DLC = 2

        with reg.TXB2DLC as txb2dlc:
            assert txb2dlc.RTR == TXBnDLCx.RTR_DataFrame
            assert txb2dlc.DLC == 2


        with reg.TXB0DATA as txb0data:
            txb0data.DATA = 0x1122334455667788

        with reg.TXB0DATA as txb0data:
            print("txb0data.DATA = ", txb0data.DATA)


        with reg.TXB1DATA as txb1data:
            txb1data.DATA = 0x1122334455667787

        with reg.TXB1DATA as txb1data:
            print("txb1data.DATA = ", txb1data.DATA)


        with reg.TXB2DATA as txb2data:
            txb2data.DATA = 0x1122334455667786

        with reg.TXB2DATA as txb2data:
            print("txb2data.DATA = ", txb2data.DATA)


    def HwTestRx(self):
        print("HwTestRx()")
        reg = self.reg
        hal = self.hal_hw
        reg.BindToHal(hal)
        hal.Reset()

        with reg.BFPCTRL as bfpctrl:
            print("bfpctrl.B1BFS = 0b{0:01b}".format(bfpctrl.B1BFS))
            print("bfpctrl.B0BFS = 0b{0:01b}".format(bfpctrl.B0BFS))
            print("bfpctrl.B1BFE = 0b{0:01b}".format(bfpctrl.B1BFE))
            print("bfpctrl.B0BFE = 0b{0:01b}".format(bfpctrl.B0BFE))
            print("bfpctrl.B1BFM = 0b{0:01b}".format(bfpctrl.B1BFM))
            print("bfpctrl.B0BFM = 0b{0:01b}".format(bfpctrl.B0BFM))

        with reg.RXB0CTRL as rxb0ctrl:
            print("rxb0ctrl.RXM = 0b{0:02b}".format(rxb0ctrl.RXM))
            print("rxb0ctrl.RXRTR = 0b{0:01b}".format(rxb0ctrl.RXRTR))
            print("rxb0ctrl.BUKT = 0b{0:01b}".format(rxb0ctrl.BUKT))
            print("rxb0ctrl.BUKT1 = 0b{0:01b}".format(rxb0ctrl.BUKT1))
            print("rxb0ctrl.FILHIT0 = 0b{0:01b}".format(rxb0ctrl.FILHIT0))

        with reg.RXB1CTRL as rxb1ctrl:
            print("rxb1ctrl.RXM = 0b{0:02b}".format(rxb1ctrl.RXM))
            print("rxb1ctrl.RXRTR = 0b{0:01b}".format(rxb1ctrl.RXRTR))
            print("rxb1ctrl.FILHIT = 0b{0:03b}".format(rxb1ctrl.FILHIT))

        with reg.RXB0ID as rxb0id:
            print("rxb0id.RXM = 0b{0:011b}".format(rxb0id.SID))
            print("rxb0id.SRR = 0b{0:1b}".format(rxb0id.SRR))
            print("rxb0id.IDE = 0b{0:1b}".format(rxb0id.IDE))
            print("rxb0id.EID = 0b{0:018b}".format(rxb0id.EID))

        with reg.RXB1ID as rxb1id:
            print("rxb1id.RXM = 0b{0:011b}".format(rxb1id.SID))
            print("rxb1id.SRR = 0b{0:1b}".format(rxb1id.SRR))
            print("rxb1id.IDE = 0b{0:1b}".format(rxb1id.IDE))
            print("rxb1id.EID = 0b{0:018b}".format(rxb1id.EID))

        with reg.RXB0DLC as rxb0dlc:
            print("rxb0dlc.RTR = 0b{0:1b}".format(rxb0dlc.RTR))
            print("rxb0dlc.RB1 = 0b{0:1b}".format(rxb0dlc.RB1))
            print("rxb0dlc.RB0 = 0b{0:1b}".format(rxb0dlc.RB0))
            print("rxb0dlc.DLC = 0b{0:04b}".format(rxb0dlc.DLC))

        with reg.RXB1DLC as rxb1dlc:
            print("rxb1dlc.RTR = 0b{0:1b}".format(rxb1dlc.RTR))
            print("rxb1dlc.RB1 = 0b{0:1b}".format(rxb1dlc.RB1))
            print("rxb1dlc.RB0 = 0b{0:1b}".format(rxb1dlc.RB0))
            print("rxb1dlc.DLC = 0b{0:04b}".format(rxb1dlc.DLC))

        with reg.RXB0DATA as rxb0data:
            print("rxb0data.DATA = 0x{0:016x}".format(rxb0data.DATA))

        with reg.RXB1DATA as rxb1data:
            print("rxb1data.DATA = 0x{0:016x}".format(rxb1data.DATA))

        with reg.RXF0ID as rxf0id:
            print("rxf0id.SID = 0b{0:011b}".format(rxf0id.SID))
            print("rxf0id.EXIDE = 0b{0:1b}".format(rxf0id.EXIDE))
            print("rxf0id.EID = 0b{0:018b}".format(rxf0id.EID))

        with reg.RXF1ID as rxf1id:
            print("rxf1id.SID = 0b{0:011b}".format(rxf1id.SID))
            print("rxf1id.EXIDE = 0b{0:1b}".format(rxf1id.EXIDE))
            print("rxf1id.EID = 0b{0:018b}".format(rxf1id.EID))

        with reg.RXF2ID as rxf2id:
            print("rxf2id.SID = 0b{0:011b}".format(rxf2id.SID))
            print("rxf2id.EXIDE = 0b{0:1b}".format(rxf2id.EXIDE))
            print("rxf2id.EID = 0b{0:018b}".format(rxf2id.EID))

        with reg.RXF3ID as rxf3id:
            print("rxf3id.SID = 0b{0:011b}".format(rxf3id.SID))
            print("rxf3id.EXIDE = 0b{0:1b}".format(rxf3id.EXIDE))
            print("rxf3id.EID = 0b{0:018b}".format(rxf3id.EID))

        with reg.RXF4ID as rxf4id:
            print("rxf4id.SID = 0b{0:011b}".format(rxf4id.SID))
            print("rxf4id.EXIDE = 0b{0:1b}".format(rxf4id.EXIDE))
            print("rxf4id.EID = 0b{0:018b}".format(rxf4id.EID))

        with reg.RXM0ID as rxm0id:
            print("rxm0id.SID = 0b{0:011b}".format(rxm0id.SID))
            print("rxm0id.EID = 0b{0:018b}".format(rxm0id.EID))

        with reg.RXM1ID as rxm1id:
            print("rxm1id.SID = 0b{0:011b}".format(rxm1id.SID))
            print("rxm1id.EID = 0b{0:018b}".format(rxm1id.EID))


    def Test_MCP25625_api(self):
        with MCP25625_api(reg) as api:
            api.Initialize()
            api.SetLoopbackMode()

            # Messages
            msg = Message();
            assert msg.arbitration_id == 0
            assert msg.extended_id == True
            assert msg.data == None
            print(msg)
            
            arb_id = 0b10101010101010101010101010101
            data = [0xDE, 0xAD, 0xCA, 0xFE]
            msg = Message(arb_id, data)
            assert len(msg.data) == len(data)
            assert msg.arbitration_id == arb_id
            print(msg)

            data = [0xDE, 0xAD, 0xCA, 0xFE, 0xDE, 0xAD, 0xCA, 0xFE, 0xFF]
            try:
                msg = Message(arb_id, data)
            except ValueError as e:
                print("PASS: Expected exception <{0}>".format(e))
            else:
                assert False

            arb_id = 0b101010101010101010101010101011
            try:
                msg = Message(arb_id, data)
            except ValueError as e:
                print("PASS: Expected exception <{0}>".format(e))
            else:
                assert False

            # Send/Receive


    def TestTx(self):
        with MCP25625_api(reg) as api:
            api.Initialize()
            api.SetLoopbackMode()

            # reset CANINTE - disable interrupts for all buffers
            self.reg.CANINTE.Zero()
            self.reg.CANINTE.Print()

            self.reg.CANINTF.Zero()
            self.reg.CANINTF.Print()

            print("- Setup receive in buffer 0 ...")
            with self.reg.RXB0CTRL as rxb0ctrl:
                rxb0ctrl.RXM = \
                self.reg.RXB0CTRL.RXM_TurnsMaskFiltersOffDevModeOnly

            self.reg.RXB0ID.Print()
            self.reg.RXB0DLC.Print()
            self.reg.RXB0DATA.Print()

            # transmit data

            # Standard ID
            toStandardId = 0b00001111000

            # Two bytes as data to be sent
            data = [0x12, 0x34]

            self.Transmit_Tx0_Std(toStandardId, data)

            self.reg.RXB0ID.Print()
            self.reg.RXB0DLC.Print()
            self.reg.RXB0DATA.Print()

    def Transmit_Tx0_Std(self, toStandardId, data):
        with self.reg.TXB0ID as txb0id:
            txb0id.SID = toStandardId
            txb0id.EXIDE = self.reg.TXB0ID.EXIDE_Disabled 

        print("- TXB0ID = ", self.reg.TXB0ID.toString())

        # replace with a runtime test
        maxBytes = 8
        assert len(data) <= maxBytes

        with self.reg.TXB0DLC as txb0dlc:
            txb0dlc.RTR = self.reg.TXB0DLC.RTR_DataFrame
            txb0dlc.DLC = len(data)

        print("- TXB0DLC = ", self.reg.TXB0DLC.toString())

        with self.reg.TXB0DATA as txb0data:
            serializedVal = 0
            for i in range(maxBytes):
                byteVal = 0
                if (i < len(data)):
                    byteVal = data[i]
                serializedVal = (serializedVal << 8) + byteVal
            txb0data.DATA = serializedVal

        print("- TXB0DATA = ", self.reg.TXB0DATA.toString())

        self.reg.CANINTE.Print()
        self.reg.CANINTF.Print()

        self.reg.TXB0CTRL.Print()
        self.reg.RXB0CTRL.Print()
        self.reg.RXB1CTRL.Print()

        with self.reg.TXB0CTRL as txb0ctrl:
            txb0ctrl.TXREQ = self.reg.TXB0CTRL.TXREQ_BufferPending
            txb0ctrl.TXP = self.reg.TXB0CTRL.TXP_HighestMessagePriority

        self.reg.TEC.Print()
        self.reg.REC.Print()
        self.reg.EFLG.Print()

        self.reg.TXB0CTRL.Print()

        self.reg.CANINTE.Print()
        self.reg.CANINTF.Print()

        self.reg.RXB0CTRL.Print()
        self.reg.RXB1CTRL.Print()

        print("- Reset CANINTF - remove transmission flags ...")
        with self.reg.CANINTF as canintf:
            canintf.TX0IF = 0

        self.reg.CANINTF.Print()


if __name__ == "__main__":
    hal_hw = MCP25625_hal()
    hal_mock = MCP25625_hal_mock()
    reg = MCP25625_RegisterGroup()

    test = MCP25625_test(reg, hal_hw, hal_mock)
    
    test.MockHW_Test1()
    test.HwTestStat()
    test.HwTestTx()
    test.HwTestRx()
    test.TestTx()
    test.Test_MCP25625_api()
    