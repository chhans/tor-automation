from sklearn import svm
import os

def guess_rank(result):
	votes = [0]*4
	p = 0
	for i in range(4):
		for j in range(i + 1, 4):
			if result[p] > 0:
				votes[i] += 1
			else:
				votes[j] += 1
			p += 1
			print p
	return votes

clf = svm.LinearSVC()
for i in range(2):
	fingerprint_path = "./repeat_100_%i/" % i

	with open("%scap.list" % fingerprint_path, "r") as f:
		f_sites = f.read().splitlines()
		f.close()

	with open("%straces" % fingerprint_path, "r") as f:
		f_traces = [[int(y) for y in x.split(", ")] for x in f]
		f.close()
		clf.fit(f_traces, f_sites)


capture_path = "./repeat_10_cap/"

with open("%straces" % capture_path, "r") as f:
	c_traces = [[int(y) for y in y.split(", ")] for y in f]
	f.close()

with open("%scap.list" % capture_path, "r") as f:
	c_sites = f.read().splitlines()
	f.close()

print clf.predict(c_traces)
print c_sites

#for c_i in range(0, 1):
#	c = c_traces[c_i]
#	f_t = f_traces[:]
#	f_s = f_sites[:]
#
#	#clf = svm.SVC(kernel='linear', probability=True)
#	clf = svm.LinearSVC()
#
#	# Remove 90% to 125% lengths
#	lim = (0.90, 1.25)
#	len_c = c[0]+c[1]
#	for i, f in reversed(list(enumerate(f_t))):
#		len_f = f[0]+f[1]
#		if len_f < lim[0]*len_c or len_f > lim[1]*len_c:
#			if f_s[i] == c_sites[c_i]:
#				print "Removed correct guess (tot packets)"
#			del f_s[i]
#			del f_t[i]
#
#	# Truncate feature array
#	short = min(len(c), min(map(len, f_t)))
#	c = c[:short]
#	f_t = [x[:short] for x in f_t]
#
#	clf.fit(f_t, f_s)
#	p = clf.predict(c)
#	print guess_rank(clf.decision_function(c)[0])
#	print f_s
##	print guess_rank(clf.decision_function(c))
#
#	print "%s - guessed %s (%s)" % (p == c_sites[c_i], p, c_sites[c_i])


# Remove 50% to 200% lengths
#lim = (0.9, 1.4)
#del_indices = []
#for i,f in reversed(list(enumerate(f_traces))):
#	if len(f) > lim[1]*len(c) or len(f) < lim[0]*len(c):
#		if f_sites[i] == c_sites[c_index]:
#			print "NOOES! Removed correct guess"
#		del f_sites[i]
#		del f_traces[i]
#
## Truncate all traces to match shortest
#short = min(len(c), min(map(len, f_traces)))
#f_traces = [x[:short] for x in f_traces]
#c = c[:short]
#
#clf = svm.SVC(kernel='linear')
#clf.fit(f_traces, f_sites)
#print clf.predict(c)
#short = min(min(map(len, c_traces)), min(map(len, f_traces)))
#c_traces = [x[:short] for x in c_traces]
#f_traces = [x[:short] for x in f_traces]

#clf = svm.SVC(kernel='linear')
#clf.fit(f_traces, f_sites)

#print clf.predict(c_traces)
#print c_sites
