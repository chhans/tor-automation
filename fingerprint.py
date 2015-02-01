from selenium import webdriver
import subprocess
import time

# Device specific variables
iface = "en0"

# Firefox profile with Tor
profile = webdriver.FirefoxProfile()
profile.set_preference('network.proxy.type', 1)
profile.set_preference('network.proxy.socks', '127.0.0.1')
profile.set_preference('network.proxy.socks_port', 9050)
#profile.set_preference('javascript.enabled', False)

N = int(input("Enter number of sites to visit: "))

# Makes request to the given address
def getPage(addr):
	print("Requesting %d: %s" % (i+1, addr))
	driver = webdriver.Firefox(profile)
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