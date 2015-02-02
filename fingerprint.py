from selenium import webdriver
from torProfile import TorProfile
import config as c
import subprocess
import time
from random import randint

# Makes request to the given address
def getPage(addr):
	print("Requesting %d: %s" % (i+1, addr))
	driver = webdriver.Firefox(TorProfile().p)
	driver.get(addr)
	driver.quit()

def capture():
	return subprocess.Popen("tshark -i %s -w ./captures/%d.cap" % (c.iface, i), shell=True)

# Opens the list of web sites included in the experiments
with open("alexa.csv") as f:
	sites = [next(f) for x in xrange(max(c.N, c.M))]

# Pick out the indices of the sites to visit
siteIndices = [0]*c.N
if c.R:
	for i in range(0,c.N):
		siteIndices[i] = randint(0,c.M)
else:
	siteIndices = range(0,c.N)

for i in siteIndices:
	address = "http://"+sites[i].split(',', 1)[1][:-1]
	captureProcess = capture()
	getPage(address)
	captureProcess.terminate()