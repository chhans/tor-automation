from selenium import webdriver
from torProfile import TorProfile
import config
import subprocess
import time

N = int(input("Enter number of sites to visit: "))

# Makes request to the given address
def getPage(addr):
	print("Requesting %d: %s" % (i+1, addr))
	driver = webdriver.Firefox(TorProfile().p)
	driver.get("http://"+addr)
	driver.quit()

def capture():
	return subprocess.Popen("tshark -i %s -w ./captures/%d.cap" % (config.iface, i), shell=True)

# Opens the list of web sites to visit and parses the first N entries
with open("alexa.csv") as f:
	sites = [next(f) for x in xrange(N)]

for (i, addr) in enumerate(sites):
	trim_addr = addr.split(',', 1)[1][:-1]
	captureProcess = capture()
	getPage(trim_addr)
	captureProcess.terminate()