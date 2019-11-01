import threading
import logging

class PulseSender (threading.Thread):
	def __init__(self, tools):
		threading.Thread.__init__(self)
		self.tools = tools

	def run(self):
		while True:
			rgPulseInfo = self.tools.pulseQueue.get(True)
			pulseStrength = rgPulseInfo[0]
			freq = rgPulseInfo[1]
			temp = rgPulseInfo[2]
			sendIndex = rgPulseInfo[3]
			logging.debug("Sending pulse %f sendIndex %d freq %d temp %f", pulseStrength, sendIndex, freq, temp)
			self.tools.mavlinkThread.sendPulseStrength(pulseStrength, sendIndex, freq)