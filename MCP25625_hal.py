# Copyright (C) 2018 Quick2Space.org under the MIT License (MIT)
# See the LICENSE.txt file in the project root for more information.

import spidev as spidev


# Hardware abstraction layer - Low-level access to MCP25625
class MCP25625_hal:

   def __init__(self, verbosePrint = False):
      self.s=spidev.SpiDev()
      self.s.open(0,0)
      self.s.max_speed_hz=10000
      self.verbosePrint = verbosePrint

   def close(self):
      self.s.close()

   # Reset the HW before beginning to inteact with it
   def __enter__(self):
      self.Reset()
      return self

   def __exit__(self, type, value, traceback):
      self.close()
      return 
      
   #
   # Low-level SPI commands implemented by MCP25625
   #

   def Reset(self):
      self.s.xfer([int('11000000',2)])

   # Read a number of bytes starting from given address and length
   def ReadBytes(self, addressBytes, len):
      # dummyData = [0]*len
      # command = [0b00000011, addressBytes] + dummyData
      dummyData = b'\x00'*len
      command = list(0b00000011.to_bytes(1, 'big') 
                     + addressBytes.to_bytes(1, 'big') + dummyData)
      # print(command)
      response = self.s.xfer(command)
      # print(response)
      # TODO test that first two bytes are zero
      # eliminate the first two bytes
      # TODO assert that readData is proper length
      readData = response[2:]
      # print(readData)
      return readData

   def WriteBytes(self, addressBytes, arrayDataBytes):
      if self.verbosePrint:
          print("## Writing {0} at address 0x{1:02x}".format(arrayDataBytes, 
                                                       addressBytes))
      command = list(0b00000010.to_bytes(1, 'big') 
                     + addressBytes.to_bytes(1, 'big') + arrayDataBytes)

      if self.verbosePrint:
          print("## SPI write command: {0} ({1})".format( 
             [hex(i) for i in command],
             [bin(i) for i in command]))

      self.s.xfer(command)

      rr = self.ReadBytes(addressBytes, len(arrayDataBytes))
      
      if self.verbosePrint:
          print("## SPI read content: {0} ({1})".format( 
             [hex(i) for i in rr], 
             [bin(i) for i in rr]        
             ))
          

   # TODO optimize this for writing a single byte
   def WriteByte(self, addressByte, byteValue):
      self.WriteBytes(addressByte, byteValue.to_bytes(1, 'big'))

   # TODO optimize this to use the other read command
   def ReadByte(self, addressByte):
      return self.ReadBytes(addressByte, 1)[0]

   # TODO optimize this
   def BitModify(self, addressByte, maskByte, dataByte):
      rr = self.ReadByte(addressByte)

      if self.verbosePrint:
        print("## (SPI read content = 0x{0:02x} (0x{0:08b}))".format(rr))
        print("## Bit modifying address 0x{0:02x} "
            "to value {1} (hex = 0x{1:02x}, bin = 0b{1:08b}) " \
            "with mask {2} (hex = 0x{2:02x}, bin = 0b{2:08b}) ..." \
            .format(addressByte, dataByte, maskByte))

      command = list(0b00000101.to_bytes(1, 'big') 
                     + addressByte.to_bytes(1, 'big')
                     + maskByte.to_bytes(1, 'big')
                     + dataByte.to_bytes(1, 'big'))

      if self.verbosePrint:
          print("## SPI bit modify command: {0} ({1})".format( 
             [hex(i) for i in command],
             [bin(i) for i in command]))
      
      self.s.xfer(command)

      rr = self.ReadByte(addressByte)
      
      if self.verbosePrint:
        print("## (SPI read content = 0x{0:02x} (0x{0:08b}))".format(rr))

   #
   #  Utilities
   #

   # Convert a string from bin format 'bbbb bbbb, bbbb bbbb, ...'
   # to [bbbb bbbb, bbbb bbbb, ...]
   def StrToBin(self, val):
      arrS = val.split(',')
      arrB = []
      for sb in arrS:
         sb_nospace = sb.replace(' ','')
         b = int(sb_nospace, 2)
         arrB = arrB + [b]
      return arrB

   # transfer bytes.
   # Accepts a string from bin format 'bbbb bbbb, bbbb bbbb, ...'
   def xfer(self, val):
      if isinstance(val, str):
         arrB = self.StrToBin(val)
      else:
         arrB = val
      return self.s.xfer(arrB)
