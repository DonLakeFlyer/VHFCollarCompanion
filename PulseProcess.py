import time
import logging

from rtlsdr import RtlSdr
from matplotlib.mlab import magnitude_spectrum, psd
from multiprocessing import Process
from queue import Queue
from scipy.signal import decimate

class PulseProcess(Process):
    def __init__(self, sampleQueue, pulseQueue):
        Process.__init__(self)
        self.sampleQueue = sampleQueue
        self.pulseQueue = pulseQueue

    def run(self):
        logging.debug("PulseProcess.run")

        leadingEdge = False
        rgPulse = []
        noiseThreshold = 10
        decimateCount = 1
        ratioMultiplier = 10
        lastPulseTime = time.time()
        timeoutCount = 0
        pulseCount = 0

        while True:
            samples = self.sampleQueue.get()
            decimateSamples = samples
            #decimateSamples = decimate(samples, decimateCount)
            #noiseThreshold /= float(decimateCount)
            mag, freqs = magnitude_spectrum(decimateSamples)
            #mag, freqs = psd(decimateSamples, NFFT=NFFT)
            #strength = mag[len(mag) // 2]
            strength = max(mag)
            #print(strength)
            if not leadingEdge:
                # Detect possible leading edge
                if strength > noiseThreshold:
                    leadingEdge = True
                    logging.debug("leading edge %d", strength)
                    rgPulse = [ strength ]
            else:
                rgPulse.append(strength)
                # Detect trailing edge
                if strength < noiseThreshold:
                    leadingEdge = False
                    pulseStrength = max(rgPulse)
                    pulseCount += 1
                    logging.debug("pulseStrength:len(rgPulse):pulseCount %f %d %d", pulseStrength, len(rgPulse), pulseCount)
                    if self.pulseQueue:
                        self.pulseQueue.put(pulseStrength)
                    lastPulseTime = time.time()
                    rgPulse = []
            lastStrength = strength
            if time.time() - lastPulseTime > 2:
                timeoutCount += 1
                if leadingEdge:
                    leadingEdge = False
                    logging.error("failed to detect trailing edge - len(rgPulse):timeoutCount %d %d", len(rgPulse), timeoutCount)
                else:
                    logging.debug("no pulse for two seconds - timeoutCount %d", timeoutCount)
                    rgPulse = [ ]
                    if self.pulseQueue:
                        self.pulseQueue.put(0)
                lastPulseTime = time.time()
