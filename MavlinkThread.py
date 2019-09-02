import threading
import math
import logging
import subprocess

import Vehicle

from pymavlink import mavutil

# Mavlink DEBUG_VECT messages are used to communicate with QGC in both directions.
# 	DEBUG_VECT.name is used to hold a command type
#	DEBUG_VECT.x/y/z are then command specific

# Pulse value
#	DEBUG_VECT.name = "PULSE"
#	DEBUG_VECT.x = pulse value
#	DEBUG_VECT.y - frequency
#	DEBUG_VECT.z - temp
DEBUG_COMMAND_ID_PULSE = "PULSE"

# Set gain
#	DEBUG_VECT.name = "GAIN"
#	DEBUG_VECT.x - new gain
DEBUG_COMMAND_ID_SET_GAIN = "SET-GAIN"

# Set frequency
#	DEBUG_VECT.name = "FREQ"
#	DEBUG_VECT.x - new frequency
DEBUG_COMMAND_ID_SET_FREQ = "SET-FREQ"

# Ack for SET commands
#	DEBUG_VECT.name = "CMD-ACK"
#	DEBUG_VECT.x - command being acked (DEBUG_COMMAND_ACK_SET_*)
#	DEBUG_VECT.y - gain/freq value which was changed to
DEBUG_COMMAND_ID_ACK = "CMD-ACK"
DEBUG_COMMAND_ACK_SET_GAIN =	0
DEBUG_COMMAND_ACK_SET_FREQ =	1

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
		rgTypes = ["DEBUG_VECT", "VFR_HUD", "HOME_POSITION", "GLOBAL_POSITION_INT"]
		msg = self.mavlink.recv_match(type=rgTypes, blocking=True)
		self.tools.vehicle.mavlinkMessage(msg)
		if msg.get_type() == 'DEBUG_VECT':
			#print("DEBUG_VECT", msg.name, msg.x, msg.y, msg.z)
			commandId = msg.name
			if commandId == DEBUG_COMMAND_ID_SET_GAIN:
				gain = int(msg.x)
				logging.debug("Set gain command received gain(%d)", gain)
				self.tools.setGainQueue.put(gain)
				self.sendMessageLock.acquire()
				self.mavlink.mav.debug_vect_send(DEBUG_COMMAND_ID_ACK, 0, DEBUG_COMMAND_ACK_SET_GAIN, gain, 0)
				self.sendMessageLock.release()
			elif commandId == DEBUG_COMMAND_ID_SET_FREQ:
				freq = int(msg.x)
				logging.debug("Set frequency command received freq(%d)", freq)
				self.tools.setFreqQueue.put(freq)
				self.sendMessageLock.acquire()
				self.mavlink.mav.debug_vect_send(DEBUG_COMMAND_ID_ACK, 0, DEBUG_COMMAND_ACK_SET_FREQ, freq, 0)
				self.sendMessageLock.release()

	def sendPulseStrength(self, strength, freq, temp):
		self.sendMessageLock.acquire()
		self.mavlink.mav.debug_vect_send(DEBUG_COMMAND_ID_PULSE, 0, strength, freq, temp)
		self.sendMessageLock.release()