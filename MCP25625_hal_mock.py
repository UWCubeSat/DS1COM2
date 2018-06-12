# Copyright (C) 2018 Quick2Space.org under the MIT License (MIT)
# See the LICENSE.txt file in the project root for more information.

import spidev as spidev


# Hardware abstraction (mock) layer - Low-level access to MCP25625
class MCP25625_hal_mock:
    def __init__(self):
        self.testData = {}

    # Reset the HW before beginning to inteact with it
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass
      
    #
    # mock commands implemented by MCP25625
    #

    def Reset(self):
        print("Reset")

    # Read a number of bytes starting from given address and length
    def ReadBytes(self, addressBytes, len):
        print("ReadBytes({0},{1},{2}".format(self, addressBytes, len))
        return self.testData[addressBytes]

    def WriteBytes(self, addressBytes, listBytes):
        print("WriteBytes({0},{1},{2}".format(
            self, addressBytes, listBytes))
        self.testData[addressBytes] = listBytes

    # TODO optimize this for writing a single byte
    def WriteByte(self, addressByte, byteValue):
        self.WriteBytes(addressByte, [byteValue])

    # TODO optimize this to use the other read command
    def ReadByte(self, addressByte):
        return self.ReadBytes(addressByte, 1)[0]
