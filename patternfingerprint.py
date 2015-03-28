import pcapy
import socket
import re
import sys
import os
import math
import patternsvm as svm

from torCell import TorCell
from siteModel import SiteModel

tls_header = "\x17\x03[\x00\x01\x02\x03]\x02[\x30\x1a]"
src_ip = "129.241.208.200"
burst_tolerance = 2000

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

Y = ["amazon.co.uk", "cbsnews.com", "ebay.co.uk", "google.com", "nrk.no", "vimeo.com", "wikipedia.org", "yahoo.com", "youtube.com"]
models = [SiteModel(x) for x in Y]

for i in range(3):
	for directory in Y:
		fp = makeFingerprint("%s/%s.cap" % (directory, i))
		print Y.index(directory)
		models[Y.index(directory)].train(fp)

print models[0].inter_burst_times

#for i in range(2):
#	X = []
#	for directory in Y:
#		X.append(makeFingerprint("%s/%s.cap" % (directory, i)))
#	svm.train(X, Y)
#
#for i in range(2, 3):
#	for directory in Y:
#		print directory, svm.predict(makeFingerprint("%s/%s.cap" % (directory, i)))