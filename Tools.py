from multiprocessing import Queue

class Tools:
    def __init__(self):
        self.mavlinkThread = None
        self.vehicle = None
        self.directionFinder = None
        self.pulseQueue = Queue()