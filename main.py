import Tools
import MavlinkThread
import PulseDetector
import Vehicle
import DirectionFinder

from argparse import ArgumentParser

def main():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("--baudrate", type=int, help="px4 port baud rate", default=57600)
	parser.add_argument("--device", help="px4 device", default="/dev/ttyS0")
	parser.add_argument("--simulateVehicle", help="simulate vehicle", default=False)
	parser.add_argument("--testPulse", help="test PulseDetector", default=False)
	args = parser.parse_args()

	tools = Tools.Tools()
	tools.mavlinkThread = MavlinkThread.MavlinkThread(tools, args)
	tools.pulseDetector = PulseDetector.PulseDetector(tools, args)
	tools.vehicle = Vehicle.Vehicle(tools)
	tools.directionFinder = DirectionFinder.DirectionFinder(tools)

	tools.mavlinkThread.start()
	tools.pulseDetector.run()

if __name__ == '__main__':
    main()