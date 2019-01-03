import Tools
import MavlinkThread
import PulseCaptureUDP
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
	parser.add_argument("--sitl", help="sitl firmware", default=False)
	parser.add_argument("--simulatePulse", help="simulate pulses", default=False)
	parser.add_argument("--testPulse", help="Test pulses", default=False)
	parser.add_argument("--logDir", help="log directory", default="")
	parser.add_argument("--workDir", help="work directory", default="")
	parser.add_argument("--gain", type=int, default="21")
	parser.add_argument("--freq", type=int, default=146e6)
	args = parser.parse_args()

	CollarLogging.pruneLogs(args.logDir)
	CollarLogging.setupLogging(args.logDir)

	tools = Tools.Tools()
	tools.logDir = args.logDir
	tools.workDir = args.workDir
	if tools.logDir == "":
		tools.logDir = tools.pyDir
	if tools.workDir == "":
		tools.workDir = tools.pyDir
	pulseQueue = None
	if not args.testPulse:
		tools.mavlinkThread = MavlinkThread.MavlinkThread(tools, args)
		tools.vehicle = Vehicle.Vehicle(tools)
		tools.directionFinder = DirectionFinder.DirectionFinder(tools)
		tools.pulseSender = PulseSender.PulseSender(tools)
		tools.pulseSender.start()
		tools.mavlinkThread.start()
		pulseQueue = tools.pulseQueue

	if args.simulatePulse:
		pulseCapture = PulseDetectorSimulator.PulseDetectorSimulator(tools)
		pulseCapture.start()
	else:
		pulseCapture = PulseCaptureUDP.PulseCaptureUDP(tools)
		pulseCapture.start()

	tools.setGainQueue.put(args.gain)
	tools.setFreqQueue.put(args.freq)

if __name__ == '__main__':
    main()
