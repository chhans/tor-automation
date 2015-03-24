import math
from itertools import imap

class Correlate:
	def __init__(self, fingerprint_path, capture_path):
		self.fingerprint_path = fingerprint_path
		self.capture_path = capture_path

		with open("%straces" % fingerprint_path, "r") as f:
			self.f_traces = [[int(y) for y in x.split(", ")] for x in f]
			f.close()

		with open("%straces" % capture_path, "r") as f:
			self.c_traces = [[int(y) for y in y.split(", ")] for y in f]
			f.close()

		with open("%scap.list" % fingerprint_path, "r") as f:
			self.f_sites = f.read().splitlines()
			f.close()

		with open("%scap.list" % capture_path, "r") as f:
			self.c_sites = f.read().splitlines()
			f.close()

	def calculate(self):
		tot_result = ""
		for i, c in enumerate(self.c_traces):
			distance_vector = [-1]*len(self.f_traces)
			for j, f in enumerate(self.f_traces):
				#distance_vector[j] = self.pcc(c, f)
				distance_vector[j] = math.sqrt((c[0]-f[0])**2 + (c[1]-f[1])**2)
			
			sorted_indices = self.getSortedIndices(distance_vector)
			correct_index = self.getCorrectIndex(i)
			guess_rank = self.getGuessRank(sorted_indices, correct_index)

			if guess_rank == 0:
				tot_result += "%d: Correct guess for site\t %s\n" % (i, self.c_sites[i])
			else:
				tot_result += "%d: Incorrect guess for site\t %s (%d)\n" % (i, self.c_sites[i], guess_rank)

			self.storeResult(i, distance_vector, sorted_indices, guess_rank)
		# Store the total result of the experiment
		print tot_result
		with open("%stotal-results.txt" % self.capture_path, "w") as f:
			f.write(tot_result)
			f.close()

	# Calculate the Pearson Correlation Coefficient of two variables X and Y
	def pcc(self, x, y):
		# Cut longest variable to match short one
		x = x[:min(len(x), len(y))]
		y = y[:min(len(x), len(y))]
		n = len(x)
		sum_x = float(sum(x))
		sum_y = float(sum(y))
		sum_x_sq = sum(map(lambda x: pow(x, 2), x))
		sum_y_sq = sum(map(lambda x: pow(x, 2), y))
		psum = sum(imap(lambda x, y: x * y, x, y))
		num = psum - (sum_x * sum_y/n)
		den = pow((sum_x_sq - pow(sum_x, 2) / n) * (sum_y_sq - pow(sum_y, 2) / n), 0.5)
		if den == 0: return 0
		return num / den

	# Get the indices of the distance_vector sorted by the value of the index
	def getSortedIndices(self, distance_vector):
		return sorted(range(len(distance_vector)), key=lambda k: distance_vector[k])

	# Get the correct index of the captured page in the list of fingerprinted pages
	def getCorrectIndex(self, capture_index):
		return self.f_sites.index(self.c_sites[capture_index])

	# Get the guess rank, the possition of the correct site in the list of guessed sites.
	# The lower the guess rank, the closer the guess is to be correct.
	def getGuessRank(self, sorted_indices, correct_index):
		return sorted_indices.index(correct_index)

	# Stores correlation results in file as follows
	# The captured web page:trace for captured page
	# Guess rank
	# List of rest of the pages according to distance to trace with the following format
	# page:distance:trace for page
	def storeResult(self, i, distance_vector, sorted_indices, guess_rank):
		file_path = ""
		tot_str = "%s:%s\n%d\n" % (self.c_sites[i], self.c_traces[i], guess_rank)
		for guess in sorted_indices:
			tot_str += "%s:%s:%s\n" % (self.f_sites[guess], distance_vector[guess], self.f_traces[guess])
		with open("%s%d-results.txt" % (self.capture_path, i), "w") as f:
			f.write(tot_str)
			f.close()

if __name__=="__main__":
	fingerprint_path = "./circuittest_nojs_100/"
	capture_path = "./circuittest_10_cap/"
	
	c = Correlate(fingerprint_path, capture_path)
	c.calculate()