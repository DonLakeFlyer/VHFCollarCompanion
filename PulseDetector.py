import time
import logging

from rtlsdr import RtlSdr
from matplotlib.mlab import magnitude_spectrum, psd
from multiprocessing import Process
from queue import Queue
from scipy.signal import decimate

NFFT = 64
NUM_SAMPLES_PER_SCAN = 1024 # NFFT * 16

class PulseDetector(Process):
    def __init__(self, pulseQueue, setFreqQueue, setGainQueue):
        Process.__init__(self)
        self.pulseQueue = pulseQueue
        self.setFreqQueue = setFreqQueue
        self.setGainQueue = setGainQueue

    def run(self):
        logging.debug("PulseDetector.run")
        try:
            sdr = RtlSdr()
            sdr.rs = 2.4e6
            sdr.fc = 146e6
            sdr.gain = 25
        except Exception as e:
            logging.exception("SDR init failed")
            return

        last_max_mag = 0
        leadingEdge = False
        rgPulse = []
        noiseThreshold = 100
        decimateCount = 8
        ratioMultiplier = 10
        lastPulseTime = time.time()
        timeoutCount = 0
        pulseCount = 0

        while True:
            try:
                newFrequency = self.setFreqQueue.get_nowait()
            except Exception as e:
                pass
            else:
                logging.debug("Changing frequency %d", newFrequency)
                sdr.fc = newFrequency
            try:
                newGain = self.setGainQueue.get_nowait()
            except Exception as e:
                pass
            else:
                sdr.gain = newGain
                logging.debug("Changing gain %d:%d", newGain, sdr.gain)
            sdrReopen = False
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
            decimateSamples = samples
            #decimateSamples = decimate(samples, decimateCount)
            #noiseThreshold /= float(decimateCount)
            mag, freqs = magnitude_spectrum(decimateSamples, Fs=sdr.rs)
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
                self.pulseQueue.put(0)
                lastPulseTime = time.time()
        sdr.close()
