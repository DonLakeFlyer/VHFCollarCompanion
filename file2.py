from matplotlib.mlab import magnitude_spectrum
from rtlsdr import RtlSdr

def main():
    sdr = RtlSdr()

    # some defaults
    sdr.rs = 2.4e6
    sdr.fc = 146e6
    sdr.gain = 50

    noiseWindowLength = 20
    noiseWindow = [ ]

    rampWindowLength = 5
    rampWindow = [ ]
    rampPercent = 1.2

    backgroundNoise = False
    pulseFound = False

    results = [ ]

    # Loop enough times to collect 3 seconds of data
    sampleLoops = int(sdr.rs * 3 / 1024)

    for i in range(0, sampleLoops):
        samples = sdr.read_samples(1024)
        curMag, freqs = magnitude_spectrum(samples, Fs=sdr.rs)
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
                else:
                    pulseFound = False

        results.append([ maxSignal, backgroundNoise, pulseFound])

    sdr.close()

    f = open("data.csv", "w")
    for result in results:
        f.write(str(result[0]))
        f.write(",")
        f.write(str(result[1]))
        f.write(",")
        f.write(str(result[2]))
        f.write("\n")
    f.close()

if __name__ == '__main__':
    main()
