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
			logging.debug("Sending pulse %d freq %d", pulseStrength, freq)
			self.tools.mavlinkThread.sendPulseStrength(pulseStrength, freq)