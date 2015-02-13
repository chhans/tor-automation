from itertools import imap

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

with open("fingerprints/traces", "r") as f:
	fingerprint_traces = [[int(y) for y in x.strip().split(", ")] for x in f]

with open("test/traces", "r") as f:
	captured_traces = [[int(y) for y in x.strip().split(", ")] for x in f]

for c in captured_traces:
	a = [-1]*len(fingerprint_traces)
	for i,f in enumerate(fingerprint_traces):
		a[i] = abs(float(f[0])/f[1] - float(c[0])/c[1])
		#a[i] = #abs(f[0]-c[0])+abs(f[1]-c[1])
	#print sorted(a)
	print c
	print a.index(min(a)) + 1