from matplotlib.mlab import magnitude_spectrum
from rtlsdr import RtlSdr

def main():
    sdr = RtlSdr()

    # some defaults
    sdr.rs = 2.4e6
    sdr.fc = 146e6
    sdr.gain = 10

    noiseWindowLength = 20
    noiseWindow = [ ]

    rampWindowLength = 5
    rampWindow = [ ]
    rampPercent = 1.2

    backgroundNoise = False
    pulseFound = False

    sampleCount = int(sdr.rs * 3 / 1024)

    f = open("data.csv", "w")

    for i in range(0, sampleCount):
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

        f.write(str(maxSignal))
        f.write(",")
        f.write(str(backgroundNoise))
        f.write(",")
        f.write(str(pulseFound))
        f.write("\n")

    f.close()

    # cleanup
    sdr.close()


if __name__ == '__main__':
    main()
