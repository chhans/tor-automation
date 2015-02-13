from selenium import webdriver
from torProfile import TorProfile
from analysis import Analysis
from random import randint
import subprocess
import os
import signal
import pyshark
import re
import datetime

class Fingerprint:

	def __init__(self, site_indices, random, passes, max_index, src_ip):
		self.site_indices = site_indices
		self.random = random
		self.passes = passes
		self.src_ip = src_ip

		with open("alexa.csv", "r") as f:
			self.sites = [next(f) for x in xrange(max_index)]

	def makeFingerprints(self, out_path, iface):
		# makes requests and captures traffic, then produce the traffic metrics for that request
		for i, s in enumerate(self.site_indices):
			totalMetrics = None
			for j in range(0, self.passes):
				file_name = "%d-%d.cap" % (i, j)
				file_path = "%scaptures/%s" % (out_path, file_name)
				captureProcess = self.capture(iface, file_path)
				self.getPage(self.getAddress(s))
				os.killpg(captureProcess.pid, signal.SIGTERM)

				metrics = self.analyze(file_path)
				print "Metrics for %s: %s" % (file_path, metrics)
				if totalMetrics == None:
					totalMetrics = metrics
				else:
					totalMetrics = self.add(totalMetrics, metrics)
			totalMetrics = self.avg(totalMetrics)

			print "Trace for site %d: %s" % (i, totalMetrics)
			trace_str = "%s\n" % ", ".join( str(x) for x in totalMetrics )
			self.appendToFile("%straces" % out_path, trace_str)
			#with open("./fingerprints/traces", "a+") as f:
			#	f.write(", ".join( str(x) for x in totalMetrics ))
			#	f.write("\n")

	def getAddress(self, i):
		return "http://"+self.sites[i].split(',', 1)[1][:-1]

	def getPage(self, addr):
		print "Requesting site %s" % addr
		driver = webdriver.Firefox(firefox_profile=TorProfile().p)
		driver.set_page_load_timeout(300)
		try:
			driver.get(addr)
		except:
			self.log("Error: %s" % addr)
		driver.quit()

	def capture(self, iface, file_path):
		command = "tshark -f tcp -i %s -w %s" % (iface, file_path)
		return subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

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
				return len(re.findall("17030[0123]0230", p.data.data))
			elif p.highest_layer == "SSL":
				if p.ssl.record_length == "560":
					return 1
			return 0
		except:
			return 0

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

	def log(self, data):
		self.appendToFile("./log.dat", "%s:\t%s\n" % (datetime.datetime.now(), data))

	def add(self, list1, list2):
		return [list1[i] + list2[i] for i in range(0,len(list1))]

	def avg(self, list):
		return [x / self.passes for x in list]


if __name__ == "__main__":
	passes = 1
	site_number = 10
	max_index = 10
	random = True
	out_path = "./test/"
	iface = "eth1"
	src_ip = "129.241.208.200"

	site_indices = [0]*site_number
	if random:
		for i in range(0, site_number):
			site_indices[i] = randint(0, max_index-1)
	else:
		site_indices = range(0, site_number)

	f = Fingerprint(site_indices, random, passes, max_index, src_ip)
	f.makeFingerprints(out_path, iface)