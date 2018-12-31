import threading
import math
import logging
import subprocess

import Vehicle
import DirectionFinder

from pymavlink import mavutil

# Mavlink DEBUG messages are used to communicate with QGC
# 	DEBUG.time_boot_msg is used to hold a command id
#	DEBUG.index/value are then command specific

# Ack for commands
#	DEBUG.index - command being acked
#	DEBUG.value - gain/freq value which was chaned to
DEBUG_COMMAND_ID_ACK = 				0
DEBUG_COMMAND_ACK_SET_GAIN_INDEX =	0
DEBUG_COMMAND_ACK_SET_FREQ_INDEX =	1

# Pulse value
#	DEBUG.index - not used
#	DEBUG.value = pulse value
DEBUG_COMMAND_ID_PULSE = 	1

# param1 frequency
COMMAND_SET_GAIN = mavutil.mavlink.MAV_CMD_USER_1
COMMAND_SET_FREQ = mavutil.mavlink.MAV_CMD_USER_2

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
		self.targetComponentId = 1
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
			if self.mavlink.target_component == 1:
				logging.debug("Heartbeat from (system %u component %u mav_type %u)" % (self.mavlink.target_system, self.mavlink.target_component, msg.type))
				self.targetSystemId = self.mavlink.target_system
				self.targetComponentId = self.mavlink.target_component
				waiting = False

	def wait_command(self):
		rgTypes = ['HEARTBEAT', 'VFR_HUD' , 'COMMAND_LONG', 'COMMAND_ACK', 'STATUSTEXT', 'HOME_POSITION', 'GPS_RAW_INT', 'ATTITUDE']
		msg = self.mavlink.recv_match(type=rgTypes, blocking=True)
		self.tools.vehicle.mavlinkMessage(msg)
		if msg.get_type() == 'HEARTBEAT':
			logging.debug("Heartbeat")	
		if msg.get_type() == 'COMMAND_LONG':
			logging.debug("COMMAND_LONG %d" % (msg.command))
			self.handleCommandLong(msg)

	def handleCommandLong(self, msg):
		commandHandled = False
		commandAck = mavutil.mavlink.MAV_RESULT_FAILED
		if msg.command == COMMAND_SET_GAIN:
			commandHandled = True
			gain = math.floor(msg.param1)
			logging.debug("Set gain command received gain(%d)", gain)
			self.tools.setGainQueue.put(gain)
			self.sendCommandAck(DEBUG_COMMAND_ACK_SET_GAIN_INDEX, gain)
		elif msg.command == COMMAND_SET_FREQ:
			commandHandled = True
			freq = math.floor(msg.param1)
			logging.debug("Set frequency command received freq(%d)", freq)
			self.tools.setFreqQueue.put(freq)
			self.sendCommandAck(DEBUG_COMMAND_ACK_SET_FREQ_INDEX, freq)

	def sendMemoryVect(self, rgValues):
		logging.debug("sendMemoryVect %s", string(rgValues))
		self.sendMessageLock.acquire()
		self.mavlink.mav.memory_vect_send(0,		# address
										  1,		# ver
										  0,		# type
										  rgValues)	# values
		self.sendMessageLock.release()

	def sendPulseStrength(self, strength):
		self.sendMessageLock.acquire()
		self.mavlink.mav.debug_send(DEBUG_COMMAND_ID_PULSE, 0, strength)
		self.sendMessageLock.release()

	def sendCommandAck(self, command, value):
		self.sendMessageLock.acquire()
		self.mavlink.mav.debug_send(DEBUG_COMMAND_ID_ACK, command, value)
		self.sendMessageLock.release()
