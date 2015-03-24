class TorCell:
	ul = 0
	ts = -1

	def __init__(self, on_uplink, timestamp):
		self.ul = on_uplink
		self.ts = timestamp