from random import randint

max_index = 4
site_number = 5
random = True

site_indices = [0]*site_number

if random:
	for i in range(0, site_number):
		site_indices[i] = randint(0, max_index)
else:
	site_indices = range(0, site_number)

print site_indices


with open("alexa.csv", "r") as f:
	sites = [next(f) for x in xrange(max_index)]

for i in site_indices:
	print "http://"+sites[i].split(',', 1)[1][:-1]