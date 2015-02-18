import torProfile
from capture import Capture
from fingerprint import Fingerprint
from correlate import Correlate

# Some blocked websites in china in addition to baidu, tumblr, netflix and nytimes
# google, facebook, youtube, baidu, twitter, instagram, tumblr, netflix, bbc.co.uk, nytimes
test_pages = [0, 1, 2, 3, 7, 24, 30, 56, 71, 98]
iface = "eth1"
src_ip = "129.241.208.200"

def captureSetup(js_enabled, site_indices, out_path, passes, world_size):
	torProfile.js = js_enabled
	c = Capture(site_indices, passes, world_size)
	c.startCapture(out_path, iface)

def fingerprintSetup(count, passes, in_path):
	f = Fingerprint(count, passes, src_ip)
	f.makeFingerprints(in_path)

def correlateSetup(fingerprint_path, capture_path):
	c = Correlate(fingerprint_path, capture_path)
	c.calculate()

if __name__ == "__main__":
	# Experiment no. 1
	# Javascript 	disabled
	# World size	100 (closed)
	# Passes 		3
	# Captured		test_pages
	fpath = "./100_nojs/"
	cpath = "./10_nojs/"
	passes = 3
	pages = range(0, 100)
	js = False
	world_size = 100

	#captureSetup(js, pages, fpath, passes, world_size)
	#fingerprintSetup(len(pages), passes, fpath)

	passes = 1
	pages = test_pages

	#captureSetup(js, pages, cpath, passes, world_size)
	#fingerprintSetup(len(pages), passes, cpath)

	#correlateSetup(fpath, cpath)

	# Experiment no. 2
	# Javascript 	enabled
	# World size 	100 (closed)
	# Passes 		3
	# Captured		testPages
	fpath = "./100_js/"
	cpath = "./10_js/"
	passes = 3
	pages = range(0, 100)
	js = True

	#captureSetup(js, pages, fpath, passes, world_size)
	#fingerprintSetup(len(pages), passes, fpath)

	passes = 1
	pages = test_pages

	#captureSetup(js, pages, cpath, passes, world_size)
	#fingerprintSetup(len(pages), passes, cpath)

	correlateSetup(fpath, cpath)