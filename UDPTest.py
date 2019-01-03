import socket
import struct
import math
import numpy
import time

def main():
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #udpSocket.bind(('localhost', 14540))
    udpSocket.bind(('localhost', 10000))
    #udpSocket.setblocking(False)

    while True:
        try:
            data = udpSocket.recv(1024)
        except Exception as e:
            print(e)
        else:
            print("data", len(data))

if __name__ == '__main__':
    main()
