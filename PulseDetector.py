import time
import logging

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
        self.minNoiseThresholdAmp = 15
        self.maxNoiseThresholdAmp = 90
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
        logging.debug("PulseDetector.run")
        try:
            sdr = RtlSdr()
            sdr.rs = 2.4e6
            sdr.fc = 146e6
            sdr.gain = 60
        except Exception as e:
            logging.exception("SDR init failed")
            return

        last_max_mag = 0
        leadingEdge = False
        rgPulse = []
        lastPulseTime = time.time()
        timeoutCount = 0
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
            noiseThreshold = self.calcNoiseThreshold(self.amp, sdr.gain)
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
            #print(sum(mag))
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

            # Check for no pulse
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
        sdr.close()
