import patternfingerprint as fingerprint
from classifier import Classifier
from itertools import combinations
import sys
import os

dump_path = "PatternDumps"
#monitored_sites = ["amazon.co.uk", "cbsnews.com", "ebay.co.uk", "google.com", "nrk.no", "vimeo.com", "wikipedia.org", "yahoo.com", "youtube.com"] # 67%
#monitored_sites = ["cbsnews.com", "google.com", "nrk.no", "vimeo.com", "wikipedia.org", "yahoo.com", "youtube.com"] # 83%
monitored_sites = ["cbsnews.com", "google.com", "nrk.no", "vimeo.com", "wikipedia.org", "youtube.com"] # 94%

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

def matchAgainstClassifiers(clf, fp):
	pred = []
	pbd = []
	td = []
	for c in clf:
		pred.append(c.predict(fp))
		pbd.append(c.perBurstDistance(fp))
		td.append(c.totalDistance(fp))
	pbv = calculateDistanceVotes(pbd, per_burst_weight)
	tdv = calculateDistanceVotes(td, total_cells_weight)
	#pbv = calc2(pbd)
	#tdv = calc2(td)
	total = [pred[i] + pbv[i] + tdv[i] for i in range(len(clf))]
	return total

def createClassifiers(file_list):
	clf = [Classifier(site) for site in monitored_sites]
	for i in file_list:
		for k, site in enumerate(monitored_sites):
			fp = fingerprint.makeFingerprint("%s/%s/%s.cap" % (dump_path, site, i))
			clf[k].train(fp)
	return clf


def closedWorldExperiment(n):
	training_sets = createTrainingSets(n)
	total_results = [0]*len(monitored_sites)
	per_site_results = {key: [0]*len(monitored_sites) for key in monitored_sites}

	for permutation in training_sets:
		# Create classifiers with training data
		clf = createClassifiers(permutation[:-1])

		# Predictions
		for site in monitored_sites:
			fp = fingerprint.makeFingerprint("%s/%s/%s.cap" % (dump_path, site, permutation[-1]))
			votes = matchAgainstClassifiers(clf, fp)
			res = indexOfSortedValues(votes, descending=True)

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

def testClassifier(c, fp):
	prediction = c.predict(fp)
	if prediction < 0.0:
		return False
	total_dist = c.totalDistance(fp)
	if total_dist > c.meanTotalDistance():
		return False
	per_burst_dist = c.perBurstDistance(fp)
	if per_burst_dist > c.meanPerBurstDistance():
		return False
	return True

def openWorldFileList(site_path, monitored, n_train):
	files = os.listdir(site_path)
	fl = []
	for f in files:
		if not f[-3:] == "cap":
			continue
		if monitored and int(f[:-4]) < n_train-1:
			continue
		fl.append(f)
	return fl

def openWorldExperiment(n_train):
	# Create classifiers with training data
	clf = createClassifiers(range(n_train))

	false_positives = 0
	true_positives = 0
	tot_p = 0
	tot_n = 0

	sites = os.listdir(dump_path)
	for site in sites:
		monitored = site in monitored_sites
		site_path = "%s/%s" % (dump_path, site)
		caps = openWorldFileList(site_path, monitored, n_train)
		for cap in caps:
			fp = fingerprint.makeFingerprint("%s/%s" % (site_path, cap))
			votes = matchAgainstClassifiers(clf, fp)
			hit = max(votes) >= 10 and (max(votes)-sorted(votes)[-2]) > 2.0
			if monitored:
				tot_p += 1
				if hit:
					true_positives += 1
			else:
				tot_n += 1
				if hit:
					false_positives += 1

	#print "Number of tests:", tot_p+tot_n
	print "Hit rate:", true_positives+false_positives,"/",tot_p+tot_n
	print "False positive rate:", 100*(float(false_positives)/tot_n), "%"
	print "True positives:", 100*(float(true_positives)/tot_p), "%"
	print "False positives:", 100*(float(false_positives)/(tot_p+tot_n)), "%"

if __name__=="__main__":

	try:
		n_train = int(sys.argv[1]) + 1
	except:
		print "Usage: python %s <number of training instances>" % sys.argv[0]
		sys.exit()

	closedWorldExperiment(n_train)
	per_burst_weight = 2.0
	total_cells_weight = 2.0
	openWorldExperiment(n_train)