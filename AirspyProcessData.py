import sys
import math
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
	processValuesFile(args.workDir, args.noCSV, 2)
	processValuesFile(args.workDir, args.noCSV, 4)
	processValuesFile(args.workDir, args.noCSV, 8)
	processValuesFile(args.workDir, args.noCSV, 16)
	processValuesFile(args.workDir, args.noCSV, 32)
	processValuesFile(args.workDir, args.noCSV, 64)

def processValuesFile(workDir, noCSV, decimateFactor):
	# We keep a rolling window of samples for background noise calculation
	noiseWindowLength = 5
	noiseWindow = [ ]

	# We keep a rolling to detect the ramping up of a pulse
	rampWindowLength = 5
	rampWindow = [ ]
	rampPercent = 1.2

	backgroundNoise = False
	pulseValues = [ ]
	minPulseLength = 3

	#decimateFactor = 16
	fftSize = 512

	sampleRate = 3000000
	decimatedSampleRate = sampleRate / decimateFactor
	decimatedSampleRatePerMsec = decimatedSampleRate / 1000

	pulseDurationMsecs = 15
	sampleCountPSD = int(math.ceil(pulseDurationMsecs * decimatedSampleRatePerMsec))
	secsPerPSDSample = sampleCountPSD * (1 / decimatedSampleRate)
	print("***decimateFactor", decimateFactor, "psd sample count", sampleCountPSD)

	#rawIntData = np.fromfile(workDir + "/values.dat", dtype=np.dtype(np.int32))
	#iqData = packed_bytes_int16_to_iq(rawIntData)

	iqData = np.fromfile(workDir + "/values.dat", dtype=np.dtype(np.complex64))

	f = open(workDir + "/pulse.dat", "w")
	csvFile = None
	if not noCSV:
		csvFile = open(workDir + "/pulse.csv", "w")

	# First calculate on overall background noise for all the data	
	decimatedSamples = decimate(iqData, decimateFactor, ftype='fir')

	# Data close to start/stop seems to be crap
	stripCount = 0
	readIndex = stripCount
#	lastIndex = len(iqData) - stripCount
	lastIndex = len(decimatedSamples) - stripCount

	pulseFoundNotified = False
	loopIndex = 1
	rgPulseTimes = [ ]
	while readIndex < lastIndex:
		rampUpFound = False
#		samples = iqData[readIndex:readIndex + (sampleCountFFT * decimateFactor)]
#		samples = decimate(samples, decimateFactor, ftype='fir')
		samples = decimatedSamples[readIndex:readIndex + sampleCountPSD]
		readIndex += len(samples)
		curMag, freqs = psd(samples, Fs=sampleRate/decimateFactor, NFFT=fftSize)
		#curMag = 10*np.log10(curMag)
		maxSignal = max(curMag)
		#print(maxSignal)

		noiseWindow.append(maxSignal)
		if len(noiseWindow) > noiseWindowLength:
			noiseWindow.pop(0)
			# Background noise is the average of the current noise sample window
			backgroundNoise = sum(noiseWindow) / noiseWindowLength

			# Check the last value in the ramp window to the first
			if maxSignal > backgroundNoise * 2:
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
					pulseMax = max(pulseValues)
					pulseTime = loopIndex*secsPerPSDSample
					rgPulseTimes.append(pulseTime)
					print("True pulse detected pulseMax:msecs:length:backgroundNoise")
					print(pulseMax, pulseTime, pulseLength, backgroundNoise)
					f.write(str(pulseMax))
					f.write(",")
					f.write(str(backgroundNoise))
					f.write(",")
					f.write(str(pulseLength))
					f.write("\n")
				pulseValues = [ ]

		if csvFile:
			csvFile.write(str(maxSignal))
			csvFile.write(",")
			csvFile.write(str(backgroundNoise))
			csvFile.write(",")
			csvFile.write(str(rampUpFound))
			csvFile.write("\n")

		loopIndex = loopIndex + 1


	f.close()
	if csvFile:
		csvFile.close()

	avgInterval = 0
	if len(rgPulseTimes) > 1:
		intervalSum = 0
		for i in range(0, len(rgPulseTimes)-1):
			intervalSum = intervalSum + (rgPulseTimes[i+1] - rgPulseTimes[i])
		avgInterval = intervalSum / (len(rgPulseTimes) - 1)

	print ("----pulse count", len(rgPulseTimes), "avg interval", avgInterval)

def packed_bytes_int16_to_iq(ints):
    iq = np.empty(len(ints)//2, 'complex')
    iq.real, iq.imag = ints[::2], ints[1::2]
    iq /= (32768/2)
    iq -= (1 + 1j)
    return iq

def packed_bytes_float32_to_iq(floats):
    iq = np.empty(len(ints)//2, 'complex')
    iq.real, iq.imag = floats[::4], floats[1::4]
    iq /= (32768/2)
    iq -= (1 + 1j)
    return iq

if __name__ == '__main__':
    main()
