import time
import logging
import threading

import geo 

from rtlsdr import RtlSdr
from matplotlib.mlab import magnitude_spectrum
from multiprocessing import Process

BPM = 45

class PulseDetectorSimulator:
    def __init__(self, tools):
        self.tools = tools

    def start(self):
        self.simulationTimer = threading.Timer(60.0 / BPM, self.simulatePulse)
        self.simulationTimer.start()

    def simulatePulse(self):
        if self.tools.vehicle.homePositionSet:
            if self.tools.vehicle.homePosition == self.tools.vehicle.position:
                self.tools.pulseQueue.put(0)
            else:
                angleToCollar = geo.great_circle_angle(self.tools.vehicle.homePosition,
                                                       self.tools.vehicle.position, 
                                                       geo.magnetic_northpole)
                distanceToCollar = geo.distance(self.tools.vehicle.position, 
                                                self.tools.vehicle.homePosition)
                vehicleHeadingToCollar = self.tools.vehicle.heading - angleToCollar
                #print("simulateBeep", angleToCollar, distanceToCollar, self.tools.mavlinkThread.vehicleHeading, vehicleHeadingToCollar)
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
                #print("beepMultiplier", beepMultiplier, vehicleHeadingToCollar)
                beepStrength *= beepMultiplier
                self.tools.pulseQueue.put(beepStrength)
        else:
            print("simulateBeep - home position not set")
        self.simulationTimer = threading.Timer(60.0 / BPM, self.simulatePulse)
        self.simulationTimer.start()
