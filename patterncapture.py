from selenium import webdriver
from torProfile import TorProfile

import selenium
import subprocess
import os
import signal
import time
import sys
import random

sleep_time = 5.0
browse_time = 120.0 # TODO: Find good value. 2 minutes?
load_timeout = 120.0
iface = "eth1"
dump_path = "PatternDumps"

urls = ["http://cbsnews.com", "http://google.com/ncr", "http://nrk.no", "http://vimeo.com", "http://wikipedia.org", "http://youtube.com"]

def startProgress():
	global progress_x
	sys.stdout.write("Browsing web page: [" + "-"*40 + "]" + chr(8)*41)
	sys.stdout.flush()
	progress_x = 0

def progress(x):
	global progress_x
	x = int(x * 40 // 100)
	sys.stdout.write("#" * (x - progress_x))
	sys.stdout.flush()
	progress_x = x

def endProgress():
	sys.stdout.write("#" * (40 - progress_x) + "]\n\n")
	sys.stdout.flush()

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

def loadPage(url):
	print "Requesting site %s through Tor" % url
	driver = webdriver.Firefox(firefox_profile=TorProfile().p)
	driver.set_page_load_timeout(load_timeout)
	try:
		t = browse_time
		driver.get(url)
		print "Successfully reached %s\n" % url
		startProgress()
		while t > 0:
			progress( ((browse_time-t)/browse_time) * 100 )
			time.sleep(1)
			t -= 1
		endProgress()
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

def startTshark(f_path):
	print "Capturing on interface %s" % iface
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

def removeFile(f_path):
	os.remove(f_path)

def captureWebsite(url):
	# Create directory for URL
	folder = (url.split("://")[1]).split("/")[0]
	dir = "%s/%s" % (dump_path, folder)
	mkdir(dir)

	# Build file path for website visit instance and start capture
	f_path = "%s/%s" % (dir, getFilename(dir))
	tshark_pid = startTshark(f_path)
	try:
		s = loadPage(url)
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

def captureRandomlyFromList(number):
	with open("safelist.csv", "r") as f:
		sites = ["http://%s" % x.split(",")[1][:-1] for x in f]
		f.close()

	while number > 0:
		captureWebsite(sites[random.randint(0,len(sites)-1)])
		number -= 1

def openWorldList(n):
	with open("openlist.csv", "r") as f:
		sites = ["http://%s" % x.split(",")[1][:-1] for x in f]
		sites = sites[:n]
		f.close()
	return sites

if __name__=="__main__":
	closed_world = False
	n = 0

	try:
		model = sys.argv[1]
		if model == "closed":
			closed_world = True
		elif model == "open":
			closed_world = False
			n = int(sys.argv[2])
		else:
			raise
	except:
		print "Usage: python %s <open/closed> <number of visits (given open world)>" % sys.argv[0]
		sys.exit()

	if closed_world:
		dump_path += "/closed"
		for url in urls:
			captureWebsite(url)
	else:
		dump_path += "/open"
		urls = openWorldList(n)
		for url in urls:
			captureWebsite(url)