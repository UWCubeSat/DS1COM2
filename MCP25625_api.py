# Copyright (C) 2018 Quick2Space.org under the MIT License (MIT)
# See the LICENSE.txt file in the project root for more information.

# High-level CAN operations 

import metalcore as mc
import threading
from time import sleep
from datetime import datetime
from MCP25625_hal import MCP25625_hal
from MCP25625_registers import *

class MCP25625_api(object):
    # TODO: Optimize for CAN bus frequency:
    _txPollingIntervalSeconds = 0.1
    _rxPollingIntervalSeconds = 0.1
    _txLock = threading.Lock()
    _rxLock = threading.Lock()

    def __init__(self, reg = MCP25625_RegisterGroup(), verbosePrint = False):
        """
        Creates a CAN API instance.
        At most one instance can exist. The driver is configured to use CS0 on Raspberry PI.

        Args: 
            verbosePrint: Enable console verbose logging.
        """

        self.reg = reg
        self.verbosePrint = verbosePrint
        self.filter0Enabled = False
        self.savedFilterId0 = 0

        self.filter1Enabled = False
        self.savedFilterId1 = 0

    # Reset the HW before beginning to interact with it
    def __enter__(self):
        self.Initialize(hal = None)
        return self

    def __exit__(self, type, value, traceback):
        if self.hal:
            self.hal.close()
            self.hal = None
        return 

    def Initialize(self, hal = None):
        """
        Initializes the CAN controller.
        """

        if (self.verbosePrint):
            print (">> Initialize({0})", hal)

        if hal == None:
            self.hal = MCP25625_hal()
            self.reg.BindToHal(self.hal)
        else:
            self.hal = hal

        self.hal.Reset()

        with self.reg.CANCTRL as canctrl:
            assert canctrl.REQOP == self.reg.CANCTRL.REQOP_Configuration
            canctrl.REQOP = 0b100

            # Set prescaler to 00 
            canctrl.CLKPRE = 0b00
            assert canctrl.REQOP == self.reg.CANCTRL.REQOP_Configuration

        if self.verbosePrint:
            self.reg.CANCTRL.Print()
            self.reg.CANSTAT.Print()

        # init values used for the HuskySat-1 satellite CAN bus
        # TODO - move initialization somewhere else? 

        with self.reg.CNF1 as cnf1:

            # 0x87 = 0b.1000.0111

            # synchronization jump width = 2 x T_Q
            cnf1.SJW = self.reg.CNF1.SJW_Length3TQ

            # Baud Rate Prescaler
            # Use 16 clock cycles 
            # T_Q = 2x(1+BRP)/F_OSC = 2x(1+7)/F_OSC = 16 / F_OSC
            cnf1.BRP = 0b000111

        with self.reg.CNF2 as cnf2:

            # 0x0bf = 0b.1011.1111

            # Use BTL
            cnf2.BTLMODE = self.reg.CNF2.BTLMODE_CNF3_PHSEG2

            # Sample point
            # TODO - should we increase this to three sample points? 
            cnf2.SAM = self.reg.CNF2.SAM_OnePointSample

            # PRSEG length = (7+PRSEG)xT_Q = (7+1)xT_Q = 8xT_Q 
            cnf2.PRSEG = 0b111

            # PHSEG1 length = (7+PHSEG1)xT_Q = (7+1)xT_Q = 8xT_Q 
            cnf2.PHSEG1 = 0b111

        with self.reg.CNF3 as cnf3:

            # 0x02 = 0b.0000.0010

            # No wake-up filter
            cnf3.WAK = 0

            # Ignored anyway since CANCTRL.CLKEN = 0
            cnf3.SOF = 0

            # PHSEG2 length = (7+PHSEG2)xT_Q = (7+1)xT_Q = 8xT_Q 
            cnf3.PHSEG2 = 0b010

        self.reg.TXRTSCTRL.Zero()

        if self.verbosePrint:
            self.reg.CNF1.Print()
            self.reg.CNF2.Print()
            self.reg.CNF3.Print()
            self.reg.TXRTSCTRL.Print()
        
        # Configure receive
        self._ConfigureReceive()

    # Split a combined 29-bit ID into a pair of SID (11 bit) and EID (18 bit)
    def SplitExtendedId(self, combinedId):
        return (combinedId >> 18), (combinedId & 0b111111111111111111)

    def SetFilterIdF0(self, filterId):
        self.filter0Enabled = True
        self.savedFilterId0 = filterId

    def SetFilterIdF1(self, filterId):
        self.filter1Enabled = True
        self.savedFilterId1 = filterId

    def _ConfigureReceive(self):

        # initialize filters, control registers
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

        if self.filter0Enabled or self.filter1Enabled:
            # Enable mask filtering 
            with self.reg.RXM0ID as rxm0id:
                rxm0id.SID, rxm0id.EID = self.SplitExtendedId(0b11111111111111111111111111111)

        if self.filter0Enabled:
            with self.reg.RXF0ID as rxf0id:
                rxf0id.EXIDE = 1
                rxf0id.SID, rxf0id.EID = self.SplitExtendedId(self.savedFilterId0)

        if self.filter1Enabled:
            with self.reg.RXF1ID as rxf1id:
                rxf1id.EXIDE = 1
                rxf1id.SID, rxf1id.EID = self.SplitExtendedId(self.savedFilterId1)

        if (self.verbosePrint):
            print("- _ConfigureReceive()")

        with self.reg.RXB0CTRL as rxb0ctrl:
            # rxb0ctrl.RXM = self.reg.RXB0CTRL.RXM_TurnsMaskFiltersOffDevModeOnly
            rxb0ctrl.RXM = self.reg.RXB1CTRL.RXM_ExtendedFramesOnly
            # TODO: configure rollover into Rself.reg.RXB1CTRL.XB1
            # rxb0ctrl.BUKT = self.reg.RXB0CTRL.BUKT_RolloverEnabled

        with self.reg.RXB1CTRL as rxb1ctrl:
            rxb1ctrl.RXM = self.reg.RXB1CTRL.RXM_TurnsMaskFiltersOffDevModeOnly

        # Clear RX bits for Peek to work correctly after Initialize.
        with self.reg.CANINTF as canintf:
            canintf.RX0IF = 0
            canintf.RX1IF = 1 # Disable RX1IF

        if (self.verbosePrint):
            self.reg.RXB0CTRL.Print()
            self.reg.RXB1CTRL.Print()
            self.reg.CANINTF.Print()

    def SetLoopbackMode(self):
        """
        Configures the CAN controller in Loopback (debug) mode.
        Note: in this mode, no messages are sent by the transciver.
        """

        if self.verbosePrint:
            print(">> SetLoopbackMode()")
            self.reg.CANCTRL.Print()

        with self.reg.CANCTRL as canctrl:
            canctrl.REQOP = self.reg.CANCTRL.REQOP_Loopback
            assert canctrl.REQOP == self.reg.CANCTRL.REQOP_Loopback

        if self.verbosePrint:
            self.reg.CANCTRL.Print()

    def SetNormalMode(self):
        """
        Configures the CAN controller in Normal mode.
        This or SetLoopbackMode must be called after Initialize and before any of the Send/Recv functions.
        """
        if self.verbosePrint:
            print(">> SetNormalMode()")
            self.reg.CANCTRL.Print()

        with self.reg.CANCTRL as canctrl:
            assert canctrl.REQOP == self.reg.CANCTRL.REQOP_Configuration
            canctrl.REQOP = self.reg.CANCTRL.REQOP_Normal
            assert canctrl.REQOP == self.reg.CANCTRL.REQOP_Normal

        if self.verbosePrint:
            self.reg.CANCTRL.Print()

    def Send(self, msg, timeoutMilliseconds=None):
        """
        Sends a CAN Message.

        Args:
            timeoutMilliseconds: the timeout in milliseconds to wait for a new message.

        Returns:
            A CAN Message

        Raises:
            TimeoutError: if the timeoutMilliseconds passed without receiving any message.
        """

        # Send only with TBX0 to ensure message sequence is preserved.
        if (self.verbosePrint):
            print(">> Send({0}, {1})".format(msg, timeoutMilliseconds))

        timeStart = self._BeginSendTXB0(msg, timeoutMilliseconds)
        self._EndSendTXB0(timeoutMilliseconds, timeStart)

    def Recv(self, timeoutMilliseconds=None):
        """
        Receives a CAN Message.

        Args:
            timeoutMilliseconds: the timeout in milliseconds to wait for a new message.

        Returns:
            A CAN Message

        Raises:
            TimeoutError: if the timeoutMilliseconds passed without receiving any message.
        """

        if (self.verbosePrint):
            print(">> Recv({0})".format(timeoutMilliseconds))
        timeStart = self._BeginReceiveRXB0()
        return self._EndReceiveRXB0(timeoutMilliseconds, timeStart)

    def Peek(self):
        """
        Peeks the CAN bus for available messages.

        Returns:
            True if a message is available for Recv.

        Remarks:
            If Peek returns True, it is guaranteed that Recv will not block.
        """
        return self._PeekRXB0()

    def _BeginSendTXB0(self, msg, timeoutMilliseconds):
        txBufferId = 0
        with self.reg.TXB0CTRL as r_ctrl, self.reg.TXB0ID as r_id, self.reg.TXB0DATA as r_data, self.reg.TXB0DLC as r_dlc:
            return self._StartSend(msg, timeoutMilliseconds, r_ctrl, r_id, r_data, r_dlc, txBufferId)

    def _EndSendTXB0(self, timeoutMilliseconds, timeStart):
        txBufferId = 0
        sent = False
        while ((not sent) and self._CheckTimeout(timeoutMilliseconds, timeStart)):
            with self.reg.TXB0CTRL as r_ctrl:
                sent = self._PollSend(r_ctrl)

        if (not sent):
            with self.reg.TXB0CTRL as r_ctrl:
                self._AbortSend(r_ctrl, txBufferId)
        
    def _StartSend(self, msg, timeoutMilliseconds, r_ctrl, r_id, r_data, r_dlc, txBufferId):
        timeStart = datetime.now()

        # Verify if current buffer is not already trying to send.
        if r_ctrl.TXREQ != TXBnCTRLx.TXREQ_NotPending:
            raise IOError("Transmit already pending in buffer {0}.".format(txBufferId))

        # Clear interrupt flag
        with self.reg.CANINTF as r_canintf:
            if (txBufferId == 0):
                r_canintf.TX0IF = 0
            else:
                r_canintf.TX1IF = 0

        #  ExtendedID
        if (msg.extended_id):
            r_id.EXIDE = TXBnIDx.EXIDE_Enabled
            r_id.SID = (msg.arbitration_id >> 18) & 0b11111111111
            r_id.EID = (msg.arbitration_id) & 0b111111111111111111
        else:
            r_id.EXIDE = TXBnIDx.EXIDE_Disabled
            r_id.SID = msg.arbitration_id & 0b11111111111

        #  Data Length and Data
        r_dlc.RTR = TXBnDLCx.RTR_DataFrame
        if (msg.data == None):
            r_dlc.DLC = 0
        else:
            r_dlc.DLC = len(msg.data)
            r_data.DATA = msg.Serialize()

        # Start send
        r_ctrl.TXP = TXBnCTRLx.TXP_HighestMessagePriority
        r_ctrl.TXREQ = TXBnCTRLx.TXREQ_BufferPending
    
        if (self.verbosePrint):
            print ("- _StartSend(TXB{0})".format(txBufferId))
            r_ctrl.Print()
            r_id.Print()
            r_data.Print()
            r_dlc.Print()

        return timeStart

    def _PollSend(self, r_ctrl):
        if (r_ctrl.TXREQ != TXBnCTRLx.TXREQ_NotPending):
            if (self.verbosePrint):
                print("- _PollSend(delay={0})".format(self._txPollingIntervalSeconds))

            sleep(self._txPollingIntervalSeconds)
            return False
        else:
            return True
                        
    def _AbortSend(self, r_ctrl, txBufferId):
        if (r_ctrl.TXREQ == TXBnCTRLx.TXREQ_BufferPending):
            # Timeout: abort transmit:
            r_ctrl.TXREQ = TXBnCTRLx.TXREQ_NotPending
            if (self.verbosePrint):
                print("- _AbortSend()")
                r_ctrl.Print()

            raise TimeoutError("Transmit aborted in buffer {0}".format(txBufferId))

    def _CheckTimeout(self, timeoutMilliseconds, timeStart):
        return (timeoutMilliseconds == None) or ((datetime.now() - timeStart).total_seconds() * 1000 < timeoutMilliseconds)

    def _BeginReceiveRXB0(self):
        timeStart = datetime.now()

        if (self.verbosePrint):
            print("_BeginReceiveRXB0(RBX0)")
            self.reg.CANINTF.Print()

        return timeStart

    def _EndReceiveRXB0(self, timeoutMilliseconds, timeStart):
        rxBufferId = 0

        received = False
        while ((not received) and self._CheckTimeout(timeoutMilliseconds, timeStart)):
            received = self._PollRecv(rxBufferId)

        if (not received):
            self._AbortReceive(rxBufferId)

        m = None
        d = 0
        with self.reg.RXB0ID as r_id, self.reg.RXB0DLC as r_dlc, self.reg.RXB0DATA as r_data:
            m = self._CreateMessage(r_id, r_dlc, r_data)
            d = r_data.val
            # print("Data : ", hex(d))
        
        # Clear interrupt flag.
        if m != None:
            self.reg.CANINTF.Zero()
            return m


    def _PeekRXB0(self):
        rxBufferId = 0
        return self._Peek(rxBufferId)

    def _Peek(self, rxBufferId):
        received = False
        with self.reg.CANINTF as r_canintf:
            if (rxBufferId == 0):
                if (r_canintf.RX0IF == 1):
                    received = True
            else:
                if (r_canintf.RX1IF == 1):
                    received = True

        return received

    def _PollRecv(self, rxBufferId):
        received = self._Peek(rxBufferId)
        if (not received):
            if (self.verbosePrint):
                print("- _PollRecv(RXB{0} delay={1})".format(rxBufferId, self._txPollingIntervalSeconds))
            # sleep(self._rxPollingIntervalSeconds)

        return received

    def _AbortReceive(self, rxBufferId):
        with self.reg.CANINTF as r_canintf:
            if (self.verbosePrint):
                print("- _AbortReceive()")
                r_canintf.Print()
        raise TimeoutError("Receive aborted in buffer {0}".format(rxBufferId))

    def _CreateMessage(self, r_id, r_dlc, r_data):
        if (self.verbosePrint):
            print ("- _CreateMessage()")
            r_id.Print()
            r_dlc.Print()
            r_data.Print()

        #  Check ExtendedID
        if (r_id.IDE == RXBnIDx.IDE_ReceivedExtendedFrame):
            extended_id = True
        elif (r_id.IDE == RXBnIDx.IDE_ReceivedStandardFrame):
            extended_id = False
        else:
            raise IOError("Unknown arbitration frame mode.")

        if (extended_id):
            arbitration_id = (r_id.SID << 18) + r_id.EID
        else:
            arbitration_id = r_id.SID
        
        msg = Message(arbitration_id, None, extended_id)

        #  Data Length and Data
        msg.DeSerialize(r_data.DATA, r_dlc.DLC)
        
        return msg

class Message(object):

    _maxBytes = 8

    def __init__(self, arbitration_id=0, data=None, extended_id=True):
        """
        Creates a new CAN Message

        Args:
            arbitration_id: the message identifier and priority.
            data: a byte array of at most 8 bytes. This can be None for an empty data-message.
                  Note: DLC will be automatically set based on the data length.
            extended_id: allows 29bit arbitration_ids (default). If False, the message must have an 11-bit standard arbitration Id.

        Raises:
            ValueError: if arguments are out of range.
        """

        self.extended_id = extended_id
        if (extended_id):
           if ((arbitration_id > 0x1FFFFFFF) or (arbitration_id < 0)):
               raise ValueError("arbitration_id must be at most 29 bits in extended mode.")
        elif ((arbitration_id > 0x7FF) or (arbitration_id < 0)):
               raise ValueError("arbitration_id must be at most 11 bits in standard mode.") 

        self.arbitration_id = arbitration_id
        if ((data != None) and (len(data) > self._maxBytes)):
            raise ValueError("data length must be between 1 and 8 bytes.")
        self.data = data

    def Serialize(self):
        """
        Serializes the data into a single 64bit integer.
        """

        serializedVal = 0
        for i in range(self._maxBytes):
            byteVal = 0
            if (i < len(self.data)):
                byteVal = self.data[i]

            serializedVal = (serializedVal << 8) + byteVal
        
        return serializedVal
    
    def DeSerialize(self, serializedVal, dlc):
        """
        Deserializes the passed 64bit integer and dlc into the message's data property.

        Args:
            serializedVal: 64bit integer containing the CAN data
            dlc: the data length
        """

        if (dlc > self._maxBytes):
            raise ValueError("dlc must be less then 8")

        if (dlc == 0):
            self.data = None
            return

        self.data = []
        for i in range(self._maxBytes):
            if (i >= self._maxBytes - dlc):
                byteVal = serializedVal & 0xFF
                self.data.insert(0, byteVal)

            serializedVal = serializedVal >> 8

    def __str__(self):
        if (self.data != None):
            data_hex = ''.join('{:02X} '.format(x) for x in self.data)
        else:
            data_hex = '<empty>'

        arbitration_hex = '{0:b}'.format(self.arbitration_id)

        return "CAN_MESSAGE: arb_id: {0} data: {1}".format(arbitration_hex, data_hex)

