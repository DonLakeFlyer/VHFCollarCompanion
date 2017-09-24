import threading
import math
import geo

import PulseDetector
import Vehicle
import DirectionFinder

from pymavlink import mavutil

class MavlinkThread (threading.Thread):
	exitFlag = False

	def __init__(self, tools, args):
		threading.Thread.__init__(self)
		self.tools = tools
		self.baudrate = args.baudrate
		self.simulateVehicle = args.simulateVehicle
		if self.simulateVehicle:
			self.device = "udp:localhost:14540"
		else:
			self.device = args.device
		self.targetSystemId = 1
		self.targetComponentId = 1
		self.capturingValues = False
		self.waitingForHeading = False
		self.cancelCommand = False
		self.sendMessageLock = threading.Lock()

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
	    print("Waiting for heartbeat from Vehicle autopilot component")
	    waiting = True
	    while waiting:
                    msg = self.mavlink.recv_match(type='HEARTBEAT', blocking=True)
                    if self.mavlink.target_component == 1:
                            print("Heartbeat from (system %u component %u mav_type %u)" % (self.mavlink.target_system, self.mavlink.target_component, msg.type))
                            self.targetSystemId = self.mavlink.target_system
                            self.targetComponentId = self.mavlink.target_component
                            waiting = False

	def wait_command(self):
		rgTypes = ['VFR_HUD' , 'COMMAND_LONG', 'COMMAND_ACK', 'STATUSTEXT', 'HOME_POSITION', 'GPS_RAW_INT', 'ATTITUDE']
		msg = self.mavlink.recv_match(type=rgTypes, blocking=True)
		self.tools.vehicle.mavlinkMessage(msg)
		if msg.get_type() == 'COMMAND_LONG':
			self.handleCommandLong(msg)
		elif msg.get_type() == 'COMMAND_ACK':
			print("COMMAND_ACK:", msg.command, msg.result)
		elif msg.get_type() == 'STATUSTEXT':
			print("STATUSTEXT:", msg.text)

	def handleCommandLong(self, msg):
		commandHandled = False
		commandAck = mavutil.mavlink.MAV_RESULT_FAILED
		if msg.command == mavutil.mavlink.MAV_CMD_USER_1:
			commandHandled = True
			self.tools.directionFinder.findDirection()
		elif msg.command == mavutil.mavlink.MAV_CMD_USER_2:
			commandHandled = True
			self.tools.directionFinder.cancel()
		if commandHandled:
			self.sendMessageLock.acquire()
			self.mavlink.mav.command_ack_send(msg.command, commandAck) 
			self.sendMessageLock.release()

	def sendDoReposition(self, heading):
		self.sendMessageLock.acquire()
		self.mavlink.mav.command_long_send(self.targetSystemId, 
	    									self.targetComponentId,
            	                      		mavutil.mavlink.MAV_CMD_DO_REPOSITION,
                	                  		0,														# first transmission
                    	              		-1,														# no change in ground speed
                        	          		mavutil.mavlink.MAV_DO_REPOSITION_FLAGS_CHANGE_MODE,	# reposition flags not used
                            	      		0,														# reserved
                                	  		math.radians(heading),									# change heading
                                  			float('nan'), float('nan'), float('NaN'))				# no change lat, lon, alt
		self.sendMessageLock.release()

	def sendMemoryVect(self, rgValues):
		print("sendMemoryVect", rgValues)
		self.sendMessageLock.acquire()
		self.mavlink.mav.memory_vect_send(0,		# address
										  1,		# ver
										  0,		# type
										  rgValues)	# values
		self.sendMessageLock.release()

	def sendPulseStrength(self, strength):
		self.tools.mavlinkThread.sendMessageLock.acquire()
		self.tools.mavlinkThread.mavlink.mav.debug_send(0, 0, strength)
		self.tools.mavlinkThread.sendMessageLock.release()