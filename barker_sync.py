#!/usr/bin/env python
from gnuradio import gr
from gnuradio import blocks
from gnuradio import digital
import numpy as np

np.set_printoptions(threshold=np.nan)

_tracep = False
def tprint(msg):
    if _tracep:
        print msg


class barker_sync(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self, name="barker_sync",
            in_sig=[np.uint8],
            out_sig=[np.uint8])

        ##################################################
        # Put Variables Here
        ##################################################
        self.syncSize = 16
        self.packetSize = 64
        self.tolerance = 0
        self.syncAndPacketSize = self.syncSize + self.packetSize
        self.barkersequence = np.array([-1, -1, -1, -1, -1, 1, 1, -1, -1, 1, -1, 1, -1, -1, -1, -1])

    def general_work(self, input_items, output_items):

        # Initial housekeeping
        in0 = input_items[0]
        out = output_items[0]

        print("Input/Output Items:  {}/{}".format(len(in0), len(out)))

        # First, make sure the buffer has enough bits to be able to process
        if len(in0) < self.syncAndPacketSize:
            self.consume_each(int(0))
            return 0
        # scan for sync pattern
        correlationOutput = np.correlate(in0.astype(np.int32) * 2 - 1, self.barkersequence)
        maxCorrIndex = np.argmax(correlationOutput)
        maxCorrValue = correlationOutput[maxCorrIndex]

        # if a lousy match, reset the buffers to try again
        if maxCorrValue < (self.syncSize - self.tolerance):
            tprint("Barker correlation insufficient, resetting buffer.")
            self.consume_each(int(len(in0)))
            return 0

        # Good match - do we have room?
        # TODO:  maybe have another interim state that allows us to avoid scanning for the Barker again
        if len(in0) < (maxCorrIndex + self.syncAndPacketSize):
            tprint("Barker found, but need more data - filling buffer.")
            self.consume_each(int(maxCorrIndex - 1))
            return 0
        index =0
        for i in in0[maxCorrIndex + self.syncSize : maxCorrIndex + self.syncAndPacketSize]:
            out[index] = i
            index +=1
        self.consume_each(int(maxCorrIndex + self.syncAndPacketSize))
        return (self.packetSize)
       
