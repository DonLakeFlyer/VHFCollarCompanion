import Tools
import PulseDetector
import PulseSender
import CollarLogging

import sys
import logging

from argparse import ArgumentParser
from time import gmtime, strftime

def main():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("--testPulse", help="Test pulses", default=False)
	parser.add_argument("--logdir", help="log directory", default="")
	parser.add_argument("--gain", type=int, default="60")
	parser.add_argument("--freq", type=int, default=146728000)
	args = parser.parse_args()

	CollarLogging.setupLogging(args.logdir)

	tools = Tools.Tools()
	pulseQueue = None
	if not args.testPulse:
		tools.pulseSender = PulseSender.PulseSender(tools)
		tools.pulseSender.start()
		pulseQueue = tools.pulseQueue

	pulseDetectorLeft = PulseDetector.PulseDetector(0, pulseQueue, tools.leftFreqQueue, tools.leftGainQueue, tools.leftAmpQueue)
	pulseDetectorLeft.start()
	pulseDetectorRight = PulseDetector.PulseDetector(1, pulseQueue, tools.rightFreqQueue, tools.rightGainQueue, tools.rightAmpQueue)
	pulseDetectorRight.start()

	tools.leftGainQueue.put(args.gain)
	tools.leftFreqQueue.put(args.freq)
	tools.rightGainQueue.put(args.gain)
	tools.rightFreqQueue.put(args.freq)

if __name__ == '__main__':
    main()
