import threading
import time
#import MavlinkThread
#import geo

from rtlsdr import RtlSdr
from matplotlib.mlab import magnitude_spectrum

NFFT = 64
NUM_SAMPLES_PER_SCAN = NFFT * 16
NUM_BUFFERED_SWEEPS = 100

BPM = 45.0

class SDRThread:
    def __init__(self, mavlinkThread, vehicle, exitEvent, simulate):
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

        msecs = int(round(time.time() * 1000))
        while not self.exitEvent.isSet():
            samples = sdr.read_samples(NUM_SAMPLES_PER_SCAN)
            mag, freqs = magnitude_spectrum(samples)
            strength = mag[len(mag) // 2]
            #new_msecs = int(round(time.time() * 1000))
            #print(strength, new_msecs - msecs)
            #msecs = new_msecs
            #continue
            if not leadingEdge:
                # Detect possible leading edge
                if strength > noiseThreshold and strength > lastStrength * ratioMultiplier:
                    leadingEdge = True
                    rgBeep.append(strength)
                    leadingEdgeStartTime = time.perf_counter()
                    print("Leading edge")
            else:
                rgBeep.append(strength)
                # Detect trailing edge
                if strength < lastStrength / ratioMultiplier:
                    print("Trailing edge")
                    leadingEdge = False
                    beepStrength = max(rgBeep)
                    print("rgBeep", beepStrength, rgBeep)
                    self.sendBeepStrength(beepStrength)
                    rgBeep = []
            lastStrength = strength
        sdr.close()

    def runSimulate(self):
        self.simulationTimer = threading.Timer(60.0 / BPM, self.simulateBeep)
        self.simulationTimer.start()
        self.exitEvent.wait()

    def sendBeepStrength(self, strength):
        print("sendBeepStrength", strength)
        return
        self.mavlinkThread.sendMessageLock.acquire()
        self.mavlinkThread.mavlink.mav.debug_send(0, 0, strength)
        self.mavlinkThread.sendMessageLock.release()
        self.lastBeepStrength = strength
        self.beepDetectedEvent.set()
        if self.beepCallback is not None:
            bc = self.beepCallback
            self.beepCallback = None
            bc(strength)

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
            maxDistance = 500.0
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
            if beepStrength > 0:
                self.sendBeepStrength(beepStrength)
        else:
            print("simulateBeep - home position not set")
        self.simulationTimer = threading.Timer(60.0 / BPM, self.simulateBeep)
        self.simulationTimer.start()
