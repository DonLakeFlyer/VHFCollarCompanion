import threading
import logging
import bluetooth
import gobject

from bluetooth import *

class PulseSender (threading.Thread):
	def __init__(self, tools):
		threading.Thread.__init__(self)
		logging.debug("PulseSender init")
		self.tools = tools

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
		self.clientSocket.setblocking(False)

	def run(self):
		while True:
			pulseInfo = self.tools.pulseQueue.get(True)
			deviceIndex, pulseStrength = pulseInfo
			logging.debug("pulse (index,strength) (%d, %d) ", deviceIndex, pulseStrength)
			if deviceIndex == 0:
				pulseStr = "left " + str(pulseStrength) + "\n"
			else:
				pulseStr = "right " + str(pulseStrength) + "\n"
			self.clientSocket.send(pulseStr)
			try:
				data = self.clientSocket.recv(1024)
				if (len(data)):
					self.incomingData(str(data))
			except Exception as e:
				pass

	def incomingConnection(self, source, condition):
		sock, info = self.serverSocket.accept()
		address, psm = info
		logging.debug("Accepted connection from %s", str(address))
		return True

	def incomingData(self, commandStr):
		logging.debug("Incoming command %s", commandStr)
		command, value = commandStr.split(" ")
		value = int(value)
		logging.debug("split %s %d", command, value)
		if command == "gain":
			self.tools.leftGainQueue.put(value)
			self.tools.rightGainQueue.put(value)
		elif command == "freq":
			logging.debug("Add to freq queue %d", value)
			self.tools.leftFreqQueue.put(value)
			self.tools.rightFreqQueue.put(value)
		elif command == "amp":
			if value == 1:
				value = True
			else:
				value = False
			self.tools.leftAmpQueue.put(value)
			self.tools.rightAmpQueue.put(value)
