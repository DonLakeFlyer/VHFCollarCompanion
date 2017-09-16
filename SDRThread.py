import threading
import time
import MavlinkThread
import geo

from rtlsdr import RtlSdr
from matplotlib.mlab import magnitude_spectrum

NFFT = 64 #1024*4
NUM_SAMPLES_PER_SCAN = NFFT*16
NUM_BUFFERED_SWEEPS = 100

BPM = 45.0

# change this to control the number of scans that are combined in a single sweep
# (e.g. 2, 3, 4, etc.) Note that it can slow things down
NUM_SCANS_PER_SWEEP = 1

# these are the increments when scrolling the mouse wheel or pressing '+' or '-'
FREQ_INC_COARSE = 1e6
FREQ_INC_FINE = 0.1e6
GAIN_INC = 5

class SDRThread (threading.Thread):
    def __init__(self, mavlinkThread, vehicle, exitEvent, simulate):
        threading.Thread.__init__(self)
        self.mavlinkThread = mavlinkThread
        self.vehicle = vehicle
        self.exitEvent = exitEvent
        self.simulate = simulate
        self.lock = threading.Lock()
        self.rgStrength = []
        self.lastBeepDetectedTime = time.perf_counter()
        self.beepDetectedEvent = threading.Event()
        self.beepCallback = None

    def run(self):
        if self.simulate:
            self.runSimulate()
        else:
            self.runSample()

    def runSample(self):
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

        while not self.exitEvent.isSet():
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
                        self.lastBeepDetectedTime = time.perf_counter()
                        beepStrength = max(rgBeep)
                        print("rgBeep", beepStrength, rgBeep)
                        self.rgStrength.append(beepStrength)
                        self.sendBeepStrength(beepStrength)
                    rgBeep = []
            last_max_mag = max_mag
            if time.perf_counter() - self.lastBeepDetectedTime > 10:
                # No beeps detected for 10 seconds
                self.sendBeepStrength(0)
                self.lastBeepDetectedTime = time.perf_counter()
        sdr.close()

    def runSimulate(self):
        self.simulationTimer = threading.Timer(60.0 / BPM, self.simulateBeep)
        self.simulationTimer.start()
        self.exitEvent.wait()

    def sendBeepStrength(self, strength):
        #print("sendBeepStrength", strength)
        self.mavlinkThread.sendMessageLock.acquire()
        self.mavlinkThread.mavlink.mav.debug_send(0, 0, strength)
        self.mavlinkThread.sendMessageLock.release()
        self.lastBeepStrength = strength
        self.beepDetectedEvent.set()
        if self.beepCallback is not None:
            self.beepCallback(strength)
            self.beepCallback = None

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
            retSignalStrength = max(self.rgStrength)
        self.lock.release()
        return retSignalStrength

    def simulateBeep(self):
        if self.vehicle.homePositionSet:
            angleToCollar = geo.great_circle_angle(self.vehicle.homePosition,
                                                   self.vehicle.position, 
                                                   geo.magnetic_northpole)
            distanceToCollar = geo.distance(self.vehicle.position, 
                                            self.vehicle.homePosition)
            vehicleHeadingToCollar = self.vehicle.heading - angleToCollar
            #print("simulateBeep", angleToCollar, distanceToCollar, self.mavlinkThread.vehicleHeading, vehicleHeadingToCollar)
            # Start at full strength
            beepStrength = 500.0 
            # Adjust for distance
            maxDistance = 2000.0
            distanceToCollar = min(distanceToCollar, maxDistance)
            beepStrength *= (maxDistance - distanceToCollar) / maxDistance
            # Adjust for vehicle heading in relationship to direction to collar
            vehicleHeadingToCollar = abs(vehicleHeadingToCollar)
            if vehicleHeadingToCollar > 180.0:
                vehicleHeadingToCollar = 180.0 - (vehicleHeadingToCollar - 180.0)
            vehicleHeadingToCollar = 180.0 - vehicleHeadingToCollar
            beepMultiplier = vehicleHeadingToCollar / 180.0
            #print("beepMultiplier", beepMultiplier, vehicleHeadingToCollar)
            beepStrength *= beepMultiplier
            self.sendBeepStrength(beepStrength)
        else:
            print("simulateBeep - home position not set")
        self.simulationTimer = threading.Timer(60.0 / BPM, self.simulateBeep)
        self.simulationTimer.start()
