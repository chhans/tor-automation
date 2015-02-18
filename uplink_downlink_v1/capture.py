from selenium import webdriver
from torProfile import TorProfile
from random import randint
import subprocess
import os
import signal

from pyvirtualdisplay import Display

class Capture:

	def __init__(self, site_indices, passes, max_index):
		self.site_indices = site_indices
		self.passes = passes

		with open("alexa.csv", "r") as f:
			self.sites = [next(f) for x in xrange(max_index)]
			f.close()

	def startCapture(self, out_path, iface):
		self.clearPreviousData(out_path)

		display = Display(visible=0, size=(800, 600))
		display.start()

		for i, s in enumerate(self.site_indices):
			# Creates directories if they don't exist
			self.createDirectories(out_path)
			address = self.getAddress(s)
			self.updateCaptureList(out_path, address)
			for j in range(0, self.passes):
				file_name = "%d-%d.cap" % (i, j)
				file_path = "%scaptures/%s" % (out_path, file_name)
				
				tsharkProcess = self.capture(iface, file_path)
				self.getPage(address)
				os.killpg(tsharkProcess.pid, signal.SIGTERM)
		display.stop()

	def clearPreviousData(self, out_path):
		try:
			open("%scap.list" % out_path, "w").close()
		except:
			pass

	def updateCaptureList(self, out_path, data):
		file_path = "%scap.list" % out_path
		with open(file_path, "a+") as f:
			f.write("%s\n" % data)
			f.close()

	def createDirectories(self, out_path):
		if not os.path.exists("%scaptures/" % (out_path)):
			os.makedirs("%scaptures/" % out_path)

	def capture(self, iface, file_path):
		try:
			print file_path
			command = "tshark -f tcp -i %s -w %s" % (iface, file_path)
			return subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
		except:
			# TODO: Log
			return None

	def getAddress(self, i):
		return "http://"+self.sites[i].split(',', 1)[1][:-1]

	def getPage(self, addr):
		print "Requesting site %s" % addr
		driver = webdriver.Firefox(firefox_profile=TorProfile().p)
		driver.set_page_load_timeout(300)
		try:
			driver.get(addr)
		except:
			pass
			# TODO: Log
		driver.quit()

if __name__ == "__main__":
	passes = 1
	site_number = 10
	max_index = 100
	random = True

	out_path = "./10_nojs/"
	iface = "eth1"

	site_indices = [0]*site_number
	if random:
		for i in range(0, site_number):
			site_indices[i] = randint(0, max_index-1)
	else:
		site_indices = range(0, site_number)

	site_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

	c = Capture(site_indices, passes, max_index)
	c.startCapture(out_path, iface)