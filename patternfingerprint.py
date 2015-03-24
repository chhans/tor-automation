import pcapy
import socket
import re
import sys
import os

from torCell import TorCell

tls_header = "\x17\x03[\x00\x01\x02\x03]\x02[\x30\x1a]"
src_ip = "129.241.208.200"

def makeFingerprint(file_path):
	# TODO: Clear previous data 
	cells = []

	try:
		cap = pcapy.open_offline(file_path)
		(header, payload) = cap.next()

		while header:
			# TODO: Filter out noise packets (causes speed-ups as it is easier than regexing the whole packet)
			cells.extend(extractCell(header, payload))
			(header, payload) = cap.next()
			# TODO: Consider doing calculation here, on the fly for improved performance
	except pcapy.PcapError:
		pass # Expected error when getting to the end of the pcap
	except:
		print "Unexpected error when extracting cells:", sys.exc_info()[0]
		raise

	print cells

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

for directory in ["google.com", "reddit.com", "flickr.com", "wikipedia.org", "youtube.com"]:
	for cap in os.listdir(directory):
		if cap[-4:] == ".cap":
			makeFingerprint("%s/%s" % (directory, cap))