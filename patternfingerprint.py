import pcapy
import socket
import re
import sys

from classifier import Classifier
from torCell import TorCell

tls_header = "\x17\x03[\x00\x01\x02\x03]\x02[\x30\x1a]"
src_ip = "129.241.208.200"
burst_tolerance = 2000

per_burst_weight = 1.0
total_cells_weight = 1.0

# TODO:
# Tune burst detection threshold (1000 = 1 second)
# Test if ignoring bursts with few packets improves accuracy (probably SENDMEs etc.)
# Performance improvements if necessary: 
	# Filter out noise packets (easier than regexing whole packet payload)
	# Do calculations on the fly when reading the dump files

def makeFingerprint(file_path):
	cells = []

	try:
		cap = pcapy.open_offline(file_path)
		(header, payload) = cap.next()

		while header:
			cells.extend(extractCell(header, payload))
			(header, payload) = cap.next()
	except pcapy.PcapError:
		pass # Expected error when getting to the end of the pcap
	except:
		print "Unexpected error when extracting cells:", sys.exc_info()[0]
		raise

	metrics = analyzeCells(cells)

	with open("%s.fp" % file_path[:-4], "w") as f:
		f.write("\n".join( str(x) for x in metrics))
		f.close()

	return metrics

def analyzeCells(cells):
	metrics = [0, 0, 0, 0, 0, 0]
	bursts = [[]]
	inter_burst_times = []
	burst_cells = [[0, 0]]

	for i, c in enumerate(cells):
		# Total cells down/up
		metrics[c.ul] += 1
		# Check if new burst
		if i == 0:
			continue
		inter_packet_t = c.ts - cells[i - 1].ts

		# Burst categorization
		if inter_packet_t < 0:
			print "ERROR: pcapy source code not updated to support nanosecond accuracy. Quitting."
			raise
		elif inter_packet_t > burst_tolerance: # 1000 equals 1 second
			bursts.append([c])
			burst_cells.append([not c.ul, c.ul])
			inter_burst_times.append(normalizeIPT(inter_packet_t))
		else:
			bursts[-1].append(c)
			burst_cells[-1][c.ul] += 1

	dl_b = [x[0] for x in burst_cells]
	dl_u = [x[1] for x in burst_cells]

	metrics[2] = sum(dl_b)/len(dl_b)
	metrics[3] = sum(dl_u)/len(dl_u)
	metrics[4] = len(bursts)
	metrics[5] = 0 if len(inter_burst_times) == 0 else sum(inter_burst_times)/len(inter_burst_times)

	return metrics

# Rounds the inter-packet time down to the nearest whole second
def normalizeIPT(t):
	return int(t/1000)

# Returns an array of the Tor cells present in the packet payload
def extractCell(header, payload):
	n = len(re.findall(tls_header, payload))
	return [TorCell(isOnUplink(payload), getTimestamp(header))]*n

# Returns the timestamp of the supplied header. 
# N.B. For nanosecond accuarcy, the pcapy source code must be modified.
def getTimestamp(header):
	try:
		return header.getts()[0]*1000 + header.getts()[1]
	except:
		return -1

# Returns true if the supplied payload indicates that the packet is on the uplink
def isOnUplink(payload):
	try:
		# Carve out src IP. Remove 14B ethernet header, 12B IP header start and 4B destination IP.
		src_ip_binary = payload[26:30]
		if src_ip == socket.inet_ntoa(src_ip_binary):
			return True
		return False
	except:
		print "Unexpected error when deciding direction. Using downlink.", sys.exc_info()[0]
		return False

def indexOfSortedValues(l, descending=False):
	sort = sorted(l, reverse=descending)
	indices = [l.index(x) for x in sort]
	return indices

def calculateDistanceVotes(vector, w):
	G = indexOfSortedValues(vector)
	l = float(len(vector))
	votes = [2*w - 2*x/l*w for x in G]
	return votes

#Y = ["amazon.co.uk", "cbsnews.com", "ebay.co.uk", "google.com", "nrk.no", "vimeo.com", "wikipedia.org", "yahoo.com", "youtube.com"]
#total_results = [0]*len(Y)
#iterations = [(0, 1, 2), (0, 2, 1), (1, 2, 0)]
#
#for pattern in iterations:
#	# Create class models with training data
#	models = [Classifier(x) for x in Y]
#	for i in [pattern[0], pattern[1]]:
#		for directory in Y:
#			fp = makeFingerprint("PatternDumps/%s/%s.cap" % (directory, i))
#			models[Y.index(directory)].train(fp)
#
#	#Predictions
#	for directory in Y:
#		fp = makeFingerprint("PatternDumps/%s/%s.cap" % (directory, pattern[2]))
#		prediction_votes = []
#		per_burst_dist = []
#		total_dist = []
#		for m in models:
#			prediction_votes.append(m.predict(fp))
#			per_burst_dist.append(m.perBurstDistance(fp))
#			total_dist.append(m.totalDistance(fp))
#
#		per_burst_votes = calculateDistanceVotes(per_burst_dist, per_burst_weight)
#		total_dist_votes = calculateDistanceVotes(total_dist, total_cells_weight)
#		total_votes = [prediction_votes[i] + per_burst_votes[i] + total_dist_votes[i] for i in range(len(models))]
#
#		print ["%.2f" % x for x in total_votes]
#		res = indexOfSortedValues(total_votes, descending=True)
#		total_results[res.index(Y.index(directory))] += 1
#
#t_sum = sum(total_results)
#print total_results, ("%.2f" % (float(total_results[0])/sum(total_results)))