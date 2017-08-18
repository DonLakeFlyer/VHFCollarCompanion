import MavlinkThread
from argparse import ArgumentParser

def main():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("--baudrate", type=int, help="px4 port baud rate", default=115200)
	parser.add_argument("--device", required=True, help="px4 device")
	parser.add_argument("--source-system", dest='SOURCE_SYSTEM', type=int, default=255, help='MAVLink source system for this GCS')
	args = parser.parse_args()
	mavlinkThread = MavlinkThread.MavlinkThread(args.device, args.baudrate, 1)
	mavlinkThread.start()
	while True:
		continue

if __name__ == '__main__':
    main()

