import threading
import math

import SDRThread

from pymavlink import mavutil

class MavlinkThread (threading.Thread):
	exitFlag = False

	def __init__(self, device, baudrate, mavlinkSystemId):
		threading.Thread.__init__(self)
		self.device = device
		self.baudrate = baudrate
		self.systemId = mavlinkSystemId
		self.targetSystemId = 1
		self.targetComponentId = 1
		self.capturingValues = False
		self.waitingForHeading = False

	def run(self):
		self.sdrThread = SDRThread.SDRThread()
		self.sdrThread.start()
		self.mavlink = mavutil.mavlink_connection(self.device, baud=self.baudrate, source_system=self.systemId)
		self.wait_heartbeat()
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
	    msg = self.mavlink.recv_match(type=['VFR_HUD' , 'COMMAND_LONG', 'COMMAND_ACK', 'STATUSTEXT'], blocking=True)
	    if msg.get_type() == 'VFR_HUD':
	    	self.checkCurrentHeading(msg.heading)
	    elif msg.get_type() == 'COMMAND_LONG' and msg.command == mavutil.mavlink.MAV_CMD_USER_1:
	    	if self.capturingValues:
	    		print("Start capture: failed in progress")
	    		self.mavlink.mav.command_ack_send(mavutil.mavlink.MAV_CMD_USER_1, mavutil.mavlink.MAV_RESULT_FAILED) 
	    	else:
	    		print("Start capture")
	    		self.mavlink.mav.command_ack_send(mavutil.mavlink.MAV_CMD_USER_1, mavutil.mavlink.MAV_RESULT_ACCEPTED)
	    		self.startCapture()
	    elif msg.get_type() == 'COMMAND_ACK':
	    	print("COMMAND_ACK:", msg.command, msg.result)
	    elif msg.get_type() == 'STATUSTEXT':
	    	print("STATUSTEXT:", msg.text)

	def startCapture(self):
		self.capturingValues = True
		self.changeVehicleHeading(0)
		self.rgStrength = []

	def stopCapture(self):
		self.capturingValues = False
		print("Capture complete")
		print(self.rgStrength)
		rgNormalized = []
		maxStrength = max(self.rgStrength)
		for strength in self.rgStrength:
			rgNormalized.append(int(127.0 * (strength / maxStrength)))
		print(rgNormalized)
		rgZeroes = [0] * 16
		rgValues = rgNormalized + rgZeroes
		print("rgValues", rgValues)
		self.mavlink.mav.memory_vect_send(0,		# address
										1,			# ver
										0,			# type
										rgValues)	# values

	def captureStrength(self):
		beepStrength = self.sdrThread.stopCapture()
		self.rgStrength.append(beepStrength)
		print("Signal strength", beepStrength)
		headingIncrement = 360.0 / 16.0
		newHeading = self.targetHeading + headingIncrement
		if newHeading == 360:
			self.stopCapture()
		else:
			self.changeVehicleHeading(newHeading)

	def checkCurrentHeading(self, heading):
		if not self.waitingForHeading:
			return
		if self.fuzzyHeadingCompare(heading, self.targetHeading):
			print("Heading change complete", self.targetHeading)
			self.waitingForHeading = False
			self.sdrThread.startCapture()
			print("Waiting 10 seconds to capture data")
			t = threading.Timer(10.0, self.captureStrength)
			t.start()

	def fuzzyHeadingCompare(self, heading1, heading2):
		#print(heading1, heading2)
		if heading1 <= 1 and heading2 >= 359 or heading2 <= 1 and heading1 >= 359:
			return True
		if abs(heading1 - heading2) < 1.0:
			return True
		else:
			return False

	def changeVehicleHeading(self, heading):
		print("change heading", heading)
		self.targetHeading = heading
		self.waitingForHeading = True
		self.mavlink.mav.command_long_send(self.targetSystemId, 
	    									self.targetComponentId,
            	                      		mavutil.mavlink.MAV_CMD_DO_REPOSITION,
                	                  		0,														# first transmission
                    	              		-1,														# no change in ground speed
                        	          		mavutil.mavlink.MAV_DO_REPOSITION_FLAGS_CHANGE_MODE,	# reposition flags not used
                            	      		0,														# reserved
                                	  		math.radians(heading),									# change heading
                                  			float('nan'), float('nan'), float('NaN'))				# no change lat, lon, alt

