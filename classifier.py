import numpy as np
import math

i_d = 0
i_u = 1
i_pbd = 2
i_pbu = 3
i_b = 4
i_ibt = 5

class Classifier:

	def __init__(self, label):
		self.label = label
		self.inter_burst_times = np.array([])
		self.num_burst = np.array([])
		self.per_burst_dn = np.array([])
		self.per_burst_up = np.array([])
		self.tot_cells_dn = np.array([])
		self.tot_cells_up = np.array([])


	def euclidianDist(self, dn_0, up_0, dn_1, up_1):
		return math.sqrt( (dn_0 - dn_1)**2 + (up_0 - up_1)**2 )

	def trainIBT(self, ibt):
		self.inter_burst_times = np.append(self.inter_burst_times, ibt)

	def trainNumBursts(self, b):
		self.num_burst = np.append(self.num_burst, b)

	def trainPerBurst(self, dn, up):
		self.per_burst_dn = np.append(self.per_burst_dn, dn)
		self.per_burst_up = np.append(self.per_burst_up, up)

	def trainTotalCells(self, dn, up):
		self.tot_cells_dn = np.append(self.tot_cells_dn, dn)
		self.tot_cells_up = np.append(self.tot_cells_up, up)

	def train(self, metrics):
		# Average inter-burst time
		self.trainIBT(metrics[i_ibt])
		# Number of bursts
		self.trainNumBursts(metrics[i_b])
		# Number of cells per burst
		self.trainPerBurst(metrics[i_pbd], metrics[i_pbu])
		# Total number of cells
		self.trainTotalCells(metrics[i_d], metrics[i_u])

	def IBTVote(self, ibt, p):
		std = np.std(self.inter_burst_times)
		mean = np.mean(self.inter_burst_times)

		dist = abs(ibt - mean)
		perfect_match = dist == 0 and std == 0
		limit = 4.0

		if perfect_match:
			print "IBT PF", p
			return 4.0
		elif dist <= limit:
			return 1.0
		else:
			return -1.0

		#if std > mean/3:
		#	return 0.0
		#elif dist > 2*mean:
		#	return -1.0
		#elif dist == 0 and std == 0:
		#	return 4.0 # Perfect score
		#else:
		#	v = (1-dist)/1
		#	return v if v >= -0.9 else -0.9

	def numBurstsVote(self, b, p):
		std = np.std(self.num_burst)
		mean = np.mean(self.num_burst)

		dist = abs(b - mean)
		perfect_match = dist <= 0.5 and std <= 0.5
		limit = 2.0

		if perfect_match:
			print "Numburst PF", p
			return 4.0
		elif dist <= limit:
			return 1.0
		else:
			return -1.0
		
		#if std > mean/3:
		#	return 0.0
		#elif dist > mean/2:
		#	return -1.0
		#else:
		#	v = (5-dist)/5
		#	return v if v >= -0.9 else -0.9

	def perBurstRatioVote(self, ratio, p):
		ratios = self.per_burst_dn/self.per_burst_up
		mean = np.mean(ratios)

		dist = abs(ratio - mean)
		limit = mean/3.5

		if dist <= limit:
			return 1.0
		else:
			return -1.0

		#if dist > mean/3.5: # TODO: Higher? All models improved except vimeo
		#	if p:
		#		print self.label, "Negative ratio score", p
		#	return -1.0
		#else:
		#	v = (1-dist)
		#	return v

	def totalRatioVote(self, ratio, p):
		ratios = self.tot_cells_dn/self.tot_cells_up
		mean = np.mean(ratios)

		dist = abs(ratio - mean)
		limit = mean/1.8

		if dist <= limit:
			return 1.0
		else:
			return -1.0
		#if dist > mean/2:
		#	return -1.0
		#else:
		#	v = (1-dist)
		#	return v

	def perBurstDistance(self, metrics):
		mean_dn = np.mean(self.per_burst_dn)
		mean_up = np.mean(self.per_burst_up)
		dn = metrics[i_pbd]
		up = metrics[i_pbu]
		return self.euclidianDist(dn, up, mean_dn, mean_up)

	def totalDistance(self, metrics):
		mean_dn = np.mean(self.tot_cells_dn)
		mean_up = np.mean(self.tot_cells_up)
		dn = metrics[i_d]
		up = metrics[i_u]
		return self.euclidianDist(dn, up, mean_dn, mean_up)

	# For each metric or metric-pair, calculate a vote in the range [-1, 4] 
	# depending on how well the supplied metric correlates weighted on the standard deviation of the training metrics
	def predict(self, metrics, c):
		p = c == self.label
		vote = 0.0
		# Average inter-burst time
		vote += self.IBTVote(metrics[i_ibt], p)
		# Number of bursts
		vote += self.numBurstsVote(metrics[i_b], p)
		# Cells per burst ratio
		vote += self.perBurstRatioVote(metrics[i_pbd]/float(metrics[i_pbu]), p)
		vote += self.totalRatioVote(metrics[i_d]/metrics[i_u], p)
		return vote