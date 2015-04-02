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
		#std = np.std(ratios)
		mean = np.mean(ratios)

		dist = abs(ratio - mean)
		if dist > mean/3.5: # TODO: Higher? All models improved except vimeo
			return -1.0
		else:
			v = (1-dist)
			return v

	def totalRatioVote(self, ratio):
		ratios = self.tot_cells_dn/self.tot_cells_up
		mean = np.mean(ratios)

		dist = abs(ratio - mean)
		if dist > mean/2:
			return -1.0
		else:
			v = (1-dist)
			return v

#	def perBurstVote(self, dn, up):
#		mean_dn = np.mean(self.per_burst_dn)
#		mean_up = np.mean(self.per_burst_up)
#		mean_dist = np.mean(self.per_burst_dist)
#		std = np.std(self.per_burst_dist)
#
#
#		dist = self.euclidianDist(dn, up, mean_dn, mean_up)
#
#		#print self.label, mean_dn, mean_up, dist
#		return 5000-dist
#
#	def totalCellsVote(self, dn, up):
#		mean_dn = np.mean(self.tot_cells_dn)
#		mean_up = np.mean(self.tot_cells_up)
#
#		dist = self.euclidianDist(dn, up, mean_dn, mean_up)
#
#		return 5000-dist

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

	# For each metric or metric-pair, calculate a vote in the range [-1, 1] 
	# depending on how well the supplied metric correlates weighted on the standard deviation of the training metrics
	def predict(self, metrics):
		vote = 0.0
		# Average inter-burst time
		vote += self.IBTVote(metrics[i_ibt])
		# Number of bursts
		vote += self.numBurstsVote(metrics[i_b])
		# Cells per burst ratio
		vote += self.perBurstRatioVote(metrics[i_pbd]/float(metrics[i_pbu]))
		vote += self.totalRatioVote(metrics[i_d]/metrics[i_u])
		return vote