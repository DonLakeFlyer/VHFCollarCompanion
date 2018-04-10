import sys
import numpy as np
from matplotlib.mlab import magnitude_spectrum
from matplotlib.mlab import psd
from argparse import ArgumentParser
from scipy.signal import decimate

def main():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("--workDir", help="log directory", default=".")
	parser.add_argument("--noCSV", default=False)
	args = parser.parse_args()

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

	decimateFactor = 16
	sampleCountFFT = 2048
	sampleRate = 3000000

	rawIntData = np.fromfile(args.workDir + "/values.dat", dtype=np.dtype(np.int32))
	iqData = packed_bytes_to_iq(rawIntData)

	f = open(args.workDir + "/pulse.dat", "w")
	csvFile = None
	if not args.noCSV:
		csvFile = open(args.workDir + "/pulse.csv", "w")

	# First calculate on overall background noise for all the data	
	decimatedSamples = decimate(iqData, decimateFactor, ftype='fir')

	# Data close to start/stop seems to be crap
	stripCount = sampleCountFFT * 2
	readIndex = stripCount
#	lastIndex = len(iqData) - stripCount
	lastIndex = len(decimatedSamples) - stripCount

	pulseFoundNotified = False
	while readIndex < lastIndex:
		rampUpFound = False
#		samples = iqData[readIndex:readIndex + (sampleCountFFT * decimateFactor)]
#		samples = decimate(samples, decimateFactor, ftype='fir')
		samples = decimatedSamples[readIndex:readIndex + sampleCountFFT]
		readIndex += len(samples)
		curMag, freqs = psd(samples, Fs=sampleRate/decimateFactor)
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
					rampUpFound = True
					if len(pulseValues) == 0:
						# Leading edge of possible pulse
						pulseValues = [ maxSignal ]
					else:
						# In the middle of a possible pulse
						pulseValues.append(maxSignal)
				else:
					pulseLength = len(pulseValues)
					if pulseLength != 0:
						# We've fallen of the trailing edge of a possible pulse
						if pulseLength >= minPulseLength:							
							pulseMax = max(pulseValues)
							print("True pulse detected pulseMax:length:backgroundNoise")
							print(pulseMax, pulseLength, backgroundNoise)
							f.write(str(pulseMax))
							f.write(",")
							f.write(str(backgroundNoise))
							f.write(",")
							f.write(str(pulseLength))
							f.write("\n")
						else:
							print("False pulse length", pulseLength)
						pulseValues = [ ]

		if csvFile:
			csvFile.write(str(maxSignal))
			csvFile.write(",")
			csvFile.write(str(backgroundNoise))
			csvFile.write(",")
			csvFile.write(str(rampUpFound))
			csvFile.write("\n")

	f.close()
	if csvFile:
		csvFile.close()

def packed_bytes_to_iq(ints):
	# Assume int16 iq packing
    iq = np.empty(len(ints)//2, 'complex')
    iq.real, iq.imag = ints[::2], ints[1::2]
    iq /= (32768/2)
    iq -= (1 + 1j)
    return iq

if __name__ == '__main__':
    main()
