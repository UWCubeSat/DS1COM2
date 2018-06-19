import numpy as np
from gnuradio import gr


class blk(gr.basic_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.basic_block.__init__(self, name="Add Barking Code",
            in_sig=[np.uint8],
            out_sig=[np.uint8])
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).

	self.barkersequence = [0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0]
	self.PACKET_SIZE = 64

    def general_work(self, input_items, output_items):
        """example: multiply with constant"""
	#TAKES in unpacked bytes and adds barker codes
	if len(input_items[0]) > self.PACKET_SIZE:
        	output_items[0]
		for i in range(len(self.barkersequence)):
			output_items[0][i] = self.barkersequence[i]
		for i in range(self.PACKET_SIZE):
			output_items[0][16+i] = input_items[0][i]
		self.consume_each(self.PACKET_SIZE);
        	return self.PACKET_SIZE + 16
	return 0

