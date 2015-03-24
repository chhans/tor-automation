import torProfile
from capture import Capture
from fingerprint import Fingerprint
from correlate import Correlate
from random import randint

iface = "eth1"
src_ip = "129.241.208.200"

def captureSetup(input_file, js_enabled, site_indices, out_path, passes, world_size):
	torProfile.js = js_enabled
	c = Capture(input_file, site_indices, passes, world_size)
	c.startCapture(out_path, iface)

def fingerprintSetup(count, passes, in_path):
	f = Fingerprint(count, passes, src_ip)
	f.makeFingerprints(in_path)

def correlateSetup(fingerprint_path, capture_path):
	c = Correlate(fingerprint_path, capture_path)
	c.calculate()

if __name__ == "__main__":
	input_file = "censoredinchina.csv"
	js = False
	world_size = 100
	passes = 1

	cpath = "./repeat_10_cap/"
	pages = [1, 2, 4, 5, 7, 10, 11, 37, 41, 98]
	captureSetup(input_file, js, pages, cpath, passes, world_size)

	pages = range(0, 100)
	for i in range(0, 10):
		fpath = "./repeat_100_%s/" % i
		captureSetup(input_file, js, pages, fpath, passes, world_size)