#!/usr/bin/env python

from gnuradio import gr
from gnuradio import blocks
from gnuradio import digital
import string_to_list
import numpy
from gnuradio import uhd
from frame_sync import frame_sync


class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self)

        ##################################################
        # Variables
        ##################################################       

        #Create Input Vector here
        barker13 = [0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0]
        msg = string_to_list.conv_string_to_1_0_list("Hello World\n")
        pad = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        pad = pad + pad + pad + pad + pad
        input_vector = barker13+msg+pad  # <-- Change this: *Hint: Use string_to_list.conv_string_to_1_0_list(s)

        #print(input_vector)
        ##################################################
        # Blocks
        ##################################################
	
	#USRP        
	#Variables
        self.samp_rate = samp_rate = 390625.0
        self.sink_args = args = "type=b200"
        #self.address = address = "addr=192.168.10.2" # real men hard-code parameters!
        self.freq = freq= 1425000000
        self.freq_offset = freq_offset= 0
        self.gain = gain= 13
        print "Sample Rate:", samp_rate
        print "Freq:", freq

	#Init
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
        	",".join((args, "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0.set_center_freq(freq, 0)
        self.uhd_usrp_sink_0.set_gain(gain+70.5, 0)

        ##################################################

        self.input_vector_source = blocks.vector_source_b(input_vector, True, 1, [])          

        self.input_unpacked_to_packed = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)

        self.mod = digital.dbpsk_mod(
            samples_per_symbol=2,
            excess_bw=0.35,
            mod_code="gray",
            verbose=False,
            log=False)
           
        
        ##################################################
        # Connections
        ##################################################
        self.connect(self.input_vector_source, self.input_unpacked_to_packed, self.mod, self.uhd_usrp_sink_0)



if __name__ == '__main__':
    tb = top_block()
    tb.start()
    tb.wait()
    tb.run()
    tb.stop()

