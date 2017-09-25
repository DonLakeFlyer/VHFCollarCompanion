import Tools
import MavlinkThread
import PulseDetector
import Vehicle
import DirectionFinder
import PulseSender
import sys
import logging

from argparse import ArgumentParser
from time import gmtime, strftime

def main():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("--baudrate", type=int, help="px4 port baud rate", default=57600)
	parser.add_argument("--device", help="px4 device", default="/dev/ttyS0")
	parser.add_argument("--simulateVehicle", help="simulate vehicle", default=False)
	parser.add_argument("--testPulse", help="test PulseDetector", default=False)
	parser.add_argument("--logfile", help="logfile output", default="")
	args = parser.parse_args()

	if logfile:
		logging.basicConfig(filename=logfile,level=logging.DEBUG)

	tools = Tools.Tools()
	tools.mavlinkThread = MavlinkThread.MavlinkThread(tools, args)
	tools.vehicle = Vehicle.Vehicle(tools)
	tools.directionFinder = DirectionFinder.DirectionFinder(tools)
	pulseSender = PulseSender.PulseSender(tools)
	pulseSender.start()

	tools.mavlinkThread.start()
	pulseDetector = PulseDetector.PulseDetector(tools.pulseQueue)
	pulseDetector.start()

if __name__ == '__main__':
    main()