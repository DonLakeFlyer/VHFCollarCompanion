import PulseDetector

from argparse import ArgumentParser

def main():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("--simulateVehicle", help="simulate signal", default=False)
	parser.add_argument("--testPulse", help="test PulseDetector", default=True)
	args = parser.parse_args()
	pulseDetector = PulseDetector.PulseDetector(args)
	pulseDetector.run()

if __name__ == '__main__':
    main()

