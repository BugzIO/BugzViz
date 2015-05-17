import os,binascii
import requests, urllib2, urllib, json
from pprint import pprint

redHatProductsList = [line.strip().replace(" ", "%20") for line in open('product/products1.txt')]
requestURLs = []
for eachProduct in redHatProductsList:
	filename = "product/data/"+eachProduct+".json"
	print filename
	url = "https://bugzilla.redhat.com/jsonrpc.cgi?method=Bug.search&params=[{\"product\":\""+eachProduct+"\"}]"
	requestURLs.append(url)
	print url
	data = json.load(urllib2.urlopen(url))
	with open(filename, "w") as f:
		json.dump(data, f)
