import sys
import numpy as np
from matplotlib.mlab import magnitude_spectrum
from matplotlib.mlab import psd

def main():
	rawIntData = np.fromfile("values.dat", dtype=np.dtype(np.int32))
	iqData = packed_bytes_to_iq(rawIntData)

	noiseWindowLength = 20
	noiseWindow = [ ]

	rampWindowLength = 5
	rampWindow = [ ]
	rampPercent = 1.2

	backgroundNoise = False
	pulseFound = False

	f = open("data.csv", "w")

	readIndex = 0
	pulseFoundNotified = False
	while readIndex < len(iqData):
		samples = iqData[readIndex:readIndex+2048]
		readIndex += 2048
#		curMag, freqs = magnitude_spectrum(samples, Fs=3000000)
		curMag, freqs = psd(samples, Fs=3000000)
		maxSignal = max(curMag)

		noiseWindow.append(maxSignal)
		if len(noiseWindow) > noiseWindowLength:
			noiseWindow.pop(0)
			backgroundNoise = sum(noiseWindow) / noiseWindowLength
			rampWindow.append(backgroundNoise)

			if len(rampWindow) > rampWindowLength:
				rampWindow.pop(0)

				if rampWindow[rampWindowLength - 1] > rampWindow[0] * rampPercent:
					pulseFound = True
					if not pulseFoundNotified:
						pulseFoundNotified = True
						print("Pulse detected")
				else:
					pulseFound = False
					pulseFoundNotified = False

		f.write(str(maxSignal))
		f.write(",")
		f.write(str(backgroundNoise))
		f.write(",")
		f.write(str(pulseFound))
		f.write("\n")

	f.close()

def packed_bytes_to_iq(ints):
	# Assume int16 iq packing
    iq = np.empty(len(ints)//2, 'complex')
    iq.real, iq.imag = ints[::2], ints[1::2]
    iq /= (32768/2)
    iq -= (1 + 1j)
    return iq

if __name__ == '__main__':
    main()
