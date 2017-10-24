import threading
import logging

class PulseSender (threading.Thread):

	def __init__(self, tools):
		threading.Thread.__init__(self)
		self.tools = tools
		self.pulseCallback = None

	def run(self):
		while True:
			pulseStrength = self.tools.pulseQueue.get(True)
			logging.debug("pulse %d", pulseStrength)
			self.tools.mavlinkThread.sendPulseStrength(pulseStrength)
			if self.pulseCallback:
				callback = self.pulseCallback
				self.pulseCallback = None
				callback(pulseStrength)
