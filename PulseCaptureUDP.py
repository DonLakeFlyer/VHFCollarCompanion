import logging
import socket
import struct

from multiprocessing import Process
from queue import Queue

class PulseCaptureUDP(Process):
    def __init__(self, tools):
        Process.__init__(self)
        self.pulseQueue = tools.pulseQueue
        self.setFreqQueue = tools.setFreqQueue
        self.setGainQueue = tools.setGainQueue
        self.setAmpQueue = tools.setAmpQueue
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind(('localhost', 10000))

    def processFreqQueue(self):
        try:
            self.freq = self.setFreqQueue.get_nowait()
        except Exception as e:
            pass
        else:
            logging.debug("Changing frequency %f", self.freq)

    def processGainQueue(self):
        try:
            self.gain = self.setGainQueue.get_nowait()
        except Exception as e:
            pass
        else:
            logging.debug("Changing gain %d", self.gain)

    def processAmpQueue(self):
        try:
            self.amp = self.setAmpQueue.get_nowait()
        except Exception as e:
            pass
        else:
            logging.debug("Changing amp %s", self.amp)

    def run(self):
        logging.debug("PulseCapture.run")

        while True:
            self.processFreqQueue()
            self.processGainQueue()
            self.processAmpQueue()

            # GRC script pushes two floats:
            #   Time in seconds
            #   Pulse value
            data, address = self.udpSocket.recvfrom(4 * 2)

            floats = struct.unpack('<ff', data)
            pulseTime = floats[0]
            pulseValue = floats[1]

            print(pulseTime, pulseValue)

            if self.pulseQueue:
                self.pulseQueue.put(pulseValue)