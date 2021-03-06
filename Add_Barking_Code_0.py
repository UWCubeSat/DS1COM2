import numpy as np
from gnuradio import gr


class blk(gr.basic_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.basic_block.__init__(self, name="padToEncode",
            in_sig=[np.uint8],
            out_sig=[np.uint8])
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).

	self.ENCODE_OUTPUT = 130
	self.REMAINDER = self.ENCODE_OUTPUT%8


    def general_work(self, input_items, output_items):
        """example: multiply with constant"""
	#TAKES in unpacked bytes and adds barker codes
	packets = len(input_items)/self.ENCODE_OUTPUT
	for j in range(packets):
		if len(input_items[0]) > (self.ENCODE_OUTPUT - self.REMAINDER)*j and len(output_items[0]) > self.ENCODE_OUTPUT*j:
			for i in range(self.ENCODE_OUTPUT- self.REMAINDER):
				output_items[j*self.ENCODE_OUTPUT][i] = input_items[j*self.ENCODE_OUTPUT][i]
			for i in range(self.ENCODE_OUTPUT-self.REMAINDER, self.ENCODE_OUTPUT):
				output_items[j*self.ENCODE_OUTPUT][i] = 0
			self.consume_each(self.ENCODE_OUTPUT-self.REMAINDER);
	return self.ENCODE_OUTPUT * packets 
	return 0


