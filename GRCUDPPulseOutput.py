"""
Embedded Python Blocks:

Each this file is saved, GRC will instantiate the first class it finds to get
ports and parameters of your block. The arguments to __init__  will be the
parameters. All of them are required to have default values!
"""
import socket
import struct
import math
import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self, sample_rate=0):  # only default arguments here
        gr.sync_block.__init__(
            self,
            name='Embedded Python Block',
            in_sig=[np.float32],
            out_sig=[np.float32]
        )
	self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	self.udpAddress = ('localhost', 10000)
	#self.sock.bind(self.udpAddress)

    def work(self, input_items, output_items):
	print "Here"
	for pulseValue in input_items[0]:
		if math.isnan(pulseValue):
			continue
		if pulseValue > 0:
			self.sock.sendto(struct.pack('<f', pulseValue), self.udpAddress)

        output_items[0][:] = input_items[0]
        return len(output_items[0])
