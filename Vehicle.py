import geo

from pymavlink import mavutil

class Vehicle:
	def __init__(self):
		self.heading = float('NaN')
		self.position = geo.xyz(0, 0)
		self.homePositionSet = False
		self.homePosition = geo.xyz(0, 0)

	def mavlinkMessage(self, msg):
		if msg.get_type() == 'VFR_HUD':
			self.heading = msg.heading
		elif msg.get_type() == 'GPS_RAW_INT' and msg.fix_type == mavutil.mavlink.GPS_FIX_TYPE_3D_FIX:
			self.position = geo.xyz(msg.lat / 1E7, msg.lon / 1E7)
		elif msg.get_type() == 'HOME_POSITION':
			self.homePositionSet = True
			self.homePosition = geo.xyz(msg.latitude / 1E7, msg.longitude / 1E7)
