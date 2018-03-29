import time
import logging

from rtlsdr import RtlSdr
from matplotlib.mlab import magnitude_spectrum, psd
from multiprocessing import Process
from Queue import Queue

NFFT = 64
NUM_SAMPLES_PER_SCAN = 1024 # NFFT * 16

class PulseDetector(Process):
    def __init__(self, deviceIndex, pulseQueue, setFreqQueue, setGainQueue, setAmpQueue):
        Process.__init__(self)
        self.deviceIndex = deviceIndex
        self.amp = True
        self.pulseQueue = pulseQueue
        self.setFreqQueue = setFreqQueue
        self.setGainQueue = setGainQueue
        self.setAmpQueue = setAmpQueue
        self.minNoiseThresholdAmp = 15
        self.maxNoiseThresholdAmp = 130
        self.minNoiseThreshold = 1
        self.maxNoiseThreshold = 15
        self.backgroundNoise = 15.0
        self.minBackgroundNoise = 5.0
        self.minPulseCaptureCount = 3

    def calcNoiseThreshold(self, amp, gain):
        if amp:
            minNoiseThreshold = self.minNoiseThresholdAmp
            maxNoiseThreshold = self.maxNoiseThresholdAmp
        else:
            minNoiseThreshold = self.minNoiseThreshold
            maxNoiseThreshold = self.maxNoiseThreshold
        noiseRange = maxNoiseThreshold - minNoiseThreshold
        return minNoiseThreshold + (noiseRange * (gain / 50.0))

    def adjustBackgroundNoise(self, signalStrength):
        self.backgroundNoise = (self.backgroundNoise * 0.98) + (signalStrength * 0.02)
        if self.backgroundNoise < self.minBackgroundNoise:
            self.backgroundNoise = self.minBackgroundNoise
        #logging.debug("Background index:noise:signal %d:%f:%f", self.deviceIndex, self.backgroundNoise, signalStrength)

    def run(self):
        logging.debug("PulseDetector.run %d", self.deviceIndex)
        try:
            sdr = RtlSdr(device_index = self.deviceIndex)
            sdr.rs = 2.4e6
            sdr.fc = 146e6
            sdr.gain = 60
        except Exception as e:
            logging.exception("SDR init failed %d", self.deviceIndex)
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
                logging.debug("Changing index:frequency %d:%d", self.deviceIndex, newFrequency)
                sdr.fc = newFrequency

            # Handle change in gain
            try:
                newGain = self.setGainQueue.get_nowait()
            except Exception as e:
                pass
            else:
                sdr.gain = newGain
                logging.debug("Changing index:gain:actual %d:%d:%f", self.deviceIndex, newGain, sdr.gain)

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
            strength = max(mag)
            #print(strength)
            self.adjustBackgroundNoise(strength)
            noiseThreshold = self.backgroundNoise * 1.5
            if not leadingEdge:
                # Detect possible leading edge spiking above background noise
                if strength > noiseThreshold:
                    leadingEdge = True
                    #logging.debug("leading edge index:strength:background %d %d %d", self.deviceIndex, strength, self.backgroundNoise)
                    rgPulse = [ strength ]
            else:
                rgPulse.append(strength)
                # Detect trailing edge falling below background noise
                if strength < noiseThreshold:
                    leadingEdge = False
                    pulseCaptureCount = len(rgPulse)
                    if pulseCaptureCount >= self.minPulseCaptureCount:
                        pulseStrength = max(rgPulse)
                        pulseCount += 1
                        logging.debug("***** %d %d %d %d index:pulseStrength:len(rgPulse):background", self.deviceIndex, pulseStrength, pulseCaptureCount, self.backgroundNoise)
                        if self.pulseQueue:
                            self.pulseQueue.put((self.deviceIndex, pulseStrength))
                        lastPulseTime = time.time()
                    else:
                        #logging.debug("pulse too short index:count %d:%d", self.deviceIndex, pulseCaptureCount)
                        pass
                    rgPulse = []
            lastStrength = strength

            # Check for no pulse
            if time.time() - lastPulseTime > 2:
                #timeoutCount += 1
                if leadingEdge:
                    leadingEdge = False
                    #logging.error("failed to detect trailing edge - index:len(rgPulse):background %d %d %d", self.deviceIndex, len(rgPulse), self.backgroundNoise)
                else:
                    logging.debug("no pulse for two seconds - index:background %d %d", self.deviceIndex, self.backgroundNoise)
                    if self.pulseQueue:
                        self.pulseQueue.put((self.deviceIndex, 0))
                rgPulse = [ ]
                lastPulseTime = time.time()
        sdr.close()
