# For the profile to function, make sure Tor is running on the correct port.
# For minimum noise, javascript is disabled.
from selenium import webdriver

js = False

class TorProfile(webdriver.FirefoxProfile):

	def __init__(self):
		self.p = webdriver.FirefoxProfile()
		self.p.set_preference('network.proxy.type', 1)
		self.p.set_preference('network.proxy.socks', '127.0.0.1')
		self.p.set_preference('network.proxy.socks_port', 9050)
		self.p.set_preference('javascript.enabled', js)