import threading
import multiprocessing
import time
import geo

from rtlsdr import RtlSdr
from matplotlib.mlab import magnitude_spectrum

NFFT = 64
NUM_SAMPLES_PER_SCAN = NFFT * 16
NUM_BUFFERED_SWEEPS = 100

BPM = 45.0

class PulseDetector(multiprocessing.Process):
    def __init__(self, tools, args):
        self.tools = tools
        self.simulateVehicle = args.simulateVehicle
        self.testPulse = args.testPulse
        print("PulseDetector.ini", self.simulateVehicle, self.testPulse)
        self.rgStrength = []
        self.lastBeepDetectedTime = time.perf_counter()
        self.beepCallback = None

    def run(self):
        if self.simulateVehicle:
            self.runSimulate()
        else:
            self.sdrSample()

    def sdrSample(self):
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
        while True:
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
                    if self.testPulse:
                        print("Leading edge")
            else:
                rgBeep.append(strength)
                # Detect trailing edge
                if strength < lastStrength / ratioMultiplier:
                    if self.testPulse:
                        print("Trailing edge")
                    leadingEdge = False
                    beepStrength = max(rgBeep)
                    if self.testPulse:
                        print("rgBeep", beepStrength, rgBeep)
                    self.sendBeepStrength(beepStrength)
                    rgBeep = []
            lastStrength = strength
        sdr.close()

    def runSimulate(self):
        self.simulationTimer = threading.Timer(60.0 / BPM, self.simulatePulse)
        self.simulationTimer.start()

    def sendBeepStrength(self, strength):
        if self.testPulse or self.simulatePulse:
            print("sendBeepStrength", strength)
            if self.testPulse:
                return
        self.tools.mavlinkThread.sendMessageLock.acquire()
        self.tools.mavlinkThread.mavlink.mav.debug_send(0, 0, strength)
        #rgZeroes = [0] * 32
        #self.tools.mavlinkThread.mavlink.mav.memory_vect_send(0,        # address
        #                                  1,        # ver
        #                                  0,        # type
        #                                  rgZeroes) # values
        self.tools.mavlinkThread.sendMessageLock.release()
        self.lastBeepStrength = strength
        if self.beepCallback is not None:
            bc = self.beepCallback
            self.beepCallback = None
            bc(strength)

    def simulatePulse(self):
        if self.tools.vehicle.homePositionSet:
            angleToCollar = geo.great_circle_angle(self.tools.vehicle.homePosition,
                                                   self.tools.vehicle.position, 
                                                   geo.magnetic_northpole)
            distanceToCollar = geo.distance(self.tools.vehicle.position, 
                                            self.tools.vehicle.homePosition)
            vehicleHeadingToCollar = self.tools.vehicle.heading - angleToCollar
            #print("simulateBeep", angleToCollar, distanceToCollar, self.tools.mavlinkThread.vehicleHeading, vehicleHeadingToCollar)
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
        self.simulationTimer = threading.Timer(60.0 / BPM, self.simulatePulse)
        self.simulationTimer.start()
