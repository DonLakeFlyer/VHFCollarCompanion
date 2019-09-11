import sys
import serial

def main():
	port = serial.Serial("/dev/ttyS0", 57600, timeout=0, dsrdtr=False, rtscts=False, xonxoff=False)
	while True:
		b = serial.read()
		print(b)


if __name__ == '__main__':
    main()
