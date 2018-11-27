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
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind(('localhost', 10000))
        self.udpAddress = ('localhost', 10000)

    def processFreqQueue(self):
        try:
            self.freq = self.setFreqQueue.get_nowait()
        except Exception as e:
            pass
        else:
            logging.debug("Changing frequency %f", self.freq)
            self.udpSocket.sendto("freq " + str(self.freq), self.udpAddress)

    def processGainQueue(self):
        try:
            self.gain = self.setGainQueue.get_nowait()
        except Exception as e:
            pass
        else:
            logging.debug("Changing gain %d", self.gain)
            self.udpSocket.sendto("gain " + str(self.gain), self.udpAddress)

    def run(self):
        logging.debug("PulseCapture.run")

        while True:
            self.processFreqQueue()
            self.processGainQueue()

            data, address = self.udpSocket.recvfrom(4)
            floats = struct.unpack('<f', data)
            pulseValue = floats[0]
            logging.debug("PulseCapture pulseValue %d", pulseValue)

            if self.pulseQueue:
                self.pulseQueue.put(pulseValue)
