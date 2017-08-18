import threading
import time

from rtlsdr import RtlSdr
from matplotlib.mlab import magnitude_spectrum

NFFT = 64 #1024*4
NUM_SAMPLES_PER_SCAN = NFFT*16
NUM_BUFFERED_SWEEPS = 100

# change this to control the number of scans that are combined in a single sweep
# (e.g. 2, 3, 4, etc.) Note that it can slow things down
NUM_SCANS_PER_SWEEP = 1

# these are the increments when scrolling the mouse wheel or pressing '+' or '-'
FREQ_INC_COARSE = 1e6
FREQ_INC_FINE = 0.1e6
GAIN_INC = 5

class SDRThread (threading.Thread):
    exitFlag = False

    def __init__(self):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.strength = 0
        self.rgStrength = []

    def run(self):
        self.exitFlag = False
        sdr = RtlSdr()
        sdr.rs = 2.4e6
        sdr.fc = 146e6
        sdr.gain = 10

        last_max_mag = 0
        leadingEdge = False
        rgBeep = []
        noiseThreshold = 50
        ratioMultiplier = 10
        beepLength = (1.0 / 1000.0) * 10.0

        while not self.exitFlag:
            samples = sdr.read_samples(NUM_SAMPLES_PER_SCAN)
            mag, freqs = magnitude_spectrum(samples)
            max_mag = max(mag)
            if not leadingEdge:
                # Detect possible leading edge
                if max_mag > noiseThreshold and max_mag > last_max_mag * ratioMultiplier:
                    leadingEdge = True
                    rgBeep.append(max_mag)
                    leadingEdgeStartTime = time.perf_counter()
                    print("Leading edge")
            else:
                rgBeep.append(max_mag)
                # Detect trailing edge
                if max_mag < last_max_mag / ratioMultiplier:
                    print("Trailing edge")
                    leadingEdge = False
                    # Was beep long enough
                    if time.perf_counter() - leadingEdgeStartTime > beepLength:
                        beepStrength = max(rgBeep)
                        print("rgBeep", rgBeep, beepStrength)
                        self.rgStrength.append(beepStrength)
                    rgBeep = []
            last_max_mag = max_mag

        sdr.close()

    def stop(self):
        self.exitFlag = True

    def startCapture(self):
        self.lock.acquire()
        self.rgStrength = []
        self.lock.release()

    def stopCapture(self):        
        self.lock.acquire()
        cStrength = len(self.rgStrength)
        if cStrength == 0:
            retSignalStrength = 0
        else:
            retSignalStrength = sum(self.rgStrength) / float(cStrength)
        self.lock.release()
        return retSignalStrength
