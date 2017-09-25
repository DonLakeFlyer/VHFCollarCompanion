import PulseDetector
import logging

from multiprocessing import Queue
from argparse import ArgumentParser
from time import localtime, strftime

def main():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("--logdir", help="log directory", default="")
	args = parser.parse_args()

	timeStr = strftime("%mm_%dd_%Hh_%Mm_%Ss", localtime())
	logFormat = '%(asctime)s - (%(module)s:%(lineno)d) %(message)s'
	if args.logdir:
		logfile = args.logdir + "/" + "collar.log." + timeStr
		logging.basicConfig(filename=logfile, 
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