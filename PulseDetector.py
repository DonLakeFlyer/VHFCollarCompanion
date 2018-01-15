import time
import logging
import numpy as np

from rtlsdr import RtlSdr
from matplotlib.mlab import magnitude_spectrum, psd
from multiprocessing import Process
from queue import Queue

NFFT = 64
NUM_SAMPLES_PER_SCAN = 1024 # NFFT * 16

class PulseDetector(Process):
    def __init__(self, pulseQueue, setFreqQueue, setGainQueue, setAmpQueue):
        Process.__init__(self)
        self.amp = True
        self.pulseQueue = pulseQueue
        self.setFreqQueue = setFreqQueue
        self.setGainQueue = setGainQueue
        self.setAmpQueue = setAmpQueue
        self.backgroundNoise = 1000
        self.minBackgroundNoise = 5.0
        self.minPulseCaptureCount = 3

    def adjustBackgroundNoise(self, strength):
        self.backgroundNoise = (self.backgroundNoise * 0.8) + (strength * 0.2)
        if self.backgroundNoise < self.minBackgroundNoise:
            self.backgroundNoise = self.minBackgroundNoise
        #logging.debug("Background noise:signal %f:%f", self.backgroundNoise, strength)

    def detectedPulseStrength(self, values):
        pulseDetected = False
        noiseThreshold = self.backgroundNoise * 1.5
        maxIndex = values.argmax()
        maxStrength = values[maxIndex]
        if maxStrength > noiseThreshold:         
            startIndex = maxIndex
            while values[startIndex] > noiseThreshold and startIndex > 0:
                startIndex -= 1
            stopIndex = maxIndex
            while values[stopIndex] > noiseThreshold and stopIndex < len(values) - 1:
                stopIndex += 1
            width = stopIndex - startIndex
            logging.debug("detectedPulseStrength value:index:width %d:%d:%d", maxStrength, maxIndex, width)
            if width >= 3:
                pulseDetected = True
        if pulseDetected:
            return maxStrength
        else:
            self.adjustBackgroundNoise(maxStrength)
            return 0

    def run(self):
        logging.debug("PulseDetector.run")
        try:
            sdr = RtlSdr()
            sdr.rs = 2.4e6
            sdr.fc = 146e6
            sdr.gain = 10
        except Exception as e:
            logging.exception("SDR init failed")
            return

        last_max_mag = 0
        leadingEdge = False
        rgPulse = []
        lastPulseTime = time.time()
        #timeoutCount = 0
        pulseCount = 0

        while True:
            # Handle change in frequency
            try:
                newFrequency = self.setFreqQueue.get_nowait()
            except Exception as e:
                pass
            else:
                logging.debug("Changing frequency %d", newFrequency)
                sdr.fc = newFrequency

            # Handle change in gain
            try:
                newGain = self.setGainQueue.get_nowait()
            except Exception as e:
                pass
            else:
                sdr.gain = newGain
                logging.debug("Changing gain %d:%f", newGain, sdr.gain)

            # Handle change in amp
            try:
                newAmp = self.setAmpQueue.get_nowait()
            except Exception as e:
                pass
            else:
                self.amp = newAmp
                logging.debug("Changing amp %s", self.amp)

            # Adjust noise threshold
            sdrReopen = False
            #noiseThreshold = self.calcNoiseThreshold(self.amp, sdr.gain)
            #logging.debug("Noise threshold %f", noiseThreshold)

            # Read samples
            try:
                samples = sdr.read_samples(NUM_SAMPLES_PER_SCAN)
            except Exception as e:
                logging.exception("SDR read failed")
                sdrReopen = True
            if sdrReopen:
                logging.debug("Attempting reopen")
                try:
                    sdr.open()
                except Exception as e:
                    logging.exception("SDR reopen failed")
                    return
                try:
                    samples = sdr.read_samples(NUM_SAMPLES_PER_SCAN)
                except Exception as e:
                    logging.exception("SDR read failed")
                    return

            # Process samples
            mag, freqs = magnitude_spectrum(samples, Fs=sdr.rs)
            if not leadingEdge:
                # Detect leading edge
                strength = self.detectedPulseStrength(mag)
                if strength:
                    leadingEdge = True
                    #logging.debug("leading edge strength:background %d %d", strength, self.backgroundNoise)
                    rgPulse = [ strength ]
            else:
                # Detect trailing edge falling below background noise
                strength = self.detectedPulseStrength(mag)
                if strength:
                    rgPulse.append(strength)
                else:
                    leadingEdge = False
                    pulseCaptureCount = len(rgPulse)
                    self.adjustBackgroundNoise(strength)
                    if pulseCaptureCount >= self.minPulseCaptureCount:
                        pulseStrength = max(rgPulse)
                        pulseCount += 1
                        logging.debug("***** %d %d %d pulseStrength:len(rgPulse):background", pulseStrength, pulseCaptureCount, self.backgroundNoise)
                        if self.pulseQueue:
                            self.pulseQueue.put(pulseStrength)
                        lastPulseTime = time.time()
                    else:
                        logging.debug("pulse too short %d", pulseCaptureCount)
                        for skippedStrength in rgPulse:
                            self.adjustBackgroundNoise(skippedStrength)                            
                    rgPulse = []

            # Check for no pulse
            if time.time() - lastPulseTime > 3:
                #timeoutCount += 1
                if leadingEdge:
                    leadingEdge = False
                    logging.error("failed to detect trailing edge - len(rgPulse):background %d %d", len(rgPulse), self.backgroundNoise)
                else:
                    logging.debug("no pulse for two seconds - background %d", self.backgroundNoise)
                    if self.pulseQueue:
                        self.pulseQueue.put(0)
                rgPulse = [ ]
                lastPulseTime = time.time()
        sdr.close()
