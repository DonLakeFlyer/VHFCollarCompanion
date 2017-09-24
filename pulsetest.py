import PulseDetector

from multiprocessing import Queue

def main():
	print("main")
	pulseQueue = Queue()
	pulseDetector = PulseDetector.PulseDetector(pulseQueue)
	pulseDetector.start()
	while True:
		pulseStrength = pulseQueue.get(True)
		print("PulseSender.pulse", pulseStrength)

if __name__ == '__main__':
    main()