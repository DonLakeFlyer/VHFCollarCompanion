import threading
import logging
import bluetooth
import gobject

from bluetooth import *

class PulseSender (threading.Thread):
	def __init__(self, pulseQueue):
		threading.Thread.__init__(self)
		logging.debug("PulseSender init")
		self.pulseQueue = pulseQueue

		# Setup bluetooth socket
		self.serverSocket = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
		self.serverSocket.bind(("", 0x1001))
		self.serverSocket.listen(1)

		# Advertise service
		uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
		bluetooth.advertise_service(
				self.serverSocket,
				"PulseServer",
				service_id = uuid,
				service_classes = [ uuid, SERIAL_PORT_CLASS ],
				profiles = [ SERIAL_PORT_PROFILE ])
		logging.debug("Waiting for bluetooth connection")
		self.clientSocket, clientInfo = self.serverSocket.accept()
		print("Accepted connection from ", clientInfo)

	def run(self):
		while True:
			pulseInfo = self.pulseQueue.get(True)
			deviceIndex, pulseStrength = pulseInfo
			logging.debug("pulse (index,strength) (%d, %d) ", deviceIndex, pulseStrength)
			if deviceIndex == 0:
				pulseStr = "left " + str(pulseStrength) + "\n"
			else:
				pulseStr = "right " + str(pulseStrength) + "\n"
			logging.debug("pulseStr %s", pulseStr)
			self.clientSocket.send(pulseStr)

	def incomingConnection(self, source, condition):
		sock, info = self.serverSocket.accept()
		address, psm = info
		logging.debug("Accepted connection from %s", str(address))
		return True
