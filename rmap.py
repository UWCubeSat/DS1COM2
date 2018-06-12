#!/usr/bin/env python3
# Copyright (C) 2018 Quick2Space.org under the MIT License (MIT)
# See the LICENSE.txt file in the project root for more information.

import argparse

import MCP25625_hal as hal

import colored as clr


# Test utility for low-level access to MCP25625 register map
class rmap:

   def __init__(self):
      self.hal = hal.MCP25625_hal()
      self.ra = self.GetRegisters()
      self.rc = self.GetRegisterColors()

   def close(self):
      self.hal.close()

   def __getitem__(self, memAddressByte):
      return self.hal.ReadByte(memAddressByte)

   def __setitem__(self, memAddressByte, byteValue):
      self.hal.WriteByte(memAddressByte, byteValue)

   def DumpMemHex(self):
      l = "LSB\HSB "
      for v in range(0,8):
         l += " {0:04b}".format(v)

      print(l)

      for v in range(0,16):
         l = ""
         for h in range(0,8):
            a = (h << 4) + v
            b = self[a]
            fgc = clr.fg(self.rc[v][h])
            fgr = clr.attr('reset')
            l += "  {0}{1:02x}{2} ".format(fgc, b, fgr)

         print("{0:04b}: ".format(v), l)

   def DumpMemBin(self):
      l = "LSB \ MSB  "
      for v in range(0,8):
         l += "{0:04b}xxxx ".format(v)

      print(l)

      for v in range(0,16):
         l = ""
         for h in range(0,8):
            a = (h << 4) + v
            b = self[a]
            fgc = clr.fg(self.rc[v][h])
            fgr = clr.attr('reset')
            l += "{0}{1:08b}{2} ".format(fgc, b, fgr)

         print("xxxx{0:04b}: ".format(v), l)

   def DumpRegBin(self):
      l = "   LSB \ MSB"
      for v in range(0,8):
         l += " ---- {0:04b}.xxxx ----- ".format(v)

      print(l)

      for lsb in range(0,16):
         l = ""
         for msb in range(0,8):
            a = (msb << 4) + lsb
            b = self[a]
            fgc = clr.fg(self.rc[lsb][msb])
            fgr = clr.attr('reset')
            l += "{0}{1:>9}/{2:02x}={3:08b}{4} ".format(fgc, 
                                                  self.ra[lsb][msb], a, b, 
                                                  fgr)

         print("xxxx.{0:04b}: ".format(lsb), l)

   def DumpRegHex(self):
      l = "   LSB \ MSB"
      for v in range(0,8):
         l += " - {0:04b}.xxxx -- ".format(v)

      print(l)

      for lsb in range(0,16):
         l = ""
         for msb in range(0,8):
            a = (msb << 4) + lsb
            b = self[a]
            fgc = clr.fg(self.rc[lsb][msb])
            fgr = clr.attr('reset')
            l += "{0}{1:>9}/{2:02x}={3:02x}{4} ".format(fgc, 
                                             self.ra[lsb][msb], a, b, 
                                             fgr)

         print("xxxx.{0:04b}: ".format(lsb), l)

   def SearchRegisterByName(self, regName):
      # get the lsb and msb of the register address
      for lsb in range(0,16):
         for msb in range(0,8):
            if self.ra[lsb][msb] == regName:
               addr = (msb << 4) + lsb
               return addr
      err = "Could not find register with name {0}".format(regName)
      raise BaseException(err)

   def GetRegisters(self):
      r = (
"RXF0SIDH RXF3SIDH RXM0SIDH TXB0CTRL TXB1CTRL TXB2CTRL RXB0CTRL RXB1CTRL",
"RXF0SIDL RXF3SIDL RXM0SIDL TXB0SIDH TXB1SIDH TXB2SIDH RXB0SIDH RXB1SIDH",
"RXF0EID8 RXF3EID8 RXM0EID8 TXB0SIDL TXB1SIDL TXB2SIDL RXB0SIDL RXB1SIDL",
"RXF0EID0 RXF3EID0 RXM0EID0 TXB0EID8 TXB1EID8 TXB2EID8 RXB0EID8 RXB1EID8",
"RXF1SIDH RXF4SIDH RXM1SIDH TXB0EID0 TXB1EID0 TXB2EID0 RXB0EID0 RXB1EID0",
"RXF1SIDL RXF4SIDL RXM1SIDL TXB0DLC TXB1DLC TXB2DLC RXB0DLC RXB1DLC",
"RXF1EID8 RXF4EID8 RXM1EID8 TXB0D0 TXB1D0 TXB2D0 RXB0D0 RXB1D0",
"RXF1EID0 RXF4EID0 RXM1EID0 TXB0D1 TXB1D1 TXB2D1 RXB0D1 RXB1D1",
"RXF2SIDH RXF5SIDH CNF3 TXB0D2 TXB1D2 TXB2D2 RXB0D2 RXB1D2",
"RXF2SIDL RXF5SIDL CNF2 TXB0D3 TXB1D3 TXB2D3 RXB0D3 RXB1D3",
"RXF2EID8 RXF5EID8 CNF1 TXB0D4 TXB1D4 TXB2D4 RXB0D4 RXB1D4",
"RXF2EID0 RXF5EID0 CANINTE TXB0D5 TXB1D5 TXB2D5 RXB0D5 RXB1D5",
"BFPCTRL TEC CANINTF TXB0D6 TXB1D6 TXB2D6 RXB0D6 RXB1D6",
"TXRTSCTRL REC EFLG TXB0D7 TXB1D7 TXB2D7 RXB0D7 RXB1D7",
"CANSTAT CANSTAT CANSTAT CANSTAT CANSTAT CANSTAT CANSTAT CANSTAT",
"CANCTRL CANCTRL CANCTRL CANCTRL CANCTRL CANCTRL CANCTRL CANCTRL")
      ra = []
      for l in r:
         rl = l.split(' ')
         ra += [rl]
      return ra

   def GetRegisterColors(self):
      filt = 'light_yellow'
      mask = 'yellow'
      txcfg = 'light_blue'
      rxcfg = 'green'
      txbuf = 'sky_blue_1'
      rxbuf = 'light_green'
      time = 'white'
      err = 'red'
      stat = 'light_magenta'
      ctrl = 'light_red'
      r =  ((filt, filt, mask, txcfg, txcfg, txcfg, rxcfg, rxcfg),
            (filt, filt, mask, txbuf, txbuf, txbuf, rxbuf, rxbuf),
            (filt, filt, mask, txbuf, txbuf, txbuf, rxbuf, rxbuf),
            (filt, filt, mask, txbuf, txbuf, txbuf, rxbuf, rxbuf),
            (filt, filt, mask, txbuf, txbuf, txbuf, rxbuf, rxbuf),
            (filt, filt, mask, txbuf, txbuf, txbuf, rxbuf, rxbuf),
            (filt, filt, mask, txbuf, txbuf, txbuf, rxbuf, rxbuf),
            (filt, filt, mask, txbuf, txbuf, txbuf, rxbuf, rxbuf),
            (filt, filt, time, txbuf, txbuf, txbuf, rxbuf, rxbuf),
            (filt, filt, time, txbuf, txbuf, txbuf, rxbuf, rxbuf),
            (filt, filt, time, txbuf, txbuf, txbuf, rxbuf, rxbuf),
            (filt, filt, stat, txbuf, txbuf, txbuf, rxbuf, rxbuf),
            (rxcfg, err, stat, txbuf, txbuf, txbuf, rxbuf, rxbuf),
            (txcfg, err, err,  txbuf, txbuf, txbuf, rxbuf, rxbuf),
            (ctrl, ctrl, ctrl, ctrl,  ctrl,  ctrl,  ctrl,  ctrl),
            (ctrl, ctrl, ctrl, ctrl,  ctrl,  ctrl,  ctrl,  ctrl))
      return r

   def SetCanMode(self, text, modeBits):
      print("Set MCP25625 in {0} mode ...".format(text))
      canctrl = self[0x0f]
      canctrl &= 0b00011111
      canctrl |= (modeBits << 5) & 0b11111111
      self[0x0f] = canctrl

   def ByteArgToValue(self, stringVal):
      if stringVal.startswith('0x') or stringVal.startswith('0X'):
         val = int(stringVal, 16)
      elif stringVal.startswith('0b'):
         val = int(stringVal, 2)
      else:
         val = int(stringVal)
      return val

if __name__ == "__main__":

   parser = argparse.ArgumentParser()
   parser.add_argument('-rb', '--regBinary', action='store_true', 
     help='display registers (binary format)')
   parser.add_argument('-rx', '--regHex', action='store_true', 
     help='display registers (hex format)')
   parser.add_argument('-mb', '--memBinary', action='store_true', 
     help='display memory (binary format)')
   parser.add_argument('-mx', '--memHex', action='store_true', 
     help='display memory (hex format)')
   parser.add_argument('-R', '--reset', action='store_true', 
     help='Perform a CAN reset')
   parser.add_argument('-SR', nargs=2, 
     metavar=('<regname>', '<val>'), 
     help='Set register with name <regname> to value <val>')
   parser.add_argument('-BMR', nargs=3, 
     metavar=('<regname>', '<val>', '<mask>'), 
     help='Bit modify register <regname> to value <val> with <mask>')
   parser.add_argument('-ML', '--loopbackMode', action='store_true', 
     help='Set CAN loopback mode')
   parser.add_argument('-MN', '--normalMode', action='store_true', 
     help='Set CAN normal mode')
   parser.add_argument('-MC', '--configMode', action='store_true', 
     help='Set CAN configuration mode')
   parser.add_argument('-MS', '--sleepMode', action='store_true', 
     help='Set CAN sleep mode')
   parser.add_argument('-MLS', '--listenMode', action='store_true', 
     help='Set CAN listen-only mode')
   args = parser.parse_args()

   m = rmap()

   if args.reset:
      print("Performing a CAN Reset ...")
      m.hal.Reset()

   if args.SR:
      m.DumpRegBin()
      regName = args.SR[0]
      val = m.ByteArgToValue(args.SR[1])
      addr = m.SearchRegisterByName(regName)
      print("Setting register {0} at address 0x{1:02x} to value {2} " \
         "(hex = 0x{2:02x}, bin = 0b{2:08b}) ..." \
         .format(regName, addr, val))
      m.hal.WriteByte(addr, val)

   if args.BMR:
      m.DumpRegBin()
      regName = args.BMR[0]
      val = m.ByteArgToValue(args.BMR[1])
      mask = m.ByteArgToValue(args.BMR[2])
      addr = m.SearchRegisterByName(regName)

      print("Bit modifying register {0} at address 0x{1:02x} "
         "to value {2} (hex = 0x{2:02x}, bin = 0b{2:08b}) " \
         "with mask {3} (hex = 0x{3:02x}, bin = 0b{3:08b}) ..." \
         .format(regName, addr, val, mask))
      m.hal.BitModify(addressByte=addr, maskByte=mask, dataByte=val)

   if args.normalMode:
      m.DumpRegBin()
      m.SetCanMode('normal', 0b000)

   if args.sleepMode:
      m.DumpRegBin()
      m.SetCanMode('sleep', 0b001)

   if args.loopbackMode:
      m.DumpRegBin()
      m.SetCanMode('loopback', 0b010)

   if args.listenMode:
      m.DumpRegBin()
      m.SetCanMode('listen-only', 0b011)

   if args.configMode:
      m.DumpRegBin()
      m.SetCanMode('config', 0b100)

   if args.regBinary:
      m.DumpRegBin()
   elif args.regHex:
      m.DumpRegHex()
   elif args.memBinary:
      m.DumpMemBin()
   elif args.memHex:
      m.DumpMemHex()
   else: 
      m.DumpRegBin()