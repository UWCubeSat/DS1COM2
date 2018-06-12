# Copyright (C) 2018 Quick2Space.org under the MIT License (MIT)
# See the LICENSE.txt file in the project root for more information.

from metalcore import RegisterGroup, Register, Field, Access


#
# Register structures
# These are used to define the bit-level structure of an register 
# instance
#


#
# Control registers
#


# CAN control register structure
# Used to set CAN operational mode, request TX abort, set one-shot mode, 
# CKLOUT pin enable, and the clock pin prescaler
class CANCTRLx(Register):

    REQOP_Normal        = 0b000
    REQOP_Sleep         = 0b001
    REQOP_Loopback      = 0b010
    REQOP_ListenOnly    = 0b011
    REQOP_Configuration = 0b100
    
    # Request operation mode
    REQOP = Field(7, 3, Access.RW, REQOP_Configuration)

    ABAT_RequestAbort           = 0b1
    ABAT_TerminateRequestAbort  = 0b0

    # Control aborting all pending transmissions
    ABAT = Field(4, 1, Access.RW, 0b0)
 
    # One-shot mode
    # 1 = enabled (messages will only attempt to transmit one time)
    # 0 = disabled (messages will reattempt to transmit if required)
    OSM     = Field(3, 1, Access.RW, 0b0)

    # CLKOUT pin enable
    # 1 = enabled
    # 0 = disabled (high-Z)
    CLKEN   = Field(2, 1, Access.RW, 0b1)

    # CLKOUT pin prescaler
    # 00 = freq. CLKOUT = System clock/1
    # 01 = freq. CLKOUT = System clock/2
    # 10 = freq. CLKOUT = System clock/4
    # 11 = freq. CLKOUT = System clock/8
    CLKPRE  = Field(1, 2, Access.RW, 0b11)


# CAN status register structure
# Used to read the success of setting the CAN operational mode and 
# the received interrupts
class CANSTATx(Register):

    OPMOD_Normal        = 0b000
    OPMOD_Sleep         = 0b001
    OPMOD_Loopback      = 0b010
    OPMOD_ListenOnly    = 0b011
    OPMOD_Configuration = 0b100
    
    # Request operation mode
    OPMOD   = Field(7, 3, Access.R, OPMOD_Configuration)

    # Bit 4 not implemented (reads 0)

    ICOD_NoInterrupt        = 0b000
    ICOD_ErrorInterrupt     = 0b001
    ICOD_WakeUpInterrupt    = 0b010
    ICOD_TXB0_Interrupt     = 0b011
    ICOD_TXB1_Interrupt     = 0b100
    ICOD_TXB2_Interrupt     = 0b101
    ICOD_RXB0_Interrupt     = 0b110
    ICOD_RXB1_Interrupt     = 0b111

    # Interrupt Flag Code bits
    ICOD    = Field(3, 3, Access.R, ICOD_NoInterrupt)

    # Bit 0 not implemented (reads 0)

# Configuration 1 register structure
# For setting synchronization jump bit widths and Baud Rate prescaler 
# Datasheet notes: (see see 3.8 Can Bit Time in MCP25625 datasheet)
# - Synchronization Jump Width is the maximum amount of PHSEG1 and 
#   PHSEG2 that can be adjusted during resynchronization
# - T_Q = the length of a Time Quanta
#       T_Q = 2 x (BRP + 1) x Time_OSC = 2 x (BRP + 1)/Freq_OSC
class CNF1x(Register):

    SJW_Length4TQ = 0b11
    SJW_Length3TQ = 0b10
    SJW_Length2TQ = 0b01
    SJW_Length1TQ = 0b00

    # Synchronization Jump Width Length bits (as a multiple of T_Q)
    SJW = Field(7, 2, Access.RW, SJW_Length1TQ)

    # Baud Rate Prescaler bits 
    # Used to define T_Q as a function of the HW oscillator
    BRP = Field(5, 6, Access.RW, 0b000000)


# Configuration 2 register structure
# For setting PS2, PS1, PRSEG timing lengths 
#   and Sample configuration count
# Datasheet notes: (see 3.8 CAN Bit Time in MCP25625 datasheet)
# - Nominal Bit Time is made of four segments:
#    * SYNC (synchronization segment). Length = 1 T_Q
#    * PRSEG (propagation segment). Length = 1..8 T_Q (configured 
#       through CNF2.PRSEG field)
#    * PHSEG1 (phase segment 1, before sample point). 
#       Length = 1..8 T_Q (see CNF2.PHSEG1 field)
#    * PHSEG2 (phase segment 2, after sample point). 
#       Length = 2..8 T_Q (see fields CNF2.BTLMODE, CNF3.PHSEG2, etc)
# - Information processing time: 
#       IPT = 2 x T_Q
class CNF2x(Register):

    # Length of PS2 is max(PS1, IPT)
    BTLMODE_Max_PS1_IPT = 0b0 

    # Length of PS2 is determined by the CNF3.PHSEG2
    BTLMODE_CNF3_PHSEG2 = 0b1

    # PS2 Bit Time Length
    BTLMODE = Field(7, 1, Access.RW, BTLMODE_Max_PS1_IPT)

    # Number of times the bus line is sampled at the sample point
    SAM_ThreePointSample = 0b1
    SAM_OnePointSample = 0b0

    # Sample Point configuration bit
    SAM = Field(6, 1, Access.RW, SAM_OnePointSample)

    # PS1 length bits
    # PS1 = (PHSEG1 + 1) x T_Q
    PHSEG1 = Field(5, 3, Access.RW, 0b000)

    # Propagation Segment (PRS) length bits
    # PRS = (PRSEG + 1) x T_Q
    PRSEG = Field(2, 3, Access.RW, 0b000)


# Configuration 3 register structure
# For setting PS2, PS1 and PRSEG timing lengths
# See above
class CNF3x(Register):

    # CLKOUT pin is enabled for SOF signal 
    SOF_CLKOUT_SOF = 0b1

    # CLKOUT pin is enabled for clock out function
    SOF_CLKOUT_CLOCK_OUT = 0b0

    # Start-of-frame signal bit
    # Only valid when CANCTRL.CLKEN = 1
    SOF = Field(7, 1, Access.RW, SOF_CLKOUT_CLOCK_OUT)

    WAKFIL_Enabled = 0b1
    WAKFIL_Disabled = 0b0

    WAKFIL = Field(6, 1, Access.RW, WAKFIL_Disabled)

    # Bits 5..3 not implemented (read zero)

    PHSEG2_DefaultSetting = 0b000
    PHSEG2_MinimumValidSetting = 0b001

    # PS2 length bits 
    # PS2 = (PHSEG2 + 1) x T_Q
    # Warning: minimum valid setting for PS2 is 2 x T_Q
    # (see datasheet 4-28)
    PHSEG2 = Field(2, 3, Access.RW, PHSEG2_DefaultSetting)


# Transmit error counter register
class TECx(Register):

    # Transmit Error Count bits
    TEC = Field(7, 8, Access.R, 0)


# Receive error counter register
class RECx(Register):

    # Receive Error Count bits
    REC = Field(7, 8, Access.R, 0)


# Error flag register
class EFLGx(Register):

    # Receive Buffer 1 Overflow Flag bit
    # - Set when a valid message is received for RXB1 and RX1IF bit in 
    #   the CANINTF register is 1
    # - Must be reset by MCU
    RX1OVR = Field(7, 1, Access.R, 0)

    # Receive Buffer 0 Overflow Flag bit
    # - Set when a valid message is received for RXB0 and CANINTF.RX0IF 
    #   bit in the CANINTF register is 1
    # - Must be reset by MCU
    RX0OVR = Field(6, 1, Access.R, 0)

    # Bus-Off Error Flag bit
    # - Bit set when TEC reaches 255
    # - Reset after a successful bus recovery sequence
    TXBO = Field(5, 1, Access.R, 0)

    # Transmit Error-Passive Flag bit
    # - Set when TEC is equal to or greater than 128
    # - Reset when TEC is less than 128
    TXEP = Field(4, 1, Access.R, 0)

    # Receive Error-Passive Flag bit
    # - Set when REC is equal to or greater than 128
    # - Reset when REC is less than 128
    RXEP = Field(3, 1, Access.R, 0)

    # Transmit Error Warning Flag bit
    # - Set when TEC is equal to or greater than 96
    # - Reset when TEC is less than 96
    TXWAR = Field(2, 1, Access.R, 0)

    # Receive Error Warning Flag bit
    # - Set when REC is equal to or greater than 96
    # - Reset when REC is less than 96
    RXWAR = Field(1, 1, Access.R, 0)

    # Error Warning Flag bit
    # - Set when TEC or REC is equal to or greater than 96 
    #   (TXWAR or RXWAR = 1)
    # - Reset when both REC and TEC are less than 96
    EWARN = Field(0, 1, Access.R, 0)


# Interrupt enable register
class CANINTEx(Register):

    # Message Error Interrupt Enable bit
    # 1 = Interrupt on error during message reception or transmission
    # 0 = Disabled
    MERRE = Field(7, 1, Access.RW, 0)

    # Wake-up Interrupt Enable bit
    # 1 = Interrupt on CAN bus activity
    # 0 = Disabled
    WAKIE = Field(6, 1, Access.RW, 0)

    # Error Interrupt Enable bit (multiple sources in the EFLG register)
    # 1 = Interrupt on EFLG error condition change
    # 0 = Disabled
    ERRIE = Field(5, 1, Access.RW, 0)

    # Transmit Buffer 2 Empty Interrupt Enable bit
    # 1 = Interrupt on TXB2 becoming empty
    # 0 = Disabled
    TX2IE = Field(4, 1, Access.RW, 0)

    # Transmit Buffer 1 Empty Interrupt Enable bit
    # 1 = Interrupt on TXB1 becoming empty
    # 0 = Disabled
    TX1IE = Field(3, 1, Access.RW, 0)

    # Transmit Buffer 0 Empty Interrupt Enable bit
    # 1 = Interrupt on TXB0 becoming empty
    # 0 = Disabled
    TX0IE = Field(2, 1, Access.RW, 0)

    #  Receive Buffer 1 Full Interrupt Enable bit
    # 1 = Interrupt when message received in RXB1
    # 0 = Disabled
    RX1IE = Field(1, 1, Access.RW, 0)

    #  Receive Buffer 0 Full Interrupt Enable bit
    # 1 = Interrupt when message received in RXB1
    # 0 = Disabled
    RX1IE = Field(0, 1, Access.RW, 0)


# Interrupt flag register
class CANINTFx(Register):

    # Message Error Interrupt Flag bit
    # 1 = Interrupt pending (must be cleared by MCU to reset interrupt)
    # 0 = No interrupt pending
    MERRF = Field(7, 1, Access.RW, 0)

    # Wake-up Interrupt Flag bit
    # 1 = Interrupt pending (must be cleared by MCU to reset interrupt)
    # 0 = No interrupt pending
    WAKIF = Field(6, 1, Access.RW, 0)

    # Error Interrupt Flag bit (multiple sources in the EFLG register)
    # 1 = Interrupt pending (must be cleared by MCU to reset interrupt)
    # 0 = No interrupt pending
    ERRIF = Field(5, 1, Access.RW, 0)

    # Transmit Buffer 2 Empty Interrupt Flag bit
    # 1 = Interrupt pending (must be cleared by MCU to reset interrupt)
    # 0 = No interrupt pending
    TX2IF = Field(4, 1, Access.RW, 0)

    # Transmit Buffer 1 Empty Interrupt Flag bit
    # 1 = Interrupt pending (must be cleared by MCU to reset interrupt)
    # 0 = No interrupt pending
    TX1IF = Field(3, 1, Access.RW, 0)

    # Transmit Buffer 0 Empty Interrupt Flag bit
    # 1 = Interrupt pending (must be cleared by MCU to reset interrupt)
    # 0 = No interrupt pending
    TX0IF = Field(2, 1, Access.RW, 0)

    #  Receive Buffer 1 Full Interrupt Flag bit
    # 1 = Interrupt pending (must be cleared by MCU to reset interrupt)
    # 0 = No interrupt pending
    RX1IF = Field(1, 1, Access.RW, 0)

    #  Receive Buffer 0 Full Interrupt Flag bit
    # 1 = Interrupt pending (must be cleared by MCU to reset interrupt)
    # 0 = No interrupt pending
    RX0IF = Field(0, 1, Access.RW, 0)


#
# Transmit buffer registers
#


# TxnRTS pin control and status register
class TXRTSCTRLx(Register):

    # bits 7..6 not implemented (reads 0)

    # - state bits (read-only):
    #     1 = Reads state of TXnRTS pin when in Digital Input mode
    #     0 = Reads as 0 when pin is in Request-to-Send mode

    # Tx2RTS pin state bit
    B2RTS = Field(5, 1, Access.R, 0)

    # Tx1RTS pin state bit
    B1RTS = Field(4, 1, Access.R, 0)

    # Tx0RTS pin state bit
    B0RTS = Field(3, 1, Access.R, 0)

    # - mode bits (read-write):
    #     1 = Pin is used to request message transmission of the 
    #           corresponding TXBx buffer (on the falling edge)
    #     0 = Digital input
    BnRTSN_PinMode = 1
    BnRTSM_DigitalMode = 0

    # Tx2RTS pin mode bit
    B2RTSM = Field(2, 1, Access.RW, BnRTSM_DigitalMode)

    # Tx1RTS pin mode bit
    B1RTSM = Field(1, 1, Access.RW, BnRTSM_DigitalMode)

    # Tx0RTS pin mode bit
    B0RTSM = Field(0, 1, Access.RW, BnRTSM_DigitalMode)


# Transmit buffer x control register
class TXBnCTRLx(Register):

    # bit 7 not implemented (reads 0)

    # TX abort flag values
    ABTF_MessageAborted = 1
    ABTF_MessageSucceeded = 0

    # Message aborted flag bit (during transmission)
    ABTF = Field(6, 1, Access.R, ABTF_MessageSucceeded)

    MLOA_ArbitrationLost = 1
    MLOA_ArbitrationNotLost = 0

    # Message lost arbitration bit (during transmission) 
    MLOA = Field(5, 1, Access.R, MLOA_ArbitrationNotLost)

    TXERR_BusError = 1
    TXERR_NoBusError = 0

    # Transmission error detected bit
    TXERR = Field(4, 1, Access.R, TXERR_NoBusError)

    # Buffer is currently pending transmission (MCU sets this bit to 
    # request message be transmitted - bit is automatically cleared 
    # when the message is sent)
    TXREQ_BufferPending = 1

    # Buffer is not currently pending transmission (MCU can clear this 
    # bit to request a message abort)
    TXREQ_NotPending = 0

    # Message transmit request bit
    TXREQ = Field(3, 1, Access.RW, TXREQ_NotPending)

    # bit 2 not implemented (reads 0)

    # Tx message priority values
    TXP_HighestMessagePriority          = 0b11
    TXP_HighIntermediateMessagePriority = 0b10
    TXP_LowIntermediateMessagePriority  = 0b01
    TXP_LowestMessagePriority           = 0b00

    # Transmit buffer priority
    TXP = Field(1, 2, Access.RW, TXP_LowestMessagePriority)


# TX Identifier registers
# Structure (4 bytes):
# - Bits 31..24 TXBnSIDH: SID<10:3>
# - Bits 23..16 TXBnSIDL: SID<2:0>, #, EXIDE, #, EID<17:16>
# - Bits 15..8  TXBnEID8: EID<15:8>
# - Bits 7..0   TXBnEID0: EID<7:0>
class TXBnIDx(Register):

    # 11-bit Standard Identifier
    SID = Field(31, 11, Access.RW, 0b00000000000)

    # Bit 20 not implemented (reads 0) 

    EXIDE_Enabled = 0b1
    EXIDE_Disabled = 0b0

    # Extended Identifier Enable Bit
    EXIDE = Field(19, 1, Access.RW, EXIDE_Disabled)

    # Bit 18 not implemented (reads 0)

    # 18-bit Extended identifier
    EID = Field(17, 18, Access.RW, 0b000000000000000000)


# TX buffer data length code register
class TXBnDLCx(Register):

    # Bit 7 not implemented (reads 0) 

    RTR_RemoteTransmitRequest = 1
    RTR_DataFrame = 0

    # Remote transmission request bit 
    # Indicates the type of the next transmit message: remote tx 
    # request or data frame
    RTR = Field(6, 1, Access.RW, 0b0)

    # Bit 5, 4 not implemented (reads 0)

    # Data Length Code bits
    # Sets the number of data bytes to be transmitted
    # Note: maximum 8 bytes transmitted
    DLC = Field(3, 4, Access.RW, 0b0000)


# TX Data buffers 
# TODO - could be optimized for smaller TX footprint in SPI? 
# (maybe with multiple overlapping register mappings)
class TXBnDATAx(Register):

    # 8 bytes
    DATA = Field(63, 64, Access.RW)


#
# Receive buffer registers
#


# Receive buffer n control register (base class)
class RXBnCTRLx(Register):

    # Bit 7 not implemented (reads 0)

    # Turns mask/filters off, receives any message 
    # (for development only, as it also allows access to MAB on error)
    RXM_TurnsMaskFiltersOffDevModeOnly = 0b11
    
    # Receive only valid messages with extended identifiers that 
    # meet filter criteria
    RXM_ExtendedFramesOnly = 0b10

    # Receive only valid messages with standard identifiers that meet 
    # filter criteria. Extended ID filter registers RXFnEID8 and RXFnEID0
    # are ignored for the messages with standard IDs.
    RXM_StandardFramesOnly = 0b01

    # Receives all valid messages using either Standard or Extended 
    # Identifiers that meet filter criteria; 
    # 
    # Note - if standard frames, then Extended ID Filter registers 
    # RXFnEID8 and RXFnEID0 (RXFx.EID<15:0>) are applied to 
    # the first two bytes of data in the messages 
    RXM_FilteredMessages = 0b00

    # Receive Buffer Operating Mode bits
    RXM = Field(6, 2, Access.RW, RXM_FilteredMessages)

    # Bit 4 not implemented (reads 0)

    RXRTR_RemoteTransferRequestReceived = 0b1
    RXRTR_NoRemoteTransferRequest = 0b0

    # Received Remote Transfer Request bit
    RXRTR = Field(3, 1, Access.R, RXRTR_NoRemoteTransferRequest)


# Receive buffer 0 control register
class RXB0CTRLx(RXBnCTRLx):

    # RXBn message will roll over and be written to RXB1 if RXBn is full
    BUKT_RolloverEnabled = 0b1

    # Rollover is disabled 
    BUKT_RolloverDisabled = 0b0

    # Rollover Enable Bit
    BUKT = Field(2, 1, Access.RW, BUKT_RolloverDisabled)

    # Read-Only Copy of BUKT bit (used internally by the MCP25625)
    BUKT1 = Field(1, 1, Access.R, BUKT_RolloverDisabled)

    # Acceeptance filter 1 (RXF1)
    FILHIT0_RXF1 = 0b1

    # Acceeptance filter 0 (RXF0)
    FILHIT0_RXF0 = 0b0

    # Filter Hit bit - Indicates which acceptance filter enabled the 
    # reception of a message.
    # Note: If a rollover from RXB0 to RXB1 occurs, the FILHIT0 bit 
    # will reflect the filter that accepted the message that rolled over
    FILHIT0 = Field(0, 1, Access.R, FILHIT0_RXF0)


# Receive buffer 1 control register
class RXB1CTRLx(RXBnCTRLx):

    # Acceeptance filter 5 (RXF5)
    FILHIT_RXF5 = 0b101

    # Acceeptance filter 4 (RXF5)
    FILHIT_RXF4 = 0b100

    # Acceeptance filter 3 (RXF2)
    FILHIT_RXF3 = 0b011

    # Acceeptance filter 2 (RXF2)
    FILHIT_RXF2 = 0b010

    # Acceeptance filter 1 (RXF1 only if BUKT bit is set in RXB0CTRL)
    FILHIT_RXF1 = 0b001

    # Acceeptance filter 0 (RXF0 only if BUKT bit is set in RXB0CTRL)
    FILHIT_RXF0 = 0b000

    # Filter Hit bit - Indicates which acceptance filter enabled the 
    # reception of a message.
    FILHIT = Field(2, 3, Access.R, FILHIT_RXF0)


# RxnBF pin control and status register
class BFPCTRLx(Register):

    # Bits 7, 6 not implemented (read as zero)

    # Rx1BF Pin State bit (Digital Output mode only)
    # Reads as ‘0’ when Rx1BF is configured as an interrupt pin
    B1BFS = Field(5, 1, Access.RW, 0b0)

    # Rx0BF Pin State bit (Digital Output mode only)
    # Reads as ‘0’ when Rx0BF is configured as an interrupt pin
    B0BFS = Field(4, 1, Access.RW, 0b0)

    # 1 = Pin function is enabled
    #     Pin operation mode is determined by the BnBFM bit
    BnBFE_PinEnabled = 0b1

    # 0 = Pin function is disabled, pin goes to the high-impedance state
    BnBFE_PinDisabled = 0b0

    # Rx1BF Pin Function Enable bit 
    # 1 = Pin function is enabled 
    #     operation mode is determined by the B1BFM bit
    # 0 = Pin function is disabled, pin goes to the high-impedance state
    B1BFE = Field(3, 1, Access.RW, BnBFE_PinDisabled)

    # Rx0BF Pin Function Enable bit
    # 1 = Pin function is enabled 
    #     operation mode is determined by the B0BFM bit
    # 0 = Pin function is disabled, pin goes to the high-impedance state
    B0BFE = Field(2, 1, Access.RW, BnBFE_PinDisabled)

    # 1 = RxnBF pin is used as an interrupt when a valid message
    #     is loaded into RXBn
    BnBFM_PinInterruptMode = 0b1

    # 0 = Digital Output mode
    BnBFM_DigitalOutputMode = 0b0

    # 1 = Pin is used as an interrupt when a valid message 
    #     is loaded into RXB1
    # 0 = Digital Output mode
    B1BFM = Field(1, 1, Access.RW, BnBFM_DigitalOutputMode)

    # 1 = Pin is used as an interrupt when a valid message 
    #     is loaded into RXB0
    # 0 = Digital Output mode
    B0BFM = Field(0, 1, Access.RW, BnBFM_DigitalOutputMode)


# RX Identifier registers
# Structure (4 bytes):
# - Bits 31..24 TXBnSIDH: SID<10:3>
# - Bits 23..16 TXBnSIDL: SID<2:0>, SRR, IDE, #, EID<17:16>
# - Bits 15..8  TXBnEID8: EID<15:8>
# - Bits 7..0   TXBnEID0: EID<7:0>
class RXBnIDx(Register):

    # 11-bit Standard Identifier
    SID = Field(31, 11, Access.R, 0b00000000000)

    SRR_RemoteTransmitRequestReceived = 0b1
    SRR_StandardDataFrameReceived = 0b0

    # Standard Frame Remote Transmit Request bit 
    # (valid only if the IDE bit = 0)
    SRR = Field(20, 1, Access.R, SRR_StandardDataFrameReceived)

    # Received message was an extended frame
    IDE_ReceivedExtendedFrame = 0b1
    IDE_ReceivedStandardFrame = 0b0

    # Extended Identifier Flag Bit. This bit indicates whether 
    # the received message was a standard or an extended frame.
    IDE = Field(19, 1, Access.R, IDE_ReceivedStandardFrame)

    # Bit 18 not implemented (reads 0)

    # 18-bit Extended identifier
    EID = Field(17, 18, Access.R, 0b000000000000000000)


# RX buffer data length code register
class RXBnDLCx(Register):

    # Bit 7 not implemented (reads 0) 

    # 1 = Extended frame Remote Transmit Request received
    RTR_ExtendedRemoteTransmitRequestReceived = 1

    # 0 = Extended data frame received
    RTR_ExtendedDataFrameReceived = 0

    # Extended Frame Remote Transmission Request bit
    # (valid only when the IDE bit in the RXBnSIDL register is ‘1’)
    RTR = Field(6, 1, Access.R, RTR_ExtendedDataFrameReceived)

    # Reserved Bit 1
    RB1 = Field(5, 1, Access.R, 0b0)

    # Reserved Bit 0
    RB0 = Field(4, 1, Access.R, 0b0)

    # Data Length Code bits
    # Indicates the number of data bytes that were received
    DLC = Field(3, 4, Access.R, 0b0000)


# RX Data buffers 
# TODO - could be optimized for smaller RX footprint in SPI? 
# (maybe with multiple overlapping register mappings)
class RXBnDATAx(Register):

    # 8 bytes
    DATA = Field(63, 64, Access.R)


#
# Acceptance filter and mask registers
#
# Note: The Mask and Filter registers read all ‘0’s when in any mode, 
# except Configuration mode.
#


# Filter registers
# Structure (4 bytes):
# - Bits 31..24 RXFnSIDH: SID<10:3>
# - Bits 23..16 RXFnSIDL: SID<2:0>, #, EXIDE, #, EID<17:16>
# - Bits 15..8  RXFnEID8: EID<15:8>
# - Bits 7..0   RXFnEID0: EID<7:0>
class RXFnIDx(Register):

    # 11-bit Standard Identifier
    SID = Field(31, 11, Access.RW, 0b00000000000)

    # Bit 20 not implemented (reads 0) 

    EXIDE_ExtendedFramesFilter = 0b1
    EXIDE_StandardFramesFilter = 0b0

    # Extended Identifier Enable Bit
    # 1 = Filter is applied only to extended frames
    # 0 = Filter is applied only to standard frames
    EXIDE = Field(19, 1, Access.RW, EXIDE_StandardFramesFilter)

    # Bit 18 not implemented (reads 0)

    # 18-bit Extended identifier
    #
    # Note: these bits hold the filter bits to be applied to 
    # the Extended Identifier portion of a  received message or
    # (for RX buffer 0 only?) to bytes 0 and 1 in received data 
    # if corresponding with RXM<1:0> = 00 and EXIDE = 0.
    EID = Field(17, 18, Access.RW, 0b000000000000000000)


# Mask registers
# Structure (4 bytes):
# - Bits 31..24 RXMnSIDH: SID<10:3>
# - Bits 23..16 RXMnSIDL: SID<2:0>, #, #, #, EID<17:16>
# - Bits 15..8  RXMnEID8: EID<15:8>
# - Bits 7..0   RXMnEID0: EID<7:0>
class RXMnIDx(Register):

    # 11-bit Standard Identifier
    SID = Field(31, 11, Access.RW, 0b00000000000)

    # Bits 20, 19, 18 not implemented (reads 0)

    # 18-bit Extended identifier
    #
    # Note: these bits hold the filter bits to be applied to 
    # the Extended Identifier portion of a  received message or
    # (for RX buffer 0 only?) to bytes 0 and 1 in received data 
    # if corresponding with RXM<1:0> = 00 and EXIDE = 0.
    # (unclear which EXIDE?)
    EID = Field(17, 18, Access.RW, 0b000000000000000000)


#
#  Register instances
#


class MCP25625_RegisterGroup(RegisterGroup):

    # General control and status registers

    CANSTAT = CANSTATx().BindToAddress(0x0E)
    CANCTRL = CANCTRLx().BindToAddress(0x0F)

    CNF1 = CNF1x().BindToAddress(0x2A)
    CNF2 = CNF2x().BindToAddress(0x29)
    CNF3 = CNF3x().BindToAddress(0x28)

    TEC = TECx().BindToAddress(0x1C)
    REC = RECx().BindToAddress(0x2C)

    EFLG = EFLGx().BindToAddress(0x2D)

    CANINTE = CANINTEx().BindToAddress(0x2B)
    CANINTF = CANINTFx().BindToAddress(0x2C)

    # Transmission registers: control, ID and data

    # TX global control
    TXRTSCTRL = TXRTSCTRLx().BindToAddress(0x0D)

    # TX Buffer control
    TXB0CTRL = TXBnCTRLx().BindToAddress(0x30)
    TXB1CTRL = TXBnCTRLx().BindToAddress(0x40)
    TXB2CTRL = TXBnCTRLx().BindToAddress(0x50)
   
    # TX Standard ID and extended ID   
    TXB0ID = TXBnIDx().BindToAddress(0x31, 4)
    TXB1ID = TXBnIDx().BindToAddress(0x41, 4)
    TXB2ID = TXBnIDx().BindToAddress(0x51, 4)

    # TX Data length code
    TXB0DLC = TXBnDLCx().BindToAddress(0x35)
    TXB1DLC = TXBnDLCx().BindToAddress(0x45)
    TXB2DLC = TXBnDLCx().BindToAddress(0x55)

    # TX Data buffers
    TXB0DATA = TXBnDATAx().BindToAddress(0x36, 8)
    TXB1DATA = TXBnDATAx().BindToAddress(0x46, 8)
    TXB2DATA = TXBnDATAx().BindToAddress(0x56, 8)

    # Reception registers: control, ID, data

    # RxnBF pin mode and status (pin interrupt or digital mode)
    BFPCTRL = BFPCTRLx().BindToAddress(0x0C)

    # Receive buffer control registers
    RXB0CTRL = RXB0CTRLx().BindToAddress(0x60)
    RXB1CTRL = RXB1CTRLx().BindToAddress(0x70)

    # Received identifiers
    RXB0ID = RXBnIDx().BindToAddress(0x61, 4)
    RXB1ID = RXBnIDx().BindToAddress(0x71, 4)

    # Receive buffers data length
    RXB0DLC = RXBnDLCx().BindToAddress(0x65)
    RXB1DLC = RXBnDLCx().BindToAddress(0x75)

    # RX Data buffers
    RXB0DATA = RXBnDATAx().BindToAddress(0x66, 8)
    RXB1DATA = RXBnDATAx().BindToAddress(0x76, 8)

    # Acceptance filter and mask registers

    # Filters 0..5
    RXF0ID = RXFnIDx().BindToAddress(0x00, 4)
    RXF1ID = RXFnIDx().BindToAddress(0x04, 4)
    RXF2ID = RXFnIDx().BindToAddress(0x08, 4)
    RXF3ID = RXFnIDx().BindToAddress(0x10, 4)
    RXF4ID = RXFnIDx().BindToAddress(0x14, 4)
    RXF5ID = RXFnIDx().BindToAddress(0x18, 4)

    # Masks 0..1
    RXM0ID = RXMnIDx().BindToAddress(0x20, 4)
    RXM1ID = RXMnIDx().BindToAddress(0x24, 4)

