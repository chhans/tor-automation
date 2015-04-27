from selenium import webdriver
from torProfile import TorProfile
from pyvirtualdisplay import Display

import selenium
from random import randint
import subprocess
import os
import signal
import sys
import time

#class Capture:
#
#	def __init__(self, input_file, site_indices, passes, max_index):
#		self.site_indices = site_indices
#		self.passes = passes
#
#		with open(input_file, "r") as f:
#			self.sites = [next(f) for x in xrange(max_index)]
#			f.close()
#
#	def __init():
#
#
#	def startCapture(self, out_path, iface):
#		self.clearPreviousData(out_path)
#
#		display = Display(visible=0, size=(800, 600))
#		display.start()
#
#		for i, s in enumerate(self.site_indices):
#			# Creates directories if they don't exist
#			self.createDirectories(out_path)
#			address = self.getAddress(s)
#			self.updateCaptureList(out_path, address)
#			for j in range(0, self.passes):
#				file_name = "%d-%d.cap" % (i, j)
#				file_path = "%scaptures/%s" % (out_path, file_name)
#				
#				tsharkProcess = self.capture(iface, file_path)
#				self.getPage(address)
#				os.killpg(tsharkProcess.pid, signal.SIGTERM)
#		display.stop()
#
#	def clearPreviousData(self, out_path):
#		try:
#			open("%scap.list" % out_path, "w").close()
#		except:
#			pass
#
#	def updateCaptureList(self, out_path, data):
#		file_path = "%scap.list" % out_path
#		with open(file_path, "a+") as f:
#			f.write("%s\n" % data)
#			f.close()
#
#	def createDirectories(self, out_path):
#		if not os.path.exists("%scaptures/" % (out_path)):
#			os.makedirs("%scaptures/" % out_path)
#
#	def capture(self, iface, file_path):
#		try:
#			print file_path
#			command = "tshark -f tcp -i %s -w %s" % (iface, file_path)
#			return subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
#		except:
#			# TODO: Log
#			return None
#
#	def getAddress(self, i):
#		return "http://"+self.sites[i].split(',', 1)[1][:-1]
#
#	def getPage(self, addr):
#		print "Requesting site %s" % addr
#		driver = webdriver.Firefox(firefox_profile=TorProfile().p)
#		driver.set_page_load_timeout(300)
#		try:
#			driver.get(addr)
#		except:
#			pass
#			# TODO: Log
#		driver.quit()

training_data = "Dumps/training/"
experiment_data = "Dumps/experiment/"
iface = "eth1"
sleep_time = 2.0
load_timeout = 120.0

def createPageList(in_file, n, random):
	with open(in_file, "r") as f:
		if random:
			sites = [""]*n
			all_sites = [next(f).split(",")[1].rstrip() for x in xrange(1000)]
			for i in range(n):
				sites[i] = all_sites[randint(0, n-1)]
		else:
			sites = [next(f).split(",")[1].rstrip() for x in xrange(n)]
		f.close()
	return sites

def mkdir(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)

def getFilename(dir):
	max_i = -1
	try:
		max_i = max([int(x.split(".")[0]) for x in os.listdir(dir)])
	except:
		pass
	return "%d.cap" % (max_i + 1)

def startTshark(f_path):
	command = "tshark -f tcp -i %s -w %s" % (iface, f_path)
	FNULL = open(os.devnull, 'w')
	tshark_proc = subprocess.Popen(command, stdout=FNULL, close_fds=True, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
	return tshark_proc.pid

def stopTshark(pid):
	try:
		os.killpg(pid, signal.SIGTERM)
	except:
		print "Could not stop tshark process"
		FNULL = open(os.devnull, 'w')
		subprocess.Popen("killall tshark", stdout=FNULL, close_fds=True, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

def loadPage(url):
	driver = webdriver.Firefox(firefox_profile=TorProfile().p)
	driver.set_page_load_timeout(load_timeout)
	try:
		driver.get("http://"+url)
		driver.close()
		time.sleep(sleep_time)
	except selenium.common.exceptions.TimeoutException:
		print "Error lading page: timed out"
		time.sleep(sleep_time)
		driver.close()
		return -1
	except (KeyboardInterrupt, SystemExit):
		driver.close()
		raise
	except:
		print "Unexpected error when loading page:", sys.exc_info()[0]
		time.sleep(sleep_time)
		driver.close()
		raise

def removeFile(f_path):
	os.remove(f_path)

def capturePage(folder, page):
	# Create directory for page
	folder = folder + page.split("/")[0]
	mkdir(folder)

	f_path = "%s/%s" % (folder, getFilename(folder))
	tshark_pid = startTshark(f_path)
	try:
		s = loadPage(page)
		stopTshark(tshark_pid)
		if s == -1:
			removeFile(f_path)
	except (KeyboardInterrupt, SystemExit):
		stopTshark(tshark_pid)
		removeFile(f_path)
		sys.exit()
	except:
		print "Unexpected error when capturing website:", sys.exc_info()[0]
		stopTshark(tshark_pid)
		removeFile(f_path)
		raise

if __name__ == "__main__":
	manual = False
	try:
		plist = sys.argv[1]
		if plist == "manual":
			manual = True
		elif not os.path.isfile(plist):
			print "ERROR: File %s not found" % plist
			raise
		else:
			n = int(sys.argv[2])		
			iface = sys.argv[3]
			t = int(sys.argv[4])
	except:
		print "Usage:\tpython %s <web page list> <number of pages to visit> <network interface> <training data (0/1)> OR" % sys.argv[0]
		print "\tpython %s manual <network interface> <training_data (0/1)> <web page(s)>" % sys.argv[0]
		print "Example: python %s alexa.csv 100 eth1 1 (capture training data from the first 100 pages of list alexa.csv on eth1)" % sys.argv[0]
		sys.exit()

	if manual:
		iface = sys.argv[2]
		t = int(sys.argv[3])
		page_list = []
		cnt = 4
		while True:
			try:
				page_list.append(sys.argv[cnt])
				cnt += 1
			except:
				break
	else:
		page_list = createPageList(plist, n, False)

	display = Display(visible=0, size=(800, 600))
	display.start()

	p = training_data if t else experiment_data

	for i,page in enumerate(page_list):
		print "Capturing web page %d/%d: %s" % (i+1, len(page_list), page)
		capturePage(p, page)

	display.stop()