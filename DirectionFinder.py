import logging
import threading

import Vehicle

from threading import Timer

class DirectionFinder:
	exitFlag = False

	def __init__(self, tools):
		self.tools = tools
		self.cancelCommand = False
		self.pulseCount = 0
		self.rgPulse = []
		self.pulseCallback = None
#		self.simulationTimer = threading.Timer(2, self.testFound)
#		self.simulationTimer.start()

	def cancel(self):
		self.cancelCommand = True

	# Called when a new pulse comes through from PulseSender
	def pulse(self, pulseStrength):
		if self.pulseCallback:
			self.saveCallback = self.pulseCallback
			self.pulseCallback = None
			self.saveCallback(pulseStrength)

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
		self.pulseCallback = pulseCallback

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
			self.pulseCallback = self.fourCornerPulseCallback
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
		logging.debug("startBisect")
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
				rgPulses = [ self.fourCornerPulses[i], self.fourCornerPulses[nextIndex] ]
				bestIndex = i
				logging.debug("Best index %d", bestIndex)
		self.bisectCount = 0
		self.bisect(rgHeadings, rgPulses)

	def bisect(self, rgHeadings, rgPulses):
		if rgHeadings[1] < rgHeadings[0]:
			rgHeadings[1] += 360
		self.rgBisectHeadings = rgHeadings
		self.rgBisectPulses = rgPulses
		headingRange = rgHeadings[1] - rgHeadings[0]
		headingIncrement = headingRange / 2
		newHeading = rgHeadings[0] + headingIncrement
		logging.debug("bisect heading1:heading2:bisect %d:%d:%d", rgHeadings[0], rgHeadings[1], newHeading)
		self.tools.vehicle.changeHeading(newHeading, self.bisectHeadingComplete)

	def bisectHeadingComplete(self):
		self.startPulseCapture(self.bisectPulseCallback)

	# Called when a pulse is received during Four Corners capture
	def bisectPulseCallback(self, pulseStrength):
		vehicleHeading = self.tools.vehicle.heading
		logging.debug("bisectPulseCallback %d:%d", vehicleHeading, pulseStrength)
		pulse = self.handlePulse(pulseStrength)
		if pulse == -1:
			# Still waiting for more pulses
			self.pulseCallback = self.bisectPulseCallback
		else:
			self.bisectCount += 1
			logging.debug("bisect capture complete bisectCount:heading:pulse %d:%d:%d", self.bisectCount, vehicleHeading, pulse)
			logging.debug("bisect headings %d %d", self.rgBisectHeadings[0], self.rgBisectHeadings[1])
			if self.bisectCount <= 3:
				# Determine strongest sector
				average1 = (self.rgBisectPulses[0] + pulseStrength) / 2.0
				average2 = (self.rgBisectPulses[1] + pulseStrength) / 2.0
				if average1 > average2:
					self.bisect([ self.rgBisectHeadings[0], vehicleHeading ], [ self.rgBisectPulses[0], pulseStrength] )
				else:
					self.bisect([ vehicleHeading, self.rgBisectHeadings[1] ], [ pulseStrength, self.rgBisectPulses[1] ] )
			else:
				# Determine strongest heading from final bisect
				rgPulses = [ self.rgBisectPulses[0], self.rgBisectPulses[1], pulseStrength ]
				index = rgPulses.index(max(rgPulses))
				if index == 0:
					strongestPulse = self.rgBisectPulses[0]
					strongestHeading = self.rgBisectHeadings[0]
				elif index == 1:
					strongestPulse = self.rgBisectPulses[1]
					strongestHeading = self.rgBisectHeadings[1]
				else:
					strongestPulse = pulseStrength
					strongestHeading = vehicleHeading
				self.tools.vehicle.changeHeading(strongestHeading, None)
				logging.debug("Bisect complete heading:pulse %d:%d", strongestHeading, strongestPulse)
				self.tools.mavlinkThread.sendHeadingFound(strongestHeading, strongestPulse)

	def constrainHeading(self, heading):
		if heading >= 360:
			return heading - 360
		elif heading < 0:
			return heading + 360
		else:
			return heading

	def testFound(self):
		self.tools.mavlinkThread.sendHeadingFound(145, 500)
		self.simulationTimer = threading.Timer(2, self.testFound)
		self.simulationTimer.start()


