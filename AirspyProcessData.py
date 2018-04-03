import sys
import numpy as np
from matplotlib.mlab import magnitude_spectrum

def main():
	rawIntData = np.fromfile("/home/pi/logs/values.dat", dtype=np.dtype(np.int32))
	iqData = packed_bytes_to_iq(rawIntData)

	# We keep a rolling window of samples for background noise calculation
	noiseWindowLength = 20
	noiseWindow = [ ]

	# We keep a rolling to detect the ramping up of a pulse
	rampWindowLength = 5
	rampWindow = [ ]
	rampPercent = 1.2

	backgroundNoise = False
	pulseValues = [ ]
	minPulseLength = 3

	f = open("/home/pi/logs/pulse.dat", "w")

	readIndex = 0
	pulseFoundNotified = False
	while readIndex < len(iqData):
		samples = iqData[readIndex:readIndex+2048]
		readIndex += 2048
		curMag, freqs = magnitude_spectrum(samples, Fs=3000000)
		maxSignal = max(curMag)

		noiseWindow.append(maxSignal)
		if len(noiseWindow) > noiseWindowLength:
			noiseWindow.pop(0)
			# Background noise is the average of the current noise sample window
			backgroundNoise = sum(noiseWindow) / noiseWindowLength
			rampWindow.append(backgroundNoise)

			if len(rampWindow) > rampWindowLength:
				rampWindow.pop(0)

				# Check the last value in the ramp window to the first
				if rampWindow[rampWindowLength - 1] > rampWindow[0] * rampPercent:
					if len(pulseValues) == 0:
						# Leading edge of possible pulse
						pulseValues = [ maxSignal ]
					else:
						pulseValues.append(maxSignal)
				else:
					pulseLength = len(pulseValues)
					if pulseLength != 0:
						if pulseLength >= minPulseLength:							
							pulseAverage = sum(pulseValues) / pulseLength
							print("True pulse detected pulseAverage:length:backgroundNoise")
							print(pulseAverage, pulseLength, backgroundNoise)
							f.write(str(pulseAverage))
							f.write(",")
							f.write(str(backgroundNoise))
							f.write(",")
							f.write(str(pulseLength))
							f.write("\n")
						else:
							print("False pulse length", pulseLength)
						pulseValues = [ ]

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
