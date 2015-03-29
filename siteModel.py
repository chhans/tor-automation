import numpy as np

i_d = 0
i_u = 1
i_pbd = 2
i_pbu = 3
i_b = 4
i_ibt = 5

class SiteModel:

	def __init__(self, label):
		self.label = label
		self.inter_burst_times = np.array([])
		self.num_burst = np.array([])
		self.per_burst_dn = np.array([])
		self.per_burst_up = np.array([])
		self.per_burst_ratio = np.array([])

	def trainIBT(self, ibt):
		self.inter_burst_times = np.append(self.inter_burst_times, ibt)

	def trainNumBursts(self, b):
		self.num_burst = np.append(self.num_burst, b)

	def trainPerBurst(self, dn, up):
		self.per_burst_dn = np.append(self.per_burst_dn, dn)
		self.per_burst_up = np.append(self.per_burst_up, up)
		self.per_burst_ratio = np.append(self.per_burst_ratio, dn/up)

	def train(self, metrics):
		# Average inter-burst time
		self.trainIBT(metrics[i_ibt])
		# Number of bursts
		self.trainNumBursts(metrics[i_b])
		# Number of cells per burst
		self.trainPerBurst(metrics[i_pbd], metrics[i_pbu])

	def IBTVote(self, ibt):
		std = np.std(self.inter_burst_times)
		mean = np.mean(self.inter_burst_times)

		dist = abs(ibt - mean)
		if std > mean/3:
			return 0.0
		elif dist > 2*mean:
			return -1.0
		else:
			v = (1-dist)/1
			return v if v >= -0.9 else -0.9

	def numBurstsVote(self, b):
		std = np.std(self.num_burst)
		mean = np.mean(self.num_burst)

		dist = abs(b - mean)
		if std > mean/3:
			return 0.0
		elif dist > mean/2:
			return -1.0
		else:
			v = (5-dist)/5
			return v if v >= -0.9 else -0.9

	def perBurstRatioVote(self, ratio):
		ratios = self.per_burst_dn/self.per_burst_up
		std = np.std(ratios)
		mean = np.mean(ratios)

		
		return 0
		#return abs(dn/float(up) - np.mean(self.per_burst_dn)/np.mean(self.per_burst_up))

	def perBurstVote(self, dn, up):
		return 0

	# For each metric or metric-pair, calculate a vote in the range [-1, 1] 
	# depending on how well the supplied metric correlates weighted on the standard deviation of the training metrics
	def predict(self, metrics):
		vote = 0.0
		# Average inter-burst time
		#vote += self.IBTVote(metrics[i_ibt])
		# Number of bursts
		#vote += self.numBurstsVote(metrics[i_b])
		# Cells per burst
		vote += self.perBurstRatioVote(metrics[i_pbd]/float(metrics[i_pbu]))
		#vote += self.perBurstVote(metrics[i_pbd], metrics[i_pbu])
		return vote