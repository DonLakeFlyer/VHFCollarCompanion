import time
import logging

from rtlsdr import RtlSdr
from matplotlib.mlab import magnitude_spectrum
from multiprocessing import Process

NFFT = 64
NUM_SAMPLES_PER_SCAN = NFFT * 16

class PulseDetector(Process):
    def __init__(self, pulseQueue):
        Process.__init__(self)
        self.pulseQueue = pulseQueue

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
        noiseThreshold = 50
        ratioMultiplier = 10
        lastPulseTime = time.time()
        timeoutCount = 0
        pulseCount = 0

        while True:
            try:
                samples = sdr.read_samples(NUM_SAMPLES_PER_SCAN)
            except Exception as e:
                logging.exception("SDR read failed")
                return
            mag, freqs = magnitude_spectrum(samples)
            strength = mag[len(mag) // 2]
            if not leadingEdge:
                # Detect possible leading edge
                if strength > noiseThreshold and strength > lastStrength * ratioMultiplier:
                    leadingEdge = True
                    logging.debug("leading edge")
                    rgPulse = [ strength ]
            else:
                rgPulse.append(strength)
                # Detect trailing edge
                if strength < lastStrength / ratioMultiplier:
                    leadingEdge = False
                    pulseStrength = max(rgPulse)
                    pulseCount += 1
                    logging.debug("trailing edge pulseStrength:len(rgPulse):pulseCount %d %d %d", pulseStrength, len(rgPulse), pulseCount)
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