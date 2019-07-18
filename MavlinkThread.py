import threading
import math
import logging
import subprocess

import Vehicle

from pymavlink import mavutil

# Mavlink DEBUG_VECT messages are used to communicate with QGC in both directions.
# 	DEBUG_VECT.x is used to hold a command id
#	DEBUG.y/z are then command specific

# Pulse value
#	DEBUG.y = pulse value
#	DEBUG.z - frequence
DEBUG_COMMAND_ID_PULSE = 	0

# Set gain
#	DEBUG.y - new gain
#	DEBUG.z = not used
DEBUG_COMMAND_ID_SET_GAIN = 1

# Set frequency
#	DEBUG.y - new frequency
#	DEBUG.z = not used
DEBUG_COMMAND_ID_SET_FREQ = 2

# Ack for SET commands
#	DEBUG.y - command being acked
#	DEBUG.z - gain/freq value which was chaned to
DEBUG_COMMAND_ID_ACK = 				3
DEBUG_COMMAND_ACK_SET_GAIN_INDEX =	0
DEBUG_COMMAND_ACK_SET_FREQ_INDEX =	1

class MavlinkThread (threading.Thread):
	exitFlag = False

	def __init__(self, tools, args):
		threading.Thread.__init__(self)
		self.tools = tools
		self.baudrate = args.baudrate
		if args.sitl:
			self.device = "udp:localhost:14540"
		else:
			self.device = args.device
		self.targetSystemId = 1
		self.capturingValues = False
		self.waitingForHeading = False
		self.cancelCommand = False
		self.sendMessageLock = threading.Lock()
		self.pulseProcess = None

	def run(self):
		# Start a mavlink connectin to get the system id from the heartbeat
		self.mavlink = mavutil.mavlink_connection(self.device, baud=self.baudrate)
		self.wait_heartbeat()
		# Close initial connection and start new one with correct source_system id
		self.mavlink.close()
		self.mavlink = mavutil.mavlink_connection(self.device, baud=self.baudrate, source_system=self.targetSystemId)
		# We broadcast all our messages so they route through the firmware
		self.target_system = 0
		self.target_component = 0
		while True:
			if self.exitFlag:
				break
			self.wait_command()

	def wait_heartbeat(self):
		logging.debug("Waiting for heartbeat from Vehicle autopilot component")
		waiting = True
		while waiting:
			msg = self.mavlink.recv_match(type='HEARTBEAT', blocking=True)
			logging.debug("Heartbeat from (system %u component %u mav_type %u)" % (self.mavlink.target_system, self.mavlink.target_component, msg.type))
			self.targetSystemId = self.mavlink.target_system
			waiting = False

	def wait_command(self):
		rgTypes = ['DEBUG_VECT']
		msg = self.mavlink.recv_match(type=rgTypes, blocking=True)
		self.tools.vehicle.mavlinkMessage(msg)
		if msg.get_type() == 'DEBUG_VECT':
			print("DEBUG_VECT", msg.x, msg.y, msg.z)
			commandId = msg.x
			if commandId == DEBUG_COMMAND_ID_SET_GAIN:
				gain = int(msg.y)
				logging.debug("Set gain command received gain(%d)", gain)
				self.tools.setGainQueue.put(gain)
				self.sendMessageLock.acquire()
				self.mavlink.mav.debug_send(DEBUG_COMMAND_ID_ACK, DEBUG_COMMAND_ACK_SET_GAIN_INDEX, gain)
				self.sendMessageLock.release()
			elif commandId == DEBUG_COMMAND_ID_SET_FREQ:
				freq = int(msg.y)
				logging.debug("Set frequency command received freq(%d)", freq)
				self.tools.setFreqQueue.put(freq)
				self.sendMessageLock.acquire()
				self.mavlink.mav.debug_send(DEBUG_COMMAND_ID_ACK, DEBUG_COMMAND_ACK_SET_GAIN_INDEX, freq)
				self.sendMessageLock.release()

	def sendPulseStrength(self, strength, freq):
		self.sendMessageLock.acquire()
		print("MavlinkThread debug_send", strength)
		self.mavlink.mav.debug_vect_send("", 0, DEBUG_COMMAND_ID_PULSE, strength, freq)
		self.sendMessageLock.release()