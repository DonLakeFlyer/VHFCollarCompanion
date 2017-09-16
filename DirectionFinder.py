import Vehicle

class DirectionFinder:
	exitFlag = False

	def __init__(self, mavlink, vehicle, sdr):
		self.mavlink = mavlink
		self.vehicle = vehicle
		self.sdr = sdr
		self.rgStrength = []
		self.cancelCommand = False

	def findDirection(self):
		self.rgStrength = []
		self.targetHeading = 0
		self.vehicle.changeHeading(self.targetHeading, self.headingChangeComplete)

	def headingChangeComplete(self):
		print("DirectionFinder heading change complete")
		self.sdr.beepCallback = self.beepCallback

	def beepCallback(self, beepStrength):
		print("DirectionFinder.beepCallback heading:strengh", self.targetHeading, beepStrength)
		self.rgStrength.append(beepStrength)
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

	def stopCapture(self):
		self.capturingValues = False

	def captureStrength(self):
		beepStrength = self.sdrThread.stopCapture()
		self.rgStrength.append(beepStrength)
		print("Signal strength", beepStrength)
		headingIncrement = 360.0 / 16.0
		newHeading = self.targetHeading + headingIncrement
		if newHeading == 360 or self.cancelCommand:
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
