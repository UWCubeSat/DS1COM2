#!/usr/bin/env python

from gnuradio import gr
from gnuradio import blocks
from gnuradio import digital
import string_to_list
from frame_sync import frame_sync


class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self)

        ##################################################
        # Variables
        ##################################################       

        #Create Input Vector here
        input_vector = 0  # <-- Change this: *Hint: Use string_to_list.conv_string_to_1_0_list(s)

        ##################################################
        # Blocks
        ##################################################
        
        self.input_vector_source = blocks.vector_source_b(input_vector, True, 1, [])          

        self.input_unpacked_to_packed = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)

        self.mod = digital.dbpsk_mod(
            samples_per_symbol=2,
            excess_bw=0.35,
            mod_code="gray",
            verbose=False,
            log=False)
            
        self.demod = digital.dbpsk_demod(
            samples_per_symbol=2,
            excess_bw=0.35,
            freq_bw=6.28/100.0,
            phase_bw=6.28/100.0,
            timing_bw=6.28/100.0,
            mod_code="gray",
            verbose=False,
            log=False
        )        
        
        self.output_unpacked_to_packed = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)

        self.frame_sync = frame_sync() # Your custom block!!!

        self.output_file_sink = blocks.file_sink(gr.sizeof_char*1, "output.txt", False)
        self.output_file_sink.set_unbuffered(True)
        
        ##################################################
        # Connections
        ##################################################
        self.connect(self.input_vector_source, self.input_unpacked_to_packed, self.mod, self.demod, self.output_unpacked_to_packed, self.frame_sync, self.output_file_sink)



if __name__ == '__main__':
    tb = top_block()
    tb.start()
    tb.wait()
    # tb.run()
    tb.stop()

