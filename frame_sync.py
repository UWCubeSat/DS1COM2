#!/usr/bin/env python
from gnuradio import gr
from gnuradio import blocks
from gnuradio import digital
import numpy

class frame_sync(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self, name="frame_sync",
            in_sig=[numpy.uint8],
            out_sig=[numpy.uint8])

        ##################################################
        # Put Variables Here
        ################################################## 


    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]


        ninput_items = len(in0)
        nitems_read = 0     # How many items you have read - does NOT have to be same as ninput_items
        nitems_written = 0  # How many items you have written - *Hint: probably want to count this as you go along

        n = 0        
        while(n < nitems_read): #Loop over the input items that you want to read

            ##################################################
            # Loop through input items, and search
            # for start of frame
            # (i.e. do correlation with barker sequence)
            #
            # What are your outputs?  What happens when you
            # find the Barker sequence? How long is your data?
            # How do you not walk off the end of the input array?
            ##################################################
            n += 1 #Update n

        self.consume_each(nitems_read)
        return nitems_written

        


