import time
import logging
import threading
import geo 

from matplotlib.mlab import magnitude_spectrum
from multiprocessing import Process
from PulseBase import PulseBase


BPM = 45

class PulseDetectorSimulator (PulseBase):
    def __init__(self, tools):
        PulseBase.__init__(self, tools.pulseQueue, tools.setFreqQueue, tools.setGainQueue)
        self.vehicle = tools.vehicle
        self.freq = 146000000
        self.simulationTimer = threading.Timer(60.0 / BPM, self.simulatePulse)
        self.simulationTimer.start()

#    def run(self):
#        logging.debug("PulseDetectorSimulator run")

    def simulatePulse(self):
        self.checkQueues()
        if self.vehicle.homePositionSet:
            headingToCollar = 80.0
            pulseStrength = 20.0 # max
            headingDifference = abs(self.vehicle.heading - headingToCollar)
            if headingDifference > 180.0:
                headingDifference = 180 - (headingDifference - 180.0)
            headingDifference = abs(headingDifference - 180.0)
            pctOfFullStrength = 0
            if self.vehicle.altRel > 10:
                pctOfFullStrength = headingDifference / 180.0
                altDiff = max(0, 121.0 - self.vehicle.altRel)
                altDiff = abs(altDiff - 121.0)
                pctOfFullStrength *= altDiff / 121
            pulseStrength *= pctOfFullStrength
            self.pulseQueue.put([pulseStrength, self.freq, 31.0])
        self.simulationTimer = threading.Timer(60.0 / BPM, self.simulatePulse)
        self.simulationTimer.start()

    def simulatePulseOld(self):
        self.checkQueues()
        if self.vehicle.homePositionSet:
            if self.vehicle.homePosition == self.vehicle.position:
                self.pulseQueue.put(0)
            else:
                angleToCollar = geo.great_circle_angle(self.vehicle.homePosition,
                                                       self.vehicle.position, 
                                                       geo.geographic_northpole)
                distanceToCollar = geo.distance(self.vehicle.position, 
                                                self.vehicle.homePosition)
                vehicleHeadingToCollar = self.vehicle.heading - angleToCollar
                print("simulateBeep", angleToCollar, distanceToCollar, self.vehicle.heading, vehicleHeadingToCollar)
                # Start at full strength
                beepStrength = 600.0 
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
                print("beepMultiplier", beepMultiplier, vehicleHeadingToCollar)
                beepStrength *= beepMultiplier
                self.pulseQueue.put(beepStrength)
        else:
            print("simulateBeep - home position not set")
        self.simulationTimer = threading.Timer(60.0 / BPM, self.simulatePulse)
        self.simulationTimer.start()

    def changeFrequency(self, frequency):
        logging.debug("Simulate frequency change %f", frequency)
        self.freq = frequency

    def changeGain(self, gain):
        logging.debug("Simulate gain change %d", gain)