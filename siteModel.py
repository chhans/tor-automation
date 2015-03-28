class SiteModel:

	i_avg_ibt = 5

	inter_burst_times = []

	def __init__(self, label):
		self.label = label

	def train(self, metrics):
		# Average inter-burst times
		self.inter_burst_times.append(metrics[self.i_avg_ibt])
		print inter_burst_times