import pyshark

def analyze(in_path):
	# metrics: [packets on uplink, packets on downlink]
	metrics = [0, 0]
	cap = pyshark.FileCapture(in_path)
	for p in cap:
		n = analyzePacket(p)
		i = metricIndex(p)
		if i != -1:
			metrics[i] += n
	return metrics

def analyzePacket(p):
	try:
		if p.highest_layer == "DATA":
			n = len(re.findall("17030[0123]0230", p.data.data))
			if n == 0:
				n = len(re.findall("17030[0123]021a", p.data.data))
			return n
		elif p.highest_layer == "SSL":
			if p.ssl.record_length == "560" or p.ssl.record_length == "543":
				return 1
		return 0
	except:
		return 0

def metricIndex(p):
	try:
		if p.ip.src == self.src_ip:
			# Packet on uplink
			return 0
		else:
			# Packet on downlink
			return 1
	except:
		# Ignores IPv6
		return -1

file_path = "./100/captures/37-0.cap"

print analyze(file_path)