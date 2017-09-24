import Tools
import MavlinkThread
import PulseDetector
import Vehicle
import DirectionFinder
import PulseSender
import sys

from argparse import ArgumentParser
from time import gmtime, strftime

def main():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("--baudrate", type=int, help="px4 port baud rate", default=57600)
	parser.add_argument("--device", help="px4 device", default="/dev/ttyS0")
	parser.add_argument("--simulateVehicle", help="simulate vehicle", default=False)
	parser.add_argument("--testPulse", help="test PulseDetector", default=False)
	parser.add_argument("--log", help="log output", default=False)
	args = parser.parse_args()

	if args.log:
		timeStr = strftime("%mm_%dd_%Hh_%Mm_%Ss", gmtime())
		fErr = open('/home/pi/logs/err.log.' + timeStr, 'w')
		sys.stderr = fErr 
		fOut = open('/home/pi/logs/out.log.' + timeStr, 'w')
		sys.stdout = fOut

	tools = Tools.Tools()
	tools.mavlinkThread = MavlinkThread.MavlinkThread(tools, args)
	tools.vehicle = Vehicle.Vehicle(tools)
	tools.directionFinder = DirectionFinder.DirectionFinder(tools)
	pulseSender = PulseSender.PulseSender(tools)

	tools.mavlinkThread.start()
	pulseDetector = PulseDetector.PulseDetector(tools.pulseQueue)
	pulseDetector.start()

if __name__ == '__main__':
    main()