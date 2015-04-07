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
		self.tot_distances = np.array([])
		self.per_burst_distances = np.array([])


	def euclidianDist(self, dn_0, up_0, dn_1, up_1):
		return math.sqrt( (dn_0 - dn_1)**2 + (up_0 - up_1)**2 )

	def trainIBT(self, ibt):
		self.inter_burst_times = np.append(self.inter_burst_times, ibt)

	def trainNumBursts(self, b):
		self.num_burst = np.append(self.num_burst, b)

	def trainPerBurstDistance(self):
		for i in range(len(self.per_burst_dn)-1):
			u0 = self.per_burst_up[-1]
			d0 = self.per_burst_dn[-1]
			u1 = self.per_burst_up[i]
			d1 = self.per_burst_dn[i]
			d = self.euclidianDist(d0, u0, d1, u1)
			self.per_burst_distances = np.append(self.per_burst_distances, d)

	def trainPerBurst(self, dn, up):
		self.per_burst_dn = np.append(self.per_burst_dn, dn)
		self.per_burst_up = np.append(self.per_burst_up, up)
		if len(self.per_burst_dn) > 1:
			self.trainPerBurstDistance()

	def trainTotalDistance(self):
		for i in range(len(self.tot_cells_dn)-1):
			u0 = self.tot_cells_up[-1]
			d0 = self.tot_cells_dn[-1]
			u1 = self.tot_cells_up[i]
			d1 = self.tot_cells_dn[i]
			d = self.euclidianDist(d0, u0, d1, u1)
			self.tot_distances = np.append(self.tot_distances, d)

	def trainTotalCells(self, dn, up):
		self.tot_cells_dn = np.append(self.tot_cells_dn, dn)
		self.tot_cells_up = np.append(self.tot_cells_up, up)
		if len(self.tot_cells_dn) > 1:
			self.trainTotalDistance()

	def train(self, metrics):
		# Average inter-burst time
		self.trainIBT(metrics[i_ibt])
		# Number of bursts
		self.trainNumBursts(metrics[i_b])
		# Number of cells per burst
		self.trainPerBurst(metrics[i_pbd], metrics[i_pbu])
		# Total number of cells
		self.trainTotalCells(metrics[i_d], metrics[i_u])

	def meanTotalDistance(self):
		return np.mean(self.tot_distances)

	def meanPerBurstDistance(self):
		return np.mean(self.per_burst_distances)

	def IBTVote(self, ibt):
		std = np.std(self.inter_burst_times)
		mean = np.mean(self.inter_burst_times)

		dist = abs(ibt - mean)
		perfect_match = dist == 0 and std == 0
		limit = 4.0

		if perfect_match:
			return 4.0
		elif dist <= limit:
			return 1.0
		else:
			return -1.0

	def numBurstsVote(self, b):
		std = np.std(self.num_burst)
		mean = np.mean(self.num_burst)

		dist = abs(b - mean)
		perfect_match = dist <= 0.5 and std <= 0.5
		limit = 2.0

		if perfect_match:
			return 4.0
		elif dist <= limit:
			return 1.0
		else:
			return -1.0

	def perBurstRatioVote(self, ratio):
		ratios = self.per_burst_dn/self.per_burst_up
		mean = np.mean(ratios)

		dist = abs(ratio - mean)
		limit = mean/3.5

		if dist <= limit:
			return 1.0
		else:
			return -1.0

	def totalRatioVote(self, ratio):
		ratios = self.tot_cells_dn/self.tot_cells_up
		mean = np.mean(ratios)

		dist = abs(ratio - mean)
		limit = mean/1.8

		if dist <= limit:
			return 1.0
		else:
			return -1.0

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

	def openIBTVote(self, ibt):
		std = np.std(self.inter_burst_times)
		mean = np.mean(self.inter_burst_times)

		dist = abs(ibt - mean)

		if dist < std/2.0:
			return 1
		else:
			return 0

	def openNumBurstVote(self, b):
		std = np.std(self.num_burst)
		mean = np.mean(self.num_burst)

		dist = abs(b - mean)
		
		if dist < std:
			return 1
		else:
			return 0

	def openTotalDistanceVote(self, d, u):
		std = np.std(self.tot_distances)
		mean = np.mean(self.tot_distances)
		
		distances = np.array([])
		for i in range(len(self.tot_cells_dn)):
			d1 = self.tot_cells_dn[i]
			u1 = self.tot_cells_up[i]
			distances = np.append(distances, self.euclidianDist(d, u, d1, u1))
		std2 = np.std(distances)
		mean2 = np.mean(distances)

		dist = abs(mean - mean2)
		if dist < std:
			return 1
		else:
			return 0

	def predictOpen(self, metrics):
		votes = []
		# Average inter-burst time
		votes.append(self.openIBTVote(metrics[i_ibt]))
		#votes.append(self.openNumBurstVote(metrics[i_b]))
		#votes.append(self.openTotalDistanceVote(metrics[i_d], metrics[i_u]))
		return votes