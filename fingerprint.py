import pyshark
import re

class Fingerprint:

	def __init__(self, count, passes, src_ip):
		self.count = count
		self.passes = passes
		self.src_ip = src_ip

	def makeFingerprints(self, in_path):
		self.clearPreviousData(in_path)
		totalStr = ""
		for i in range(0, count):
			totalMetrics = None
			for j in range(0, passes):
				file_path = "%scaptures/%d-%d.cap" % (in_path, i, j)

				metrics = self.analyze(file_path)
				totalMetrics = self.add(totalMetrics, metrics)

			totalMetrics = self.avg(totalMetrics)
			print "Trace for site %d: %s" % (i, totalMetrics)
			totalStr += "%s\n" % ", ".join( str(x) for x in totalMetrics )
		self.appendToFile("%straces" % in_path, totalStr)

	def clearPreviousData(self, in_path):
		try:
			open("%straces" % in_path, "w").close()
		except:
			pass

	def analyze(self, in_path):
		# metrics: [packets on uplink, packets on downlink]
		metrics = [0, 0]
		cap = pyshark.FileCapture(in_path)
		for p in cap:
			n = self.analyzePacket(p)
			i = self.metricIndex(p)
			if i != -1:
				metrics[i] += n
		return metrics
	
	def analyzePacket(self, p):
		try:
			if p.highest_layer == "DATA":
				n = len(re.findall("17030[0123]0230", p.data.data))
				if n == 0:
					n = len(re.findall("17030[0123]021a", p.data.data))
				return n
			elif p.highest_layer == "SSL":
				if p.ssl.record_length == "560" or p.ssl.record_length == "543":
					return 1
			return 0
		except:
			return 0

	def add(self, list1, list2):
		if list1 == None:
			return list2;
		elif list2 == None:
			return list1
		return [list1[i] + list2[i] for i in range(0,len(list1))]

	def avg(self, list):
		return [x / self.passes for x in list]

	def metricIndex(self, p):
		try:
			if p.ip.src == self.src_ip:
				# Packet on uplink
				return 0
			else:
				# Packet on downlink
				return 1
		except:
			# Ignores IPv6
			return -1

	def appendToFile(self, file_path, data):
		with open(file_path, "a+") as f:
			f.write(data)
			f.close()

if __name__ == "__main__":
	count = 100
	passes = 1
	in_path = "./100/"
	src_ip = "192.168.1.5"

	f = Fingerprint(count, passes, src_ip)
	f.makeFingerprints(in_path)