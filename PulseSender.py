class PulseSender (threading.Thread):

	def __init__(self, tools):
		threading.Thread.__init__(self)
		self.tools = tools

	def run(self):
		while True:
			pulseStrength = self.tools.pulseQueue.get(True)
			print("PulseSender.pulse", pulseStrength)
			self.tools.mavlinkThread.sendPulseStrength(pulseStrength)
