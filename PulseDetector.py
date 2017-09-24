import time

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
        print("PulseDetector.run")
        sdr = RtlSdr()
        sdr.rs = 2.4e6
        sdr.fc = 146e6
        sdr.gain = 10

        last_max_mag = 0
        leadingEdge = False
        rgPulse = []
        noiseThreshold = 50
        ratioMultiplier = 10
        lastPulseTime = time.time()

        while True:
            samples = sdr.read_samples(NUM_SAMPLES_PER_SCAN)
            mag, freqs = magnitude_spectrum(samples)
            strength = mag[len(mag) // 2]
            if not leadingEdge:
                # Detect possible leading edge
                if strength > noiseThreshold and strength > lastStrength * ratioMultiplier:
                    leadingEdge = True
                    rgPulse = [ strength ]
            else:
                rgPulse.append(strength)
                # Detect trailing edge
                if strength < lastStrength / ratioMultiplier:
                    leadingEdge = False
                    pulseStrength = max(rgPulse)
                    self.pulseQueue.put(pulseStrength)
                    lastPulseTime = time.time()
                    rgPulse = []
            lastStrength = strength
            if time.time() - lastPulseTime > 2:
                self.pulseQueue.put(0)
                lastPulseTime = time.time()

        sdr.close()