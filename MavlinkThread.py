import threading
import math
import logging
import subprocess

import Vehicle
import DirectionFinder

from pymavlink import mavutil

DEBUG_TS_COMMAND_ACK = 			0
DEBUG_INDEX_COMMAND_ACK_START =	0
DEBUG_INDEX_COMMAND_ACK_STOP =	1

DEBUG_TS_PULSE = 	1
DEBUG_INDEX_PULSE =	0

# param1 frequency
COMMAND_START_CAPTURE = mavutil.mavlink.MAV_CMD_USER_1

COMMAND_STOP_CAPTURE = mavutil.mavlink.MAV_CMD_USER_2

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
		rgTypes = ['VFR_HUD' , 'COMMAND_LONG', 'COMMAND_ACK', 'STATUSTEXT', 'HOME_POSITION', 'GPS_RAW_INT', 'ATTITUDE']
		msg = self.mavlink.recv_match(type=rgTypes, blocking=True)
		self.tools.vehicle.mavlinkMessage(msg)
		if msg.get_type() == 'COMMAND_LONG':
			self.handleCommandLong(msg)

	def handleCommandLong(self, msg):
		commandHandled = False
		commandAck = mavutil.mavlink.MAV_RESULT_FAILED
		if msg.command == COMMAND_START_CAPTURE:
			commandHandled = True
			self.handleStartCapture(msg)
		elif msg.command == COMMAND_STOP_CAPTURE:
			commandHandled = True
			self.handleStopCapture(msg)
		elif False: #msg.command == mavutil.mavlink.MAV_CMD_USER_2:
			# Set gain
			commandHandled = True
			gain = math.floor(msg.param1)
			logging.debug("Set gain %d", gain)
			self.tools.setGainQueue.put(gain)
		if commandHandled:
			self.sendMessageLock.acquire()
			#self.mavlink.mav.command_ack_send(msg.command, commandAck) 
			self.sendMessageLock.release()

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
		self.mavlink.mav.debug_send(DEBUG_TS_PULSE, DEBUG_INDEX_PULSE, strength)
		self.sendMessageLock.release()

	def handleStartCapture(self, msg):
		# New frequency is in param 1 as int ###### which reads as ###.###
		frequency = math.floor(msg.param1 * math.pow(10, 3))
		logging.debug("Start detect frequency %d", frequency)
		self.tools.setFreqQueue.put(frequency)
		try:
			self.pulseProcess = subprocess.Popen(["/usr/bin/python", "/home/pi/repos/VHFCollarCompanion/PulseDetectCmdLine.py", "--pulse-freq", str(frequency)])
		except:
			logging.debug("subprocess.Popen exception")
		if self.pulseProcess == None:
			logging.debug("Failed to start PulseDetectCmdLine.py")
		else:
			self.sendCommandAck(DEBUG_INDEX_COMMAND_ACK_START, msg.param1)

	def handleStopCapture(self, msg):
		if self.pulseProcess:
			self.pulseProcess.terminate()
			self.pulseProcess = None
			self.sendCommandAck(DEBUG_INDEX_COMMAND_ACK_STOP, 0)

	def sendCommandAck(self, command, value):
		self.sendMessageLock.acquire()
		self.mavlink.mav.debug_send(DEBUG_TS_COMMAND_ACK, command, value)
		self.sendMessageLock.release()
