from multiprocessing import Queue

class Tools:
    def __init__(self):
        self.mavlinkThread = None
        self.vehicle = None
        self.directionFinder = None
        self.pulseSender= None
        self.pulseQueue = Queue()
        self.setFreqQueue = Queue()
        self.setGainQueue = Queue()
        self.setAmpQueue = Queue()