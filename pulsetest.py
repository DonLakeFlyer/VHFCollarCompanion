import PulseDetector
import logging

from multiprocessing import Queue
from argparse import ArgumentParser

def main():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("--logfile", help="logfile output", default="")
	args = parser.parse_args()

	logFormat = '%(asctime)s - (%(module)s:%(lineno)d) %(message)s'
	if args.logfile:
		logging.basicConfig(filename=args.logfile, 
							filemode="w", level=logging.DEBUG, 
							format = logFormat)
	else:
		logging.basicConfig(level=logging.DEBUG,
							format = logFormat)

	pulseQueue = Queue()
	pulseDetector = PulseDetector.PulseDetector(pulseQueue)
	pulseDetector.start()
	while True:
		pulseStrength = pulseQueue.get(True)
		logging.debug("Pulse from Queue %d", pulseStrength)

if __name__ == '__main__':
    main()