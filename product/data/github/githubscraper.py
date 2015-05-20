import os, json
import requests
import subprocess
from pprint import pprint

argument = ["curl", "-u", "sudheesh001:d4995195565835dda1900a850f2682dc7c5a6bc2"]
with open('openstackrepos.json') as json_file:
	data = json.load(json_file)

dataLen = len(data)
print dataLen

languagesURL = []

for glusterrepo in range(0,dataLen):
	temp = argument
	temp.append(data[glusterrepo]["languages_url"])
	print temp
	f = open(data[glusterrepo]["name"], "w")
	subprocess.call(temp, stdout=f)
	temp.pop()


