import os
import numpy as np

inter_capture_time = 45 # minutes

def numTrain(l):
	return int(l.split(": ")[1])

def timeSpan(l):
	s = l.split(", experiment: ")
	exp = int(s[1])
	t = s[0].split(": ")[1]
	t_list = t[1:-1].split(",")
	t_list = [int(x) for x in t_list]	
	t_list.append(exp)
	time_span = (max(t_list)-min(t_list))*inter_capture_time
	return time_span

def accuracy(l):
	return float(l.split(" (")[1].split("%)")[0])

def singleTotal(l):
	s = l.split(":")
	return (int(s[0]), int(s[1]))

def singlePage(l):
	s = l.split(":")
	return (s[0], int(s[1]))

time_dictionary = {45: {"total": {}, "page": {}, "acc": np.array([])}, 
					90: {"total": {}, "page": {}, "acc": np.array([])}, 
					135: {"total": {}, "page": {}, "acc": np.array([])}, 
					180: {"total": {}, "page": {}, "acc": np.array([])},
					225: {"total": {}, "page": {}, "acc": np.array([])}}

ntrain_dictionary = {1: np.array([]), 2: np.array([]), 3: np.array([]), 4: np.array([]), 5: np.array([])}
pages = {}

worst = {"acc": 100, "train": 0, "time": 0, "total": {}}
best = {"acc": 0, "train": 0, "time": 0, "total": {}}


for res_file in os.listdir("."):
	if res_file == "resultInterpreter.py":
		continue
	with open(res_file, "r") as f:
		n_train = numTrain(f.next())
		time = timeSpan(f.next())
		f.next()
		f.next()
		a = accuracy(f.next())
		l = f.next()
		total = {}
		while not l == "\n":
			st = singleTotal(l)
			if st in total:
				total[st[0]] += st[1]
			else:
				total[st[0]] = st[1]
			l = f.next()

		l = f.next()
		l = f.next()
		while True:
			try:
				s = singlePage(l)
				if not s[0] in pages:
					pages[s[0]] = np.array([s[1]])
				else:
					pages[s[0]] = np.append(pages[s[0]], s[1])
				l = f.next()
			except:
				break
		
		if a < worst["acc"]:
			worst["acc"] = a
			worst["train"] = n_train
			worst["time"] = time
			worst["total"] = total
		if a > best["acc"]:
			best["acc"] = a
			best["train"] = n_train
			best["time"] = time
			best["total"] = total

		ntrain_dictionary[n_train] = np.append(ntrain_dictionary[n_train], a)
		time_dictionary[time]["acc"] = np.append(time_dictionary[time]["acc"], a)


		f.close()

mean_acc = np.array([])
for (key, value) in ntrain_dictionary.iteritems():
	mean_acc = np.append(mean_acc, value)

print "MEAN ACCURACY: %.2f" % np.mean(mean_acc)
print "BEST: %.2f \t n = %d \t t = %d" % (best["acc"], best["train"], best["time"])
print "WORST: %.2f \t n = %d \t t = %d\n" % (worst["acc"], worst["train"], worst["time"])


print "RESULTS BASED ON #TRAINING INSTANCES"
for (key, value) in ntrain_dictionary.iteritems():
	print "  %d:\t%.2f" % (key, np.mean(value))

print "RESULST BASED ON TIMESPAN"
for (key, value) in time_dictionary.iteritems():
	print " TIME = %d" % key
	print len(value["acc"])
	print "   %.2f" % np.mean(value["acc"])

for page in pages:
	print page, "\tMEAN: %.2f, \tSTDEV: %.2f" % (np.mean(pages[page]), np.std(pages[page]))