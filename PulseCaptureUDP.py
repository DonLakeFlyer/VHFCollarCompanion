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
        self.sendAddress = ('localhost', 10001)

    def processFreqQueue(self):
        try:
            self.freq = self.setFreqQueue.get_nowait()
        except Exception as e:
            pass
        else:
            logging.debug("Changing frequency %f", self.freq)
            self.udpSocket.sendto(struct.pack('<ii', 2, self.freq), self.sendAddress)

    def processGainQueue(self):
        try:
            self.gain = self.setGainQueue.get_nowait()
        except Exception as e:
            pass
        else:
            logging.debug("Changing gain %d", self.gain)
            self.udpSocket.sendto(struct.pack('<ii', 1, self.gain), self.sendAddress)

    def run(self):
        logging.debug("PulseCaptureUDP receive loop")
        while True:
            self.processFreqQueue()
            self.processGainQueue()

            data, address = self.udpSocket.recvfrom(4*6)
            rgPulseInfo = struct.unpack('<iiffii', data)
            channelIndex = rgPulseInfo[1]
            pulseValue = rgPulseInfo[2]
            temp = rgPulseInfo[3]
            freq = rgPulseInfo[4]
            gain = rgPulseInfo[5]
            logging.debug("PulseCaptureUDP pulseValue %d temp %f freq %d gain %d", pulseValue, temp, freq, gain)

            if self.pulseQueue:
                self.pulseQueue.put([pulseValue, freq, temp])
