import threading

import SDRThread

from argparse import ArgumentParser

def main():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("--simulate", help="simulate signal", default=False)
	args = parser.parse_args()
	sdrThreadExitEvent = threading.Event()
	sdrThread = SDRThread.SDRThread(None, None, sdrThreadExitEvent, args.simulate)
	sdrThread.start()
	while True:
		continue

if __name__ == '__main__':
    main()

