import Vehicle

from threading import Timer

class DirectionFinder:
	exitFlag = False

	def __init__(self, mavlink, vehicle, sdr):
		self.mavlink = mavlink
		self.vehicle = vehicle
		self.sdr = sdr
		self.rgStrength = []
		self.cancelCommand = False
		self.beepTimeoutTimer = None
		self.beepCount = 0
		self.rgBeeps = []

	def cancel(self):
		self.cancelCommand = True

	def findDirection(self):
		self.cancelCommand = False
		self.rgStrength = []
		self.beepCount = 0
		self.rgBeeps = []
		self.targetHeading = 0
		self.vehicle.changeHeading(self.targetHeading, self.headingChangeComplete)

	def headingChangeComplete(self):
		print("DirectionFinder heading change complete")
		if self.cancelCommand:
			return
		self.sdr.beepCallback = self.beepCallback
		self.beepTimeoutTimer = Timer(10, self.beepTimeout)
		self.beepTimeoutTimer.start()

	def beepCallback(self, beepStrength):
		self.beepCount += 1
		self.rgBeeps.append(beepStrength)
		print("DirectionFinder.beepCallback heading:strengh:beepCount", self.targetHeading, beepStrength, self.beepCount)
		#if self.cancelCommand:
		#	return
		if self.beepCount == 3:
			self.beepTimeoutTimer.cancel()
			self.rgStrength.append(max(self.rgBeeps))
			self.nextHeading()
		else:
			self.sdr.beepCallback = self.beepCallback

	def nextHeading(self):
		self.beepCount = 0
		self.rgBeeps = []
		headingIncrement = 360.0 / 16.0
		newHeading = self.targetHeading + headingIncrement
		if newHeading != 360 and not self.cancelCommand:
			self.targetHeading = newHeading
			self.vehicle.changeHeading(self.targetHeading, self.headingChangeComplete)
		elif newHeading == 360:
			# Capture complete, send values to ground station
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
			self.mavlink.sendMemoryVect(rgValues)


	def beepTimeout(self):
		# No beep heard
		print("DirectionFinder.beepTimeout beepCount", self.beepCount)
		self.sdr.beepCallback = None
		self.rgBeeps.append(0)
		self.rgStrength.append(max(self.rgBeeps))
		if self.cancelCommand:
			return
		self.nextHeading()

	def changeVehicleHeading(self, heading):
		print("change heading", heading)
		self.targetHeading = heading
		self.waitingForHeading = True
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

		

