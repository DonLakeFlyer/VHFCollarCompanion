import Tools
import PulseDetector
import PulseDetectorSimulator
import PulseSender
import CollarLogging

import sys
import logging

from argparse import ArgumentParser
from time import gmtime, strftime

def main():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("--logdir", help="log directory", default="")
	parser.add_argument("--testPulse", default=False)
	args = parser.parse_args()

	CollarLogging.setupLogging(args.logdir)

	tools = Tools.Tools()

	if not args.testPulse:
		tools.pulseSender = PulseSender.PulseSender(tools)
		tools.pulseSender.start()

	pulseDetectorLeft = PulseDetector.PulseDetector(0, args.testPulse, tools.pulseQueue, tools.leftFreqQueue, tools.leftGainQueue, tools.leftAmpQueue)
	pulseDetectorLeft.start()
	pulseDetectorRight = PulseDetector.PulseDetector(1, args.testPulse, tools.pulseQueue, tools.rightFreqQueue, tools.rightGainQueue, tools.rightAmpQueue)
	pulseDetectorRight.start()

if __name__ == '__main__':
    main()
