import logging

import Vehicle

from threading import Timer

class DirectionFinder:
	exitFlag = False

	def __init__(self, tools):
		self.tools = tools
		self.cancelCommand = False
		self.pulseCount = 0
		self.rgPulse = []

	def cancel(self):
		self.cancelCommand = True

	# Find the strongest pulse heading
	def findStrongestHeading(self):
		logging.debug("findStrongestHeading")
		# Start direction finding passes
		# 	Phase 1: Four corner pulse capture
		#	Phase 2: Bisect strongest sector
		self.cancelCommand = False
		# Set up for four corner pulse capture
		nextHeading = self.tools.vehicle.heading
		self.fourCornerHeadings = [ nextHeading ]
		for i in range(0,3):
			nextHeading = self.constrainHeading(nextHeading + 90)
			self.fourCornerHeadings.append(nextHeading)
		self.fourCornerPulses = []
		self.fourCornerCurrentCorner = 0
		self.startPulseCapture(self.fourCornerPulseCallback)

	def startPulseCapture(self, pulseCallback):
		self.pulseCount = 0
		self.rgPulse = []
		self.tools.pulseSender.pulseCallback = pulseCallback

	# Called when the vehicle completes a heading change during four corner capture
	def fourCornerHeadingComplete(self):
		logging.debug("fourCornerHeadingComplete %d", self.tools.vehicle.heading)
		self.startPulseCapture(self.fourCornerPulseCallback)

	# Called when a new pulse is available. Collects 3 pulses and returns strongest of the three.
	# Returns:
	#	-1 - More pulses to capture
	#	Strongest pulse strength captured
	def handlePulse(self, pulseStrength):
		self.pulseCount += 1
		self.rgPulse.append(pulseStrength)
		logging.debug("handlePulse heading:strength:pulseCount %d:%d:%d", self.tools.vehicle.heading, pulseStrength, self.pulseCount)
		if self.pulseCount == 3:
			return max(self.rgPulse)
		else:
			return -1

	# Called when a pulse is received during Four Corners capture
	def fourCornerPulseCallback(self, pulseStrength):
		logging.debug("fourCornerPulseCallback %d", pulseStrength)
		pulse = self.handlePulse(pulseStrength)
		if pulse == -1:
			# Still waiting for more pulses
			self.tools.pulseSender.pulseCallback = self.fourCornerPulseCallback
		else:
			logging.debug("corner capture complete index:heading:pulse %d:%d:%d", self.fourCornerCurrentCorner, self.tools.vehicle.heading, pulse)
			self.fourCornerPulses.append(pulse)
			self.fourCornerCurrentCorner += 1
			if self.fourCornerCurrentCorner > 3:
				# All four corners captured
				self.startBisect()
			else:
				# More corners to capture
				self.tools.vehicle.changeHeading(self.fourCornerHeadings[self.fourCornerCurrentCorner], self.fourCornerHeadingComplete)

	def startBisect(self):
		# Determine which corner is the strongest
		bestAverage = -1
		bestIndex = -1
		for i in range(0,4):
			if i == 3:
				nextIndex = 0
			else:
				nextIndex = i + 1
			average = (self.fourCornerPulses[i] + self.fourCornerPulses[nextIndex]) / 2.0
			if average > bestAverage:
				bestAverage = average
				rgHeadings = [ self.fourCornerHeadings[i], self.fourCornerHeadings[nextIndex] ]
				bestIndex = i
		print(rgHeadings)
		self.bisect(rgHeadings[0], rgHeadings[1])

	def bisect(self, heading1, heading2):
		if heading2 < heading1:
			heading2 += 360
		headingRange = heading2 - heading1
		headingIncrement = headingRange / 2
		newHeading = heading1 + headingIncrement
		self.tools.vehicle.changeHeading(newHeading, self.bisectHeadingComplete)

	def bisectHeadingComplete(self):
		pass

	def constrainHeading(self, heading):
		if heading >= 360:
			return heading - 360
		elif heading < 0:
			return heading + 360
		else:
			return heading
