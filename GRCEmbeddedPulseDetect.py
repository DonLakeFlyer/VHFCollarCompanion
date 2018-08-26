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

	self.sample_rate = sample_rate
	self.backgroundNoise = 1000
	self.snrThreshold = 1.5
	self.sampleCount = 0
	self.lastPulseSeconds = 0
	self.pulseMax = 0
	self.pulseSampleCount = 0
	self.pulseTriggerValue = 0
	self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	self.udpAddress = ('localhost', 10000)
	#self.sock.bind(self.udpAddress)

	self.csvFile = open("pulse.csv", "w")

	if sample_rate == 0:
		print("ERROR: Sample rate = 0")

    def adjustBackgroundNoise(self, strength):
        self.backgroundNoise = (self.backgroundNoise * 0.99) + (strength * 0.01)

    def work(self, input_items, output_items):
	for pulseValue in input_items[0]:
		if math.isnan(pulseValue):
			continue

		csvFile.write(str(pulseValue))
		csvFile.write(",")
		csvFile.write(str(self.backgroundNoise))
		csvFile.write("\n")

		self.sampleCount = self.sampleCount + 1
		lastSampleSeconds = self.sampleCount / self.sample_rate

		pulseTriggered = False
		if self.pulseSampleCount != 0:
			if pulseValue >= self.pulseTriggerValue:
				pulseTriggered = True
		else: 
			if pulseValue > self.backgroundNoise * self.snrThreshold:
				self.pulseTriggerValue = pulseValue
				pulseTriggered = True

		if pulseTriggered:
			self.pulseSampleCount = self.pulseSampleCount + 1
			if pulseValue > self.pulseMax:
				self.pulseMax = pulseValue
		elif self.pulseSampleCount != 0:
			self.lastPulseSeconds = lastSampleSeconds
			self.sock.sendto(struct.pack('<ff', lastSampleSeconds, self.pulseMax), self.udpAddress)
			print("True pulse detected pulseMax:secs:length:backgroundNoise")
			print(self.pulseMax, self.lastPulseSeconds, self.pulseSampleCount / self.sample_rate * 1000, self.backgroundNoise)
			self.pulseSampleCount = 0
			self.pulseMax = 0
			self.skipTrailingEdge = self.sample_rate / (1000 / 15)
		else:
			self.adjustBackgroundNoise(pulseValue)

		if lastSampleSeconds > self.lastPulseSeconds + 2.1:
			self.lastPulseSeconds = lastSampleSeconds
			self.sock.sendto(struct.pack('<ff', lastSampleSeconds, 0), self.udpAddress)
			print("No pulse for 2.1 seconds backgroundNoise", self.backgroundNoise)

        output_items[0][:] = input_items[0]
        return len(output_items[0])
