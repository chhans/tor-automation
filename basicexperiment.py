import sys
import os
import math
import operator
from datetime import datetime
from itertools import combinations

training_data = "Dumps/training/"
experiment_data = "Dumps/experiment/"
results = "BasicResults/"

def trainModel(path, training_range):
	key = path.split("/")[-1]
	u = 0
	d = 0
	for i in training_range:
		f_path = path+"/%d.fp" % i
		try:
			fingerprint = getFingerprint(f_path)
			u += fingerprint[0]
			d += fingerprint[1]
		except:
			print "ERROR: Not enough fingerprints to create model of %s with %d training instances" % (key, training_range)
			sys.exit()
	u = float(u)/len(training_range)
	d = float(d)/len(training_range)
	value = [u, d]
	return (key, value)

def getFingerprint(f_path):
	fingerprint = [0, 0]
	with open(f_path, "r") as f:
		fp_string = f.next().split(",")
		f.close()
		fingerprint[0] = int(fp_string[0])
		fingerprint[1] = int(fp_string[1])
		return fingerprint

def euclidianDistance(fp1, fp2):
	return math.sqrt ( (fp1[0] - fp2[0])**2 + ( fp1[1] - fp2[1] )**2 )

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

	for e_set in experiment_sets:
		training_set = e_set[0]
		for exp in e_set[1]:
			training_models = {}
			page_results = {}
			total_results = {}
			correct = 0

			for page in os.listdir(training_data):
				# Create classifiers from training data
				model = trainModel(training_data+page, training_set)
				training_models[model[0]] = model[1]

				# Do experiments on classifiers
				fp = getFingerprint(training_data+page+"/%d.fp" % exp)
				distances = {}
				for (key, value) in training_models.iteritems():
					distances[key] = euclidianDistance(fp, value)
				sorted_distances = sorted(distances.items(), key=operator.itemgetter(1))
				rank = [y[0] for y in sorted_distances].index(page)

				if rank in total_results:
					total_results[rank] += 1
				else:
					total_results[rank] = 1

				if rank == 0:
					correct += 1

				page_results[page] = rank

			storeResults(training_set, exp, n_train, correct, len(page_results), total_results, page_results)

def storeResults(t_set, exp, n_train, correct, number_of_pages, total_results, page_results):
	with open(results+str(datetime.now()), "w") as r_file:
		print "Completed experiment. Achieved accuracy of %.2f%%. Detailed results stored in %s." % (100*float(correct)/number_of_pages, r_file.name)
		r_file.write("Number of training instances: %d\n" % n_train) 
		r_file.write("Training set: %s, experiment: %d\n\n" % (t_set, exp))
		r_file.write("Total results:\n")
		r_file.write("Accuracy:\t%d/%d (%.2f%%)\n" % (correct, number_of_pages, 100*float(correct)/number_of_pages))
		for (key, value) in total_results.iteritems():
			r_file.write("%d:\t\t\t%d\n" % (key, value))
		r_file.write("\nIndividual page results:\n")
		for (key, value) in page_results.iteritems():
			r_file.write("%s: %d\n" % (key, value))
		r_file.close()

if __name__ == "__main__":
	try:
		n_train = int(sys.argv[1])
		n_exp = int(sys.argv[2])
	except:
		print "Usage: python %s <number of training instances> <number of experiment instances>" % sys.argv[0]
		sys.exit()

	closedWorldExperiment(n_train, n_exp)