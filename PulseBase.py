import logging

from multiprocessing import Process
from queue import Queue

# Base class for real and simulated pulse handling
class PulseBase(Process):
    def __init__(self, pulseQueue, setFreqQueue, setGainQueue, setAmpQueue):
        Process.__init__(self)
        self.amp = False
        self.pulseQueue = pulseQueue
        self.setFreqQueue = setFreqQueue
        self.setGainQueue = setGainQueue
        self.setAmpQueue = setAmpQueue
        self.minNoiseThresholdAmp = 15
        self.maxNoiseThresholdAmp = 110
        self.minNoiseThreshold = 1
        self.maxNoiseThreshold = 15

    def calcNoiseThreshold(self, amp, gain):
        if amp:
            minNoiseThreshold = self.minNoiseThresholdAmp
            maxNoiseThreshold = self.maxNoiseThresholdAmp
        else:
            minNoiseThreshold = self.minNoiseThreshold
            maxNoiseThreshold = self.maxNoiseThreshold
        noiseRange = maxNoiseThreshold - minNoiseThreshold
        return minNoiseThreshold + (noiseRange * (gain / 50.0))

    def checkQueues(self):
        # Handle change in frequency    
        try:
            newFrequency = self.setFreqQueue.get_nowait()
        except Exception as e:
            pass
        else:
            logging.debug("Changing frequency %d", newFrequency)
            self.changeFrequency(newFrequency)

        # Handle change in gain
        try:
            newGain = self.setGainQueue.get_nowait()
        except Exception as e:
            pass
        else:
            logging.debug("Changing gain %d", newGain)
            self.changeGain(newGain)

        # Handle change in amp
        try:
            newAmp = self.setAmpQueue.get_nowait()
        except Exception as e:
            pass
        else:
            self.amp = newAmp
            logging.debug("Changing amp %s", self.amp)