import threading
import math

from pymavlink import mavutil

class MavlinkThread (threading.Thread):
	exitFlag = False

	def __init__(self, device, baudrate, mavlinkSystemId):
		threading.Thread.__init__(self)
		self.device = device
		self.baudrate = baudrate
		self.systemId = mavlinkSystemId
		self.headingWait = float('nan')

	def run(self):
		self.mavlink = mavutil.mavlink_connection(self.device, baud=self.baudrate, source_system=self.systemId)
		self.wait_heartbeat()
		while True:
			if self.exitFlag:
				break
			self.wait_command()

	def wait_heartbeat(self):
	    print("Waiting for heartbeat")
	    msg = self.mavlink.recv_match(type='HEARTBEAT', blocking=True)
	    self.targetSystemId = self.mavlink.target_system
	    self.targetComponentId = self.mavlink.target_component
	    print("Heartbeat from (system %u component %u)" % (self.mavlink.target_system, self.mavlink.target_component))

	def wait_command(self):
	    msg = self.mavlink.recv_match(type=['VFR_HUD' , 'COMMAND_LONG', 'COMMAND_ACK', 'STATUSTEXT'], blocking=True)
	    if msg.get_type() == 'VFR_HUD':
	    	self.checkCurrentHeading(msg.heading)
	    elif msg.get_type() == 'COMMAND_LONG' and msg.command == mavutil.mavlink.MAV_CMD_USER_1:
	    	print("command:", " %3u" % (msg.command))
	    	self.changeVehicleHeading(0)
	    elif msg.get_type() == 'COMMAND_ACK':
	    	print("COMMAND_ACK:", msg.command, msg.result)
	    	self.mavlink.mav.command_ack_send(msg.command, mavutil.mavlink.MAV_RESULT_ACCEPTED) 
	    elif msg.get_type() == 'STATUSTEXT':
	    	print("STATUSTEXT:", msg.text)

	def checkCurrentHeading(self, heading):
		#print("heading", heading, "headingWait", self.headingWait)
		if self.fuzzyHeadingCompare(heading, self.headingWait):
			print("Heading change complete", self.headingWait)
			lastHeading = self.headingWait
			self.headingWait = float('nan')
			headingIncrement = 360.0 / 16.0
			newHeading = lastHeading + headingIncrement
			if newHeading != 0:
				t = threading.Timer(3.0, self.changeVehicleHeading, [newHeading])
				t.start()

	def fuzzyHeadingCompare(self, heading1, heading2):
		print(heading1, heading2)
		if heading1 <= 1 and heading2 >= 359 or heading2 <= 1 and heading1 >= 359:
			return True
		if abs(heading1 - heading2) < 1.0:
			return True
		else:
			return False

	def changeVehicleHeading(self, heading):
		print("change heading", heading)
		self.headingWait = heading
		self.mavlink.mav.command_long_send(self.targetSystemId, 
	    									self.targetComponentId,
            	                      		mavutil.mavlink.MAV_CMD_DO_REPOSITION,
                	                  		0,														# first transmission
                    	              		-1,														# no change in ground speed
                        	          		0,#mavutil.mavlink.MAV_DO_REPOSITION_FLAGS_CHANGE_MODE,	# reposition flags not used
                            	      		0,														# reserved
                                	  		math.radians(heading),									# change heading
                                  			float('nan'), float('nan'), float('NaN'))				# no change lat, lon, alt

