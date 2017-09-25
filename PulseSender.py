import threading
import logging

class PulseSender (threading.Thread):

	def __init__(self, tools):
		threading.Thread.__init__(self)
		self.tools = tools

	def run(self):
		while True:
			pulseStrength = self.tools.pulseQueue.get(True)
			logging.debug("PulseSender.pulse %d", pulseStrength)
			self.tools.mavlinkThread.sendPulseStrength(pulseStrength)
