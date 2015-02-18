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
		# metrics: [packets on uplink, packets on downlink]
		metrics = [0, 0]

		try:
			cap = pcapy.open_offline(in_path)
			(header, payload) = cap.next()
			while header:
				n = len(re.findall("\x17\x03[\x00\x01\x02\x03]\x02[\x30\x1a]", payload))
				i = self.metricIndex(payload)
				if i != -1:
					metrics[i] +=n
				(header, payload) = cap.next()
		except pcapy.PcapError:
			pass
		return metrics
	
	def metricIndex(self, payload):
		try:
			# Carve out src IP. Remove 14B ethernet header, 12B IP header start and 4B destination IP.
			ip_header = payload[26:30]
			src_ip = socket.inet_ntoa(ip_header)
			if src_ip == self.src_ip:
				# Packet on uplink
				return 0
			else:
				# Packet on downlink
				return 1
		except:
			# Ignore IPv6
			return 0

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