import pcapy
import socket
import re

class Fingerprint:

	def __init__(self, count, passes, src_ip):
		self.count = count
		self.passes = passes
		self.src_ip = src_ip

	def makeFingerprints(self, in_path):
		self.clearPreviousData(in_path)
		for i in range(0, self.count):
			totalMetrics = None
			for j in range(0, self.passes):
				file_path = "%scaptures/%d-%d.cap" % (in_path, i, j)

				metrics = self.analyze(file_path)
				totalMetrics = self.add(totalMetrics, metrics)

			totalMetrics = self.avg(totalMetrics)
			print "Trace for site %d: %s" % (i, totalMetrics)
			self.appendToFile("%straces" % in_path, "%s\n" % ", ".join( str(x) for x in totalMetrics ))

	def clearPreviousData(self, in_path):
		try:
			open("%straces" % in_path, "w").close()
		except:
			pass

	def analyze(self, in_path):
		# metrics: [packets on uplink, packets on downlink, total transmitted bytes]
		metrics = [0, 0, 0]

		try:
			cap = pcapy.open_offline(in_path)
			total_bytes = 0
			(header, payload) = cap.next()
			while header:
				# Filter out the noise packets
				if self.isNoise(header, payload):
					(header,payload) = cap.next()
					continue

				# Metrics 0 and 1 (TLS headers)
				n = self.getTLSHeaders(payload)
				if self.isOnUplink(payload):
					metrics[0] += n
				else:
					metrics[1] += n

				# Metric 2 (total transmitted bytes)
				total_bytes += header.getlen()

				(header, payload) = cap.next()
			metrics[2] = (total_bytes - (total_bytes % 10000)) / 10000
		except pcapy.PcapError:
			pass
		return metrics

	# Returns the number of TLS headers in the payload matching the bytestring
	def getTLSHeaders(self, payload):
		bytestring = "\x17\x03[\x00\x01\x02\x03]\x02[\x30\x1a]"
		return len(re.findall(bytestring, payload))

	# Returns true if the supplied header indicates packet length of 66 (ACK etc) or if it is part of a TLS handshake
	def isNoise(self, header, payload):
		if header.getlen() == 66:
			return True
		elif len(re.findall("\x16\x03[\x00\x01\x02\x03]", payload)) > 0:
			return True
		return False
	
	# Returns true if the supplied payload is on the uplink, false if it is on the downlink
	def isOnUplink(self, payload):
		try:
			# Carve out src IP. Remove 14B ethernet header, 12B IP header start and 4B destination IP.
			ip_header = payload[26:30]
			src_ip = socket.inet_ntoa(ip_header)
			if src_ip == self.src_ip:
				return True
			return False
		except:
			return False

	def add(self, list1, list2):
		if list1 == None:
			return list2;
		elif list2 == None:
			return list1
		return [list1[i] + list2[i] for i in range(0,len(list1))]

	def avg(self, list):
		return [x / self.passes for x in list]

	def appendToFile(self, file_path, data):
		with open(file_path, "a+") as f:
			f.write(data)
			f.close()

if __name__ == "__main__":
	count = 10
	passes = 1
	in_path = "./10_js/"
	src_ip = "129.241.208.200"

	f = Fingerprint(count, passes, src_ip)
	f.makeFingerprints(in_path)