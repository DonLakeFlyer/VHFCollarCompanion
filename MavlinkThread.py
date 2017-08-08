import threading
from pymavlink import mavutil

class MavlinkThread (threading.Thread):
	exitFlag = False

	def __init__(self, device, baudrate, mavlinkSystemId):
		threading.Thread.__init__(self)
		self.device = devtakes 1 positional argument but 2 were givenice
		self.baudrate = baudrate
		self.systemId = mavlinkSystemId

	def run(self):
		mavlink = mavutil.mavlink_connection(self.device, baud=self.baudrate, source_system=self.systemId)
		self.wait_heartbeat(mavlink)
		while True:
			if self.exitFlag:
				break
			self.wait_heading(mavlink)

	def wait_heartbeat(self, m):
	    print("Waiting for heartbeat")
	    msg = m.recv_match(type='HEARTBEAT', blocking=True)
	    self.targetSystem = m.target_system
	    self.targetComponent = m.target_component
	    print("Heartbeat from (system %u component %u)" % (m.target_system, m.target_component))

	def wait_heading(self, m):
	    msg = m.recv_match(type='VFR_HUD', blocking=True)
	    print("heading: %3u" % (msg.heading))