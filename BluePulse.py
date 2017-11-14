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
	parser.add_argument("--freq", type=int, default="146000000")
	parser.add_argument("--gain", type=int, default="1")
	parser.add_argument("--amp", default=False)
	args = parser.parse_args()

	CollarLogging.setupLogging(args.logdir)

	tools = Tools.Tools()
	pulseQueue = None

	tools.pulseSender = PulseSender.PulseSender(tools.pulseQueue)
	tools.pulseSender.start()

	pulseDetectorLeft = PulseDetector.PulseDetector(0, tools.pulseQueue, args.freq, args.gain, args.amp)
	pulseDetectorLeft.start()
	pulseDetectorRight = PulseDetector.PulseDetector(1, tools.pulseQueue, args.freq, args.gain, args.amp)
	pulseDetectorRight.start()

if __name__ == '__main__':
    main()
