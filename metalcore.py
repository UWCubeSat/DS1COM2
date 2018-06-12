# -*- coding: utf-8 -*-
# Copyright © 2018 Quick2Space.org under the MIT License (MIT)
# See the LICENSE.txt file in the project root for more information.

# TODO:
# - [register]
#    - define context at register group level (and instantiate with 
#      a HAL/device)
#       - this will allow support for multiple devices
#       - will also allow simpler usage - tx spans across registers
#    - multi-byte registers
# - [HAL]
#     - separate lower-level device functions from higher level ones 
#     - differentiate between HAL and device (conceptually)


from enum import Enum
import inspect


#
#  Constant state (register/field definitions)
#

class MetalCoreException(Exception):
   def __init__(self, val):
      self.parameter = val
   def __str__(self):
      return repr(self.parameter)
   @staticmethod
   def ThrowIf(condition, message):
      if (condition):
         raise MetalCoreException(message)

class ArgumentException(Exception):
   def __init__(self, val):
      self.parameter = val
   def __str__(self):
      return repr(self.parameter)
   @staticmethod
   def ThrowIf(condition, message):
      if (condition):
         raise ValueError(message)

class Access(Enum):
   U = 0    # Unimplemented 
   RW = 1   # Read-write
   R = 2    # Read-only
   W = 3    # Write-only

class Field(object):

   def RightPaddingBits(bitOffsetMSB, bitsLength):
      return (1 + bitOffsetMSB - bitsLength)

   # Returns a byte-wide mask 
   def Mask(bitOffsetMSB, bitsLength):
      return ((1 << bitsLength) - 1)

   # Initializes the bit field
   # Bit offset starts from left (7 with MSB) toward right (0 with LSB)
   # as in 7.......0
   # 
   # Bit offset and length are not limited in size
   def __init__(
         self, 
         bitOffsetMSB, 
         bitsLength, 
         access = Access.RW, 
         initialValue = 0
         ):
      ArgumentException.ThrowIf(bitOffsetMSB < 0, 
         "MSB offset cannot be negative")
      ArgumentException.ThrowIf(bitsLength <= 0, 
         "bits length cannot be negative or zero")
      ArgumentException.ThrowIf(1 + bitOffsetMSB - bitsLength < 0, 
         "bit mask needs to fit")

      self.bitOffsetMSB = bitOffsetMSB
      self.bitsLength = bitsLength
      self.access = access
      self.initialValue = initialValue
      self.valueMask = Field.Mask(bitOffsetMSB, bitsLength)
      self.rightPaddingBits = Field.RightPaddingBits(bitOffsetMSB, 
                                                     bitsLength
                                                     )
      self.registerMask = self.valueMask << self.rightPaddingBits

   def IsReadable(self):
      return (self.access == Access.RW) or (self.access == Access.R)

   def IsWriteable(self):
      return (self.access == Access.RW) or (self.access == Access.W)

#
#  Modifiable state
#

# internal class to implement a field state
class FieldInstance(object):
   def __init__(self, tx, fieldName, field):
      self.field = field
      self.fieldName = fieldName
      self.tx = tx
      self.val = 0
      self.modified = False

   # Internal method. Called to initialize the instance from a register
   def LoadFromRegister(self):
      self.val = (self.tx.val & self.field.registerMask) >> \
                  self.field.rightPaddingBits
      assert (self.val & ~ self.field.valueMask) == 0

   # Internal method. Called to save the current value into a register
   def SaveToRegister(self):
      assert (self.val & ~ self.field.valueMask) == 0
      if (self.modified):
         modifiedTxVal = self.tx.val
         modifiedTxVal &= ~ self.field.registerMask
         shiftedVal = self.val << self.field.rightPaddingBits
         assert  (shiftedVal & ~self.field.registerMask) == 0
         modifiedTxVal |= shiftedVal
         # print("Applying {0}: Tx:{1:08b} -> Tx:{2:08b}".format( 
         #     self.fieldName, self.tx.val, modifiedTxVal))
         self.tx.val = modifiedTxVal

   # Internal method. Getter that returns the current value 
   # in the asscociated property.
   def Read(self, tx):
      # print("Read reached: ", tx, tx.register, ", ", self.fieldName, 
      #        "val == ", self.val)
      assert (self.val & ~ self.field.valueMask) == 0
      return self.val

   # Internal method. Getter that returns the current value 
   # in the asscociated property.
   def Read_bytes(self, tx):
      # print("Read reached: ", tx, tx.register, ", ", self.fieldName, 
      #        "val == ", self.val)
      assert (self.val & ~ self.field.valueMask) == 0
      bytesLen = ((self.field.bitsLength + 7) & 0xfffa) >> 3
      print(bytesLen)
      bytesData = self.val.to_bytes(bytesLen, byteorder='big')
      return bytesData

   # Internal method. Setter that sets the current value to something 
   # supplied by the property
   def Write(self, tx, val):
      assert (self.field.access == Access.RW) \
             or (self.field.access == Access.W)
      # print("Write reached: ", tx, tx.register, ", ", self.fieldName, 
      #        "=", val)

      # This error is thrown when attempting to set a larger value that 
      # a bitfield can hold 

      # print("Applying {0}: Tx:{1:b} # Tx:{2:b}".format(self.fieldName, 
      #        val, self.field.valueMask))
      ArgumentException.ThrowIf((val & ~ self.field.valueMask) != 0, 
         "Value needs to fit into the field")
      if (self.val != val):
         # print("Modifying {0}: {1} -> {2}".format(self.fieldName,    \
         #      self.val, val)                                        
         self.val = val
         self.modified = True
         self.tx.modified = True


# internal class to represent registry state
class RegisterTransaction(object):
   def __init__(self, register):
      self.val = 0
      self.register = register
      self.fields = []
      self.hal = register.hal
      self.modified = False
      # print("Register type = ", type(self.register))
      for n,v in inspect.getmembers(type(self.register)):
         if isinstance(v, Field):
            # print("Adding field ", n, v)
            fieldTx = FieldInstance(self, n, v)

            # Check for non-overlaping bitmasks with other fields in 
            # the same register
            # If there is an error thrown here then some fields have 
            # overlapping bit-field declarations within the register
            for otherField in self.fields:
               overlap = (otherField.field.registerMask \
                           & fieldTx.field.registerMask)
               ArgumentException.ThrowIf(
                  overlap,
                  "Fields {0}.{1} with mask {2:08b} and {0}.{3} " + 
                  "with mask {4:08b} have overlapping masks"
                  .format( 
                     str(type(self.register)), otherField.fieldName, 
                     otherField.field.registerMask, fieldTx.fieldName, 
                     fieldTx.field.registerMask)
                  )

            # set "int" field property
            readRoutine = None
            writeRoutine = None
            if (fieldTx.field.IsReadable()):
               readRoutine = fieldTx.Read
            if (fieldTx.field.IsWriteable()):
               writeRoutine = fieldTx.Write
            setattr(type(self), n, property(readRoutine, writeRoutine))

            # set "bytes" field property
            readRoutine_bytes = None
            writeRoutine_bytes = None
            if (fieldTx.field.IsReadable()):
               readRoutine_bytes = fieldTx.Read_bytes
            # TODO - add implementation for write bytes? 
            setattr(type(self), n + "_bytes", 
               property(readRoutine_bytes, writeRoutine_bytes))

            self.fields += [fieldTx]
      self.InitializeHw()
      for field in self.fields:
         field.LoadFromRegister()

   # Fills each writable field with zero
   def Zero(self):
      for field in self.fields:
         if field.field.IsWriteable():
            field.Write(self, 0)
      
   def InitializeHw(self):
      MetalCoreException.ThrowIf(self.register.address == None,
         "need to define address field in registry declaration for %s" 
         % type(self.register))
      # Read the register contents at the given address
      # readBytes = self.hal.ReadBytes(self.register.address, 
      #                                self.register.lengthBytes
      #                                )
      readBytes = self.register.readValue()

      # print(readBytes)
      self.val = int.from_bytes(readBytes, 'big')
      # print("## Read value 0b{0:b} (0x{0:x}) at address 0x{1:x}"
      #        .format(self.val, self.register.address))
      
   def Close(self):
      if (self.modified):
         # print("start Close()")
         oldVal = self.val
         for field in self.fields:
            field.SaveToRegister()
         # print("## Writing value 0b{0:b} (0x{0:x}) -> " 
         #      + "0b{1:b} (0x{1:x}) at address 0x{2:x}"
         #      .format(oldVal, self.val, self.register.address))
         # print("#Value info: ", type(self.val), "{0:x}".format(self.val), 
         #      type(self.register.lengthBytes), self.register.lengthBytes)
         newBytes = self.val.to_bytes(self.register.lengthBytes, 'big')
         self.hal.WriteBytes(self.register.address, newBytes)
         # print("end Close()")

   def Print(self):
      print("- Printing {0} = 0b{1:b} (0x{1:x})".format(
         self.register.instanceNameInGroup,
         self.val))
      strList = []
      for fieldInstance in self.fields:
         if fieldInstance.field.IsReadable():
            fieldVal = fieldInstance.Read(self)
            if (self.register.lengthBytes == 1):
               offsetMsbFformatStr = "{0}"
            else:
               offsetMsbFformatStr = "{0:02}"
            offsetMSB = offsetMsbFformatStr.format(
                           fieldInstance.field.bitOffsetMSB)
            formatStr = "  - [msb:%s] %s.%s = {0:0%db} (0x{0:x})" % (
                           offsetMSB,
                           self.register.instanceNameInGroup,
                           fieldInstance.fieldName,
                           fieldInstance.field.bitsLength)
            strList += [formatStr.format(fieldVal)]
      strList.sort(reverse=True)
      for s in strList:
         print(s)



# Base class representing a single register type
# Needs to be derived by indicating static fields as inner fields 
# Implements an auto transaction class that can be used with "with" 
# statements
# Allows multiple instances to be bound to different addresses
class Register(object):

   def __init__(self):
      self.tx = None
      self.address = None
      self.lengthBytes = 1
      self.hal = None
      self.instanceNameInGroup = None

   def BindToAddress(self, byteAddress, byteLength = 1):
      self.address = byteAddress
      self.lengthBytes = byteLength
      return self

   def BindToHal(self, hal, instanceNameInGroup):
      self.hal = hal
      self.instanceNameInGroup = instanceNameInGroup

   # Instantiate a transaction that can be used to manipulate the 
   # contents of the register
   def __enter__(self):
      self.tx = RegisterTransaction(self)
      return self.tx

   def __exit__(self, type, value, traceback):
      self.tx.Close()
      self.tx = None

   # utility to read the value
   # TODO add utility to also write the value
   def readValue(self):
      return self.hal.ReadBytes(self.address, self.lengthBytes)

   def toString(self):
      val = self.readValue()
      return self.instanceNameInGroup + ": " + \
               ",".join("{0:08b}".format(b) for b in val)

   def Print(self):
      with self as tx:
         tx.Print()

   def Zero(self):
      with self as tx:
         tx.Zero()




# Base class representing a well defined group of registers associated 
# with a certain hardware device
# Needs to be derived by a specialized implementation containing static 
# Register() instances
# Needs to be bound to a HAL using the BindToHal() method
# Note - an instance of a group of registers can be bound to a given 
# HAL device
# - TODO - allow multiple RegisterGroup instantiation to be bound to 
# different HAL devices
class RegisterGroup(object):

   def __init__(self):
      self.hal = None

   def BindToHal(self, hal):
      self.hal = hal
      for n,v in type(self).__dict__.items():
         if isinstance(v, Register):
            # print("Binding HAL to Register", self.hal, n, v)
            v.BindToHal(hal, n)
