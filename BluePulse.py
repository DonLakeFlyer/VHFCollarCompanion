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
	args = parser.parse_args()

	CollarLogging.setupLogging(args.logdir)

	tools = Tools.Tools()

	tools.pulseSender = PulseSender.PulseSender(tools)
	tools.pulseSender.start()

	pulseDetectorLeft = PulseDetector.PulseDetector(0, tools.pulseQueue, tools.leftFreqQueue, tools.leftGainQueue, tools.leftAmpQueue)
	pulseDetectorLeft.start()
	pulseDetectorRight = PulseDetector.PulseDetector(1, tools.pulseQueue, tools.rightFreqQueue, tools.rightGainQueue, tools.rightAmpQueue)
	pulseDetectorRight.start()
	tools.leftGainQueue.put(2)

if __name__ == '__main__':
    main()
