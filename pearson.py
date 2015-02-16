from itertools import imap
import math

def pearson(x, y):
	n = len(x)
	sum_x = float(sum(x))
	sum_y = float(sum(y))
	sum_x_sq = sum(map(lambda x: pow(x, 2), x))
	sum_y_sq = sum(map(lambda x: pow(x, 2), y))
	psum = sum(imap(lambda x, y: x * y, x, y))
	num = psum - (sum_x * sum_y/n)
	den = pow((sum_x_sq - pow(sum_x, 2) / n) * (sum_y_sq - pow(sum_y, 2) / n), 0.5)
	if den == 0:
		return 0
	else:
		return num / den

with open("test/traces", "r") as f:
	fingerprint_traces = [[int(y) for y in x.strip().split(", ")] for x in f]
	f.close()

with open("test2/traces", "r") as f:
	captured_traces = [[int(y) for y in x.strip().split(", ")] for x in f]
	f.close()

for j,c in enumerate(captured_traces):
	distance = [-1]*len(fingerprint_traces)
	for i,f in enumerate(fingerprint_traces):
		distance[i] = math.sqrt( (c[0]-f[0])**2 + (c[1]-f[1])**2)
	print "TRACE %d guess: %s" % (j,distance.index(min(distance)))