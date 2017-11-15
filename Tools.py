from multiprocessing import Queue

class Tools:
	def __init__(self):
		self.mavlinkThread = None
		self.vehicle = None
		self.directionFinder = None
		self.pulseSender= None
		self.pulseQueue = Queue()
		self.leftFregQueue = Queue()
		self.rightFreqQueue = Queue()
		self.leftGainQueue = Queue()
		self.rightGainQueue = Queue()
		self.leftAmpQueue = Queue()
		self.rightAmpQueue = Queue()
