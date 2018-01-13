import time
import logging

from rtlsdr import RtlSdr
from matplotlib.mlab import magnitude_spectrum, psd
from multiprocessing import Process
from Queue import Queue

NFFT = 64
NUM_SAMPLES_PER_SCAN = 1024 # NFFT * 16

class PulseDetector(Process):
    def __init__(self, deviceIndex, testPulse, pulseQueue, freqQueue, gainQueue, ampQueue):
        Process.__init__(self)
        self.deviceIndex = deviceIndex
        self.testPulse = testPulse
        self.amp = False
        self.freq = 146000000
        self.gain = 1
        self.pulseQueue = pulseQueue
        self.freqQueue = freqQueue
        self.gainQueue = gainQueue
        self.ampQueue = ampQueue
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

    def run(self):
        logging.debug("PulseDetector.run %d", self.deviceIndex)
        try:
            sdr = RtlSdr(device_index = self.deviceIndex)
            sdr.rs = 2.4e6
            sdr.fc = self.freq
            sdr.gain = self.gain
        except Exception as e:
            logging.exception("SDR init failed %d, self.deviceIndex")
            return

        last_max_mag = 0
        leadingEdge = False
        rgPulse = []
        lastPulseTime = time.time()
        timeoutCount = 0
        pulseCount = 0

        while True:
            # Handle change in frequency
            if not self.freqQueue.empty():
                newFrequency = self.freqQueue.get_nowait()
                logging.debug("Changing frequency %d", newFrequency)
                sdr.fc = newFrequency

            # Handle change in gain
            if not self.gainQueue.empty():
                newGain = self.gainQueue.get_nowait()
                sdr.gain = newGain
                logging.debug("Changing gain %d:%f", newGain, sdr.gain)

            # Handle change in amp
            if not self.ampQueue.empty():
                newAmp = self.ampQueue.get_nowait()
                self.amp = newAmp
                logging.debug("Changing amp %s", self.amp)

            # Adjust noise threshold
            sdrReopen = False
            noiseThreshold = self.calcNoiseThreshold(self.amp, sdr.gain)
            #logging.debug("Noise threshold %f", noiseThreshold)

            # Read samples
            try:
                samples = sdr.read_samples(NUM_SAMPLES_PER_SCAN)
            except Exception as e:
                logging.exception("SDR read failed %d, self.deviceIndex")
                sdrReopen = True
            if sdrReopen:
                logging.debug("Attempting reopen %d", self.deviceIndex)
                try:
                    sdr.open()
                except Exception as e:
                    logging.exception("SDR reopen failed %d", self.deviceIndex)
                    return
                try:
                    samples = sdr.read_samples(NUM_SAMPLES_PER_SCAN)
                except Exception as e:
                    logging.exception("SDR read failed %d", self.deviceIndex)
                    return

            # Process samples
            mag, freqs = magnitude_spectrum(samples, Fs=sdr.rs)
            strength = max(mag)
            #print(strength)
            if not leadingEdge:
                # Detect possible leading edge
                if strength > noiseThreshold:
                    leadingEdge = True
                    logging.debug("leading edge index:strength %d:%f", self.deviceIndex, strength)
                    rgPulse = [ strength ]
            else:
                rgPulse.append(strength)
                # Detect trailing edge
                if strength < noiseThreshold:
                    leadingEdge = False
                    pulseStrength = max(rgPulse)
                    pulseCount += 1
                    logging.debug("index:pulseStrength:len(rgPulse):pulseCount %d %f %d %d", self.deviceIndex, pulseStrength, len(rgPulse), pulseCount)
                    if not self.testPulse:
	                    self.pulseQueue.put((self.deviceIndex, pulseStrength))
                    lastPulseTime = time.time()
                    rgPulse = []
            lastStrength = strength

            # Check for no pulse
            if time.time() - lastPulseTime > 2:
                timeoutCount += 1
                if leadingEdge:
                    leadingEdge = False
                    logging.error("failed to detect trailing edge - index:len(rgPulse):timeoutCount %d:%d:%d", self.deviceIndex, len(rgPulse), timeoutCount)
                else:
                    logging.debug("no pulse for two seconds - index:timeoutCount %d:%d", self.deviceIndex, timeoutCount)
                    rgPulse = [ ]
                    if not self.testPulse:
                        self.pulseQueue.put((self.deviceIndex, 0))
                lastPulseTime = time.time()
        sdr.close()
