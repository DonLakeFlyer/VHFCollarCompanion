import Tools
import MavlinkThread
import PulseDetector
import PulseDetectorSimulator
import Vehicle
import DirectionFinder
import PulseSender
import CollarLogging

import sys
import logging

from argparse import ArgumentParser
from time import gmtime, strftime

def main():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("--baudrate", type=int, help="px4 port baud rate", default=57600)
	parser.add_argument("--device", help="px4 device", default="/dev/ttyS0")
	parser.add_argument("--simulateVehicle", help="simulate vehicle", default=False)
	parser.add_argument("--simulatePulse", help="simulate pulses", default=False)
	parser.add_argument("--logdir", help="log directory", default="")
	args = parser.parse_args()

	CollarLogging.setupLogging(args.logdir)

	tools = Tools.Tools()
	tools.mavlinkThread = MavlinkThread.MavlinkThread(tools, args)
	tools.vehicle = Vehicle.Vehicle(tools)
	tools.directionFinder = DirectionFinder.DirectionFinder(tools)
	tools.pulseSender = PulseSender.PulseSender(tools)
	tools.pulseSender.start()

	tools.mavlinkThread.start()

	if args.simulatePulse:
		pulseDetector = PulseDetectorSimulator.PulseDetectorSimulator(tools)
		pulseDetector.start()
	else:
		pulseDetector = PulseDetector.PulseDetector(tools.pulseQueue, tools.setFreqQueue, tools.setGainQueue)
		pulseDetector.start()

if __name__ == '__main__':
    main()