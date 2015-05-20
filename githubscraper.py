import os, json
import requests
import subprocess
from pprint import pprint

argument = ["curl", "-u", "sudheesh001:d4995195565835dda1900a850f2682dc7c5a6bc2"]
with open('product/data/github/glusterrepos.json') as json_file:
	data = json.load(json_file)

dataLen = len(data)
print dataLen

languagesURL = []

for glusterrepo in range(0,dataLen):
	temp = argument
	languagesURL.append(data[glusterrepo]["languages_url"])
	temp.append(data[glusterrepo]["languages_url"])
	temp.append('>')
	temp.append(data[glusterrepo]["name"])
	print temp
	subprocess.call(temp)
	temp.pop()
	temp.pop()
	temp.pop()


