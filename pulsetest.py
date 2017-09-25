import PulseDetector
import CollarLogging

import logging

from multiprocessing import Queue
from argparse import ArgumentParser
from time import localtime, strftime

def main():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("--logdir", help="log directory", default="")
	args = parser.parse_args()

	CollarLogging.setupLogging(args.logdir)

	pulseQueue = Queue()
	pulseDetector = PulseDetector.PulseDetector(pulseQueue)
	pulseDetector.start()
	while True:
		pulseStrength = pulseQueue.get(True)
		logging.debug("Pulse from Queue %d", pulseStrength)

if __name__ == '__main__':
    main()