import pcapy
import socket
import re
import sys
import os

from torCell import TorCell

tls_header = "\x17\x03[\x00\x01\x02\x03]\x02[\x30\x1a]"
burst_tolerance = 2500
burst_size_limit = 1
src_ip = "129.241.208.200"
open_data = "PatternDumps/open/"
closed_data = "PatternDumps/closed/"

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
			new_ibt = normalizeIPT(inter_packet_t)
			if len(bursts[-1]) < burst_size_limit:
				for dc in bursts[-1]:
					metrics[dc.ul] -= 1
				bursts.pop()
				burst_cells.pop()
				try:
					new_ibt += inter_burst_times.pop()
				except:
					pass
			bursts.append([c])
			burst_cells.append([not c.ul, c.ul])
			inter_burst_times.append(new_ibt)
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

if __name__ == "__main__":

	try:
		src_ip = sys.argv[1]
		socket.inet_aton(src_ip)
	except socket.error:
		print "Error: Invalid IP address"
		sys.exit()
	except:
		print "Usage: python %s <IP address of client>" % sys.argv[0]
		sys.exit()

	# Create fingerprints from closed world data
	for (dirpath, dirnames, filenames) in os.walk(closed_data):
		site = dirpath.split("/")[2]
		if len(site) > 1:
			print "Generating fingerprints for %s" % site

		for f in filenames:
			if not f[-4:] == ".cap":
				continue
			path = dirpath+"/"+f
			makeFingerprint(path)

	# Create fingerprints from open world data
	for (dirpath, dirnames, filenames) in os.walk(open_data):
		site = dirpath.split("/")[2]
		if len(site) > 1:
			print "Generating fingerprints for %s" % site

		for f in filenames:
			if not f[-4:] == ".cap":
				continue
			path = dirpath+"/"+f
			makeFingerprint(path)

	print "Successfully generated fingerprints"