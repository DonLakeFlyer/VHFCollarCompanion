"""
Embedded Python Blocks:

Each this file is saved, GRC will instantiate the first class it finds to get
ports and parameters of your block. The arguments to __init__  will be the
parameters. All of them are required to have default values!
"""
import socket
import struct
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
	self.noiseWindowLength = sample_rate * 2
	self.noiseWindow = int(self.noiseWindowLength) * [ None ]
	self.noiseWindowIndex = 0
	self.noiseWindowFull = False
	self.noiseWindowSum = 0
	self.sampleCount = 0
	self.lastPulseSeconds = 0
	self.pulseMax = 0
	self.pulseSampleCount = 0
	self.pulseTriggerValue = 0
	self.skipTrailingEdge = 0
	self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	self.udpAddress = ('localhost', 10000)
	#self.sock.bind(self.udpAddress)

    def work(self, input_items, output_items):
	for pulseValue in input_items[0]:
		self.sampleCount = self.sampleCount + 1
		lastSampleSeconds = self.sampleCount / self.sample_rate

		previousValue = self.noiseWindow[self.noiseWindowIndex]
		self.noiseWindowSum = self.noiseWindowSum + pulseValue
		self.noiseWindow[self.noiseWindowIndex] = pulseValue
		self.noiseWindowIndex = self.noiseWindowIndex + 1
		if self.noiseWindowFull:
			self.noiseWindowSum = self.noiseWindowSum - previousValue
		if self.noiseWindowIndex >= self.noiseWindowLength:
			self.noiseWindowIndex = 0
			self.noiseWindowFull = True

		if self.skipTrailingEdge > 0:
			self.skipTrailingEdge = self.skipTrailingEdge - 1
			continue

		if self.noiseWindowFull:
			# Background noise is the average of the current noise sample window
			backgroundNoise = self.noiseWindowSum / self.noiseWindowLength
			#print(backgroundNoise, pulseValue)
			#self.loopIndex = loopIndex + 1
			#continue

			pulseTriggered = False
			if self.pulseSampleCount != 0:
				if pulseValue >= self.pulseTriggerValue:
					pulseTriggered = True
			else: 
				if pulseValue > backgroundNoise * 5:
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
				print(self.pulseMax, self.lastPulseSeconds, self.pulseSampleCount / self.sample_rate * 1000, backgroundNoise)
				self.pulseSampleCount = 0
				self.pulseMax = 0
				self.skipTrailingEdge = self.sample_rate / (1000 / 15)

		if lastSampleSeconds > self.lastPulseSeconds + 2.1:
			self.lastPulseSeconds = lastSampleSeconds
			self.sock.sendto(struct.pack('<ff', lastSampleSeconds, 0), self.udpAddress)
			print("No pulse for 2.1 seconds")

        output_items[0][:] = input_items[0]
        return len(output_items[0])
