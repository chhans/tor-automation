from selenium import webdriver
import subprocess
import time

# Change interface to the currently connected
iface = "en0"
N = int(input("Enter number of sites to visit: "))

# Makes request to the given address
def getPage(addr):
	print("Requesting %d: %s" % (i+1, addr))
	driver = webdriver.Firefox()
	driver.get("http://"+addr)
	driver.quit()

def capture():
	return subprocess.Popen("tshark -i %s -w ./captures/%d.cap" % (iface, i), shell=True)

# Opens the list of web sites to visit and parses the first N entries
with open("alexa.csv") as f:
	sites = [next(f) for x in xrange(N)]

for (i, addr) in enumerate(sites):
	trim_addr = addr.split(',', 1)[1][:-1]
	captureProcess = capture()
	getPage(trim_addr)
	captureProcess.terminate()