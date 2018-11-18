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
	self.DATALENGTH = self.ENCODE_OUTPUT-self.REMAINDER
	self.bitscopied=0

    def general_work(self, input_items, output_items):
	packets = min(int(len(input_items[0])/(self.DATALENGTH)),int(len(output_items[0])/(self.ENCODE_OUTPUT)))
	if packets > 0:
		for p in range(packets):
			for index in range(self.DATALENGTH):
				output_items[0][p*self.ENCODE_OUTPUT + index] = input_items[0][p*self.DATALENGTH +index]
		self.consume_each(packets*self.DATALENGTH)
		return(packets*self.ENCODE_OUTPUT)			
		
	return 0


