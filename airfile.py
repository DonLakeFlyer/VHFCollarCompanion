import sys
import numpy as np
from matplotlib.mlab import magnitude_spectrum

def main():
	floats = np.fromfile("values.dat", dtype=np.dtype(np.float32))
	iq = np.empty(len(floats)//2, 'complex')
	iq.real, iq.imag = floats[::2], floats[1::2]
	index = 0
	while index < len(iq):
		samples = iq[index:index+1024]
		#print(*samples)
		index += 1024 
		mag, freqs = magnitude_spectrum(samples, Fs=3000000)
		if max(mag) > 1:
			print(max(mag))

if __name__ == '__main__':
    main()
