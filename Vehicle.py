import geo
import math

from pymavlink import mavutil

class Vehicle:
	def __init__(self, tools):
		self.mavlink = tools.mavlinkThread
		self.heading = float('NaN')
		self.targetHeadingRadians = float('NaN')
		self.position = geo.xyz(0, 0)
		self.homePositionSet = False
		self.homePosition = geo.xyz(0, 0)

	def mavlinkMessage(self, msg):
		msgType = msg.get_type()
		if msgType == "VFR_HUD":
			self.handleVfrHud(msg)
		elif msgType == "GPS_RAW_INT":
			self.handleGpsRawInt(msg)
		elif msgType == "HOME_POSITION":
			self.handleHomePosition(msg)
		elif msgType == "ATTITUDE":
			self.handleAttitude(msg)

	def handleVfrHud(self, msg):
		self.heading = msg.heading

	def handleGpsRawInt(self, msg):
		if msg.fix_type == mavutil.mavlink.GPS_FIX_TYPE_3D_FIX:
			self.position = geo.xyz(msg.lat / 1E7, msg.lon / 1E7)

	def handleHomePosition(self, msg):
		self.homePositionSet = True
		self.homePosition = geo.xyz(msg.latitude / 1E7, msg.longitude / 1E7)

	def handleAttitude(self, msg):
		if not math.isnan(self.targetHeadingRadians):
			# We are waiting for the vehicle to reach a new target heading
			if abs(msg.yawspeed) < 0.1:
				# Vehicle has stopped yaw rate, possibly turning
				if msg.yaw < 0:
					positiveRadians = math.pi * 2 + msg.yaw
				else:
					positiveRadians = msg.yaw
				#print("Checking heading complete", msg.yawspeed, msg.yaw, positiveRadians, self.targetHeadingRadians)
				delta = 0.05
				if positiveRadians - delta < self.targetHeadingRadians and self.targetHeadingRadians < positiveRadians + delta:
					# Heading is within target
					self.targetHeadingRadians = float('NaN')
					if self.headingCompleteCallback:
						self.headingCompleteCallback()
					print("Vehicle completed turn")

	def changeHeading(self, newHeading, changeCompleteCallback):
		self.headingCompleteCallback = changeCompleteCallback
		self.mavlink.sendDoReposition(newHeading)
		self.targetHeadingRadians = math.radians(newHeading)
		print("Vehicle.changeHeading newHeading:radians", newHeading, self.targetHeadingRadians)
