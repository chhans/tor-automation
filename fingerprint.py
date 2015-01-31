from selenium import webdriver

#TODO: Make sure scripts and add-ons are disabled and Tor is enabled

num_sites = int(input("Enter number of sites to visit: "))

with open("alexa.csv") as siteFile:
	site_list = [next(siteFile) for x in xrange(num_sites)]

for (i, address) in enumerate(site_list):
	trimmed_address = address.split(',' , 1)[1][:-1]
	print("Requesting %d: %s" % (i+1, trimmed_address))
	browser = webdriver.Firefox()
	browser.get("http://"+trimmed_address)

#browser.get('http://vg.no/')