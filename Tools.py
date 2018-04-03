from multiprocessing import Queue
import inspect
import os

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
        self.logDir = None
        self.workDir = None
        self.pyDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
