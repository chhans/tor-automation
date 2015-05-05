from classifier import Classifier
from itertools import combinations
from datetime import datetime
import sys
import os

open_path = "PatternDumps/open"
closed_path = "PatternDumps/closed"
monitored_sites = ["cbsnews.com", "google.com", "nrk.no", "vimeo.com", "wikipedia.org", "youtube.com"]

per_burst_weight = 1
total_cells_weight = 1.1

diff_threshold = 1.5 # Higher threshold implies lower true and false positive rate
max_threshold = 7

def mkdir(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)

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
	total = [pred[i] + pbv[i] + tdv[i] for i in range(len(clf))]
	return total

def getFingerprint(f_path):
	with open(f_path, "r") as f:
		fp = [int(dimension) for dimension in f.readlines()]
		f.close()
	return fp

def createClassifiers(file_list):
	clf = [Classifier(site) for site in monitored_sites]
	for i in file_list:
		for k, site in enumerate(monitored_sites):
			f_path = "%s/%s/%i.fp" % (closed_path, site, i)
			fp = getFingerprint(f_path)
			clf[k].train(fp)
	return clf

def createExperimentSets(n_train, n_exp):
	tot = n_train + n_exp
	tot_r = range(tot)

	combo_train = list(combinations(tot_r, n_train))
	exp_sets = []
	if n_train == 1:
		for t in combo_train:
			exp_sets.append([[y for y in t], [x for x in tot_r if x not in t]])
			tot_r = [x for x in tot_r if x not in t]
	else:
		for t in combo_train:
			exp_sets.append([[y for y in t], [x for x in tot_r if x not in t]])

	return exp_sets

def closedWorldExperiment(n_train, n_exp):

	experiment_sets = createExperimentSets(n_train, n_exp)
	total_results = dict.fromkeys(range(0, 6), 0)
	site_results = dict.fromkeys(monitored_sites, 0)
	total = 0

	for e_set in experiment_sets:
		training_set = e_set[0]
		# Create classifiers with training data
		clf = createClassifiers(training_set)
		for exp in e_set[1]:

			for i, site in enumerate(monitored_sites):
				f_path = "%s/%s/%d.fp" % (closed_path, site, exp)
				fp = getFingerprint(f_path)
				votes = matchAgainstClassifiers(clf, fp)
				res = indexOfSortedValues(votes, descending=True)

				j = 0
				while True:
					try:
						rank = res.index(i-j)
						break
					except:
						j += 1


				total += 1
				total_results[rank] += 1
				if rank == 0:
					site_results[site] += 1

	storeClosedWorldResult(n_train, n_exp, total, total_results, site_results)

def openWorldFileList(train_range):
	fp_list = []

	for (dirpath, dirnames, filenames) in os.walk(closed_path):
		for f in filenames:
			if f[-3:] == ".fp" and not int(f[-4]) in train_range:
				fp_list.append(dirpath+"/"+f)

	for (dirpath, dirnames, filenames) in os.walk(open_path):
		for f in filenames:
			if f[-3:] == ".fp":
				fp_list.append(dirpath+"/"+f)

	return fp_list

# Returns True if votes imply an open world hit
def openWorldThreshold(votes):
	if max(votes) > max_threshold and (max(votes)-sorted(votes)[-2]) > diff_threshold:
		return True
	else:
		return False

# Returns true if the supplied fingerprint feature vector is predicted to belong to one of the marked sites
def openWorldPrediction(marked, feature_vector, clf):
	votes = matchAgainstClassifiers(clf, feature_vector)
	res = indexOfSortedValues(votes, descending=True)
	guessed_site = monitored_sites[res[0]]

	# The site is guessed to be one of the marked ones
	if guessed_site in marked and openWorldThreshold(votes):
		return True
	else:
		return False

def openWorldExperiment(n_train, n_classifier, marked):

	true_positives = 0
	false_positives = 0
	false_negatives = 0
	true_negatives = 0

	training_sets = [x[0] for x in createExperimentSets(n_train, n_classifier)]
	for training_range in training_sets:
		# Create classifiers with training data, use remaining feature vectors as experiments
		clf = createClassifiers(training_range)
		fv_paths = openWorldFileList(training_range)

		for f_path in fv_paths:
			feature_vector = getFingerprint(f_path)
			actual_site = f_path.split("/")[-2]

			hit = openWorldPrediction(marked, feature_vector, clf)

			if hit:
				if actual_site in marked:
					true_positives += 1
				else:
					false_positives += 1
			else:
				if actual_site in marked:
					false_negatives += 1
				else:
					true_negatives += 1

	storeOpenWorldResult(n_train, marked, true_positives, false_positives, false_negatives, true_negatives)

def storeClosedWorldResult(n_train, n_exp, total, total_results, site_results):

	with open("PatternResults/closed/%s" % (str(datetime.now())), "w") as r_file:
		print "Completed experiment. Achieved accuracy of %.2f%%. Detailed results stored in %s." % (100*(float(total_results[0]))/total, r_file.name)
		r_file.write("Number of training instances: %d\n" % n_train)
		r_file.write("Number of predictions: %d\n\n" % total)
		r_file.write("Accuracy:\t%.2f\n" % (float(total_results[0])/total))
		for guesses in total_results:
			r_file.write("%d:\t\t%d\t%.2f\n" % (guesses, total_results[guesses], float(total_results[guesses])/total))
		r_file.write("\nIndividual site accuracy:\n")
		for site in site_results:
			r_file.write("%s: %.2f\n" % (site, float(site_results[site])/(total/len(monitored_sites))))

		r_file.close()

def storeOpenWorldResult(n_train, marked, true_positives, false_positives, false_negatives, true_negatives):

	first_dir = "PatternResults/open/%s_training_instances" % n_train
	mkdir(first_dir)
	second_dir = "%s/%d_marked_sites" % (first_dir, len(marked))
	mkdir(second_dir)

	acc = float(true_positives+true_negatives)/(true_positives+false_negatives+false_positives+true_negatives)

	with open("%s/%s" % (second_dir, marked), "w") as r_file:
		print "Completed experiment. Achieved an accuracy of %.2f%%. Detailed results stored in %s." % (100*acc, r_file.name)
		r_file.write("Number of training instances: %d\n" % n_train)
		r_file.write("Marked sites: ")
		for site in marked:
			r_file.write(site+" ")
		r_file.write("\n\nTP\tFP\tTN\tFN\n%d\t%d\t%d\t%d" % (true_positives, false_positives, true_negatives, false_negatives))

if __name__=="__main__":

	try:
		model = sys.argv[1]
		if model not in ["closed", "open"]:
			raise
	except:
		print "Error: first argument must be either 'open' or 'closed'"
		print "Usage: python %s <closed/open> <number of training instances> <number of experiment instances> <marked sites (if open world)>" % sys.argv[0]
		sys.exit()

	if model == "closed":
		try:
			n_train = int(sys.argv[2])
			n_exp = int(sys.argv[3])
		except:
			print "Error: second and third argument must be the number of training instances and experiments respectively"
			print "Usage: python %s <closed/open> <number of training instances> <number of experiment instances> <marked sites (if open world)>" % sys.argv[0]
			sys.exit()

		closedWorldExperiment(n_train, n_exp)
	elif model == "open":
		try:
			n_train = int(sys.argv[2])
			n_exp = int(sys.argv[3])
		except:
			print "Error: second and third argument must be the number of training instances and experiments respectively"
			print "Usage: python %s <closed/open> <number of training instances> <number of experiment instances> <marked sites (if open world)>" % sys.argv[0]
			sys.exit()

		marked = []
		i = 4
		while True:
			try:
				marked_site = sys.argv[i]
				marked.append(marked_site)
				i += 1
			except:
				break
		if len(marked) == 0:
			print "Error: no marked sites supplied."
			print "Usage: python %s <closed/open> <number of training instances> <number of experiment instances> <marked sites (if open world)>" % sys.argv[0]
			sys.exit()
		for site in marked:
			if site not in monitored_sites:
				print "Error: site %s is not part of classifier and can thus not be used as a monitored site" % site
				sys.exit()
		openWorldExperiment(n_train, n_exp, marked)