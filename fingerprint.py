import pcapy
import socket
import re
import sys
import os

training_data = "Dumps/training/"
experiment_data = "Dumps/experiment/"
src_ip = "0.0.0.0" # 129.241.208.200

def makeFingerprint(capture_path):
	out_path = capture_path[:-4]+".fp"
	feature_vector = analyze(capture_path)
	with open(out_path, "w") as f:
		f.write(",".join( str(x) for x in feature_vector))
		f.close()

def analyze(capture_path):
	feature_vector = [0, 0]

	try:
		cap = pcapy.open_offline(capture_path)
		(header, payload) = cap.next()

		while header:
			# Filter out noise packets
			if isNoise(header, payload):
				(header, payload) = cap.next()
				continue

			# Number of TLS headers on uplink/downlink
			tls = carveTLSHeaders(payload)
			if tls[1]:
				feature_vector[0] += tls[0]
			else:
				feature_vector[1] += tls[0]

			(header, payload) = cap.next()
	except pcapy.PcapError:
		pass # Expected when reaching the end of the capture file
	except:
		print "Unexpected error", sys.exc_info()[0]
		raise

	return feature_vector

# Returns True if the supplied header indicates packet length of 66 (ACK etc) or if it is part of a TLS handshake 
def isNoise(header, payload):
	if header.getlen() == 66:
		return True
	elif len(re.findall("\x16\x03[\x00\x01\x02\x03]", payload)) > 0:
		return True
	else:
		return False

# Returns a tuple consisting of the number of TLS headers matching the bytestring and whether it is on uplink or downlink
def carveTLSHeaders(payload):
	bytestring = "\x17\x03[\x00\x01\x02\x03]\x02[\x30\x1a]"
	n = len(re.findall(bytestring, payload))
	ul = False
	try:
		# Carve out src IP. Remove 14B Ethernet header, 12B IP header start and 4B destination IP.
		ip_header = payload[26:30]
		s = socket.inet_ntoa(ip_header)
		if src_ip == s:
			ul = True
	except:
		pass
	return (n, ul)

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

	# Create fingerprints from training data
	for (dirpath, dirnames, filenames) in os.walk(training_data):
		site = dirpath.split("/")[2]
		if len(site) > 1:
			print "Generating fingerprints for %s" % site

		for f in filenames:
			if not f[-4:] == ".cap":
				continue
			path = dirpath+"/"+f
			makeFingerprint(path)

	for (dirpath, dirnames, filenames) in os.walk(experiment_data):
		site = dirpath.split("/")[2]
		if len(site) > 1:
			print "Generating fingerprints for %s" % site

		for f in filenames:
			if not f[-4:] == ".cap":
				continue
			path = dirpath+"/"+f
			makeFingerprint(path)

	print "Successfully generated fingerprints"