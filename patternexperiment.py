import patternfingerprint as fingerprint
from classifier import Classifier
from itertools import combinations
import sys

dump_path = "PatternDumps"
monitored_sites = ["amazon.co.uk", "cbsnews.com", "ebay.co.uk", "google.com", "nrk.no", "vimeo.com", "wikipedia.org", "yahoo.com", "youtube.com"]
#monitored_sites = ["google.com", "nrk.no", "vimeo.com", "youtube.com"] 88%

per_burst_weight = 1.0
total_cells_weight = 1.0

def indexOfSortedValues(l, descending=False):
	sort = sorted(l, reverse=descending)
	indices = [l.index(x) for x in sort]
	return indices

def calculateDistanceVotes(vector, w):
	G = indexOfSortedValues(vector)
	l = float(len(vector))
	votes = []
	for i in range(len(vector)):
		j = i
		while True:
			try:
				r = G.index(j)
				break
			except:
				j -= 1

		v = 2*w - 2*r/l*w
		if v == 2.0:
			v += 2.0
		votes.append(v)
	return votes

def createTrainingSets(n):
	l = []
	for i in range(n):
		l.append(range(0, i)+range(i+1, n)+range(i, i+1))
	return l

def closedWorldExperiment(n):
	training_sets = createTrainingSets(num_train)
	total_results = [0]*len(monitored_sites)
	per_site_results = {key: [0]*len(monitored_sites) for key in monitored_sites}

	for permutation in training_sets:
		# Create classifiers with training data
		clf = [Classifier(site) for site in monitored_sites]
		for i in permutation[:-1]:
			for k, site in enumerate(monitored_sites):
				try:
					fp = fingerprint.makeFingerprint("%s/%s/%s.cap" % (dump_path, site, i))
					clf[k].train(fp)
				except:
					print "ERROR: Not enough packet dumps to train with %d visits." % (num_train - 1)
					sys.exit()

		# Predictions
		for site in monitored_sites:
			fp = fingerprint.makeFingerprint("%s/%s/%s.cap" % (dump_path, site, permutation[-1]))
			prediction_votes = []
			per_burst_dist = []
			total_dist = []
			for c in clf:
				try:
					prediction_votes.append(c.predict(fp, site))
					per_burst_dist.append(c.perBurstDistance(fp))
					total_dist.append(c.totalDistance(fp))
				except:
					print "ERROR: Not enough packet dumps to train with %d visits." % (num_train - 1)
					sys.exit()

			per_burst_votes = calculateDistanceVotes(per_burst_dist, per_burst_weight)
			total_dist_votes = calculateDistanceVotes(total_dist, total_cells_weight)

			total_votes = [prediction_votes[i] + per_burst_votes[i] + total_dist_votes[i] for i in range(len(clf))]
			res = indexOfSortedValues(total_votes, descending=True)

			j = monitored_sites.index(site)
			while True:
				try:
					per_site_results[site][res.index(j)] += 1
					total_results[res.index(j)] += 1
					break
				except:
					j -= 1

	print per_site_results
	print "Total results: ", total_results, ("%.2f" % (float(total_results[0])/sum(total_results)) )

if __name__=="__main__":

	try:
		num_train = int(sys.argv[1]) + 1
	except:
		print "Usage: python %s <number of training instances>" % sys.argv[0]
		sys.exit()

	closedWorldExperiment(num_train)