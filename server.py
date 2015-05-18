# all the imports
import os,binascii
from flask import Flask, request, session, g, redirect, url_for, abort, \
		render_template, flash, Blueprint
from flaskext.mysql import MySQL
from flask_mail import Mail,Message
from config import config, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
from werkzeug.utils import secure_filename
from flask import send_from_directory
import datetime, json
from pprint import pprint
from collections import Counter
import re, datetime
import urllib2, urllib
from bs4 import BeautifulSoup
import requests, chartkick
 
import logging
from logging.handlers import SMTPHandler
credentials = None

mysql = MySQL()
# create our little application :)

app = Flask(__name__)

for key in config:
	app.config[key] = config[key]

mail = Mail(app)
# Mail
mail.init_app(app)

if MAIL_USERNAME or MAIL_PASSWORD:
	credentials = (MAIL_USERNAME, MAIL_PASSWORD)
	mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'resetpass', credentials)
	mail_handler.setLevel(logging.ERROR)
	app.logger.addHandler(mail_handler)

mysql.init_app(app)
app.config.from_object(__name__)
ck = Blueprint('ck_page', __name__, static_folder=chartkick.js(), static_url_path='/static')
app.register_blueprint(ck, url_prefix='/ck')
app.jinja_env.add_extension("chartkick.ext.charts")

def tup2float(tup):
	return float('.'.join(str(x) for x in tup))

def get_cursor():
	return mysql.connect().cursor()

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.djt'), 404

@app.route('/charts')
def charts():
	redHatProductsList = [line.strip().replace(" ", "%20") for line in open('product/productRevised.txt')]
	createdTime = []
	status = []
	assignedTo = []
	reportedBy = []
	monthYear = []
	Year = []
	month = []
	for eachProduct in redHatProductsList:
		print eachProduct + ' request Started'
		filepath = 'product/data/'+eachProduct+'.json'
		with open(filepath) as json_file:
			data = json.load(json_file)
		print eachProduct + ' Request Complete'
		result = data["result"]["bugs"]
		for objects in result:
			bugDateTime = datetime.datetime.strptime(objects["creation_time"], '%Y-%m-%dT%H:%M:%SZ').date().strftime('%m/%d/%Y')
			createdTime.append(bugDateTime)
			monthYear.append(datetime.datetime.strptime(objects["creation_time"], '%Y-%m-%dT%H:%M:%SZ').date().strftime('%m/%Y'))
			Year.append(datetime.datetime.strptime(objects["creation_time"], '%Y-%m-%dT%H:%M:%SZ').date().strftime('%Y'))
			status.append(objects["status"])
			assignedTo.append(objects["assigned_to"])
			reportedBy.append(objects["creator"])
	counterData = dict(list(Counter(createdTime).items()))
	statusCount = dict(list(Counter(status).items()))
	monthYearCount = dict(list(Counter(monthYear).items()))
	YearCount = dict(list(Counter(Year).items()))
	data = []
	for key, value in statusCount.iteritems():
		temp = []
		temp.append(key.encode('ascii','ignore'))
		temp.append(value)
		data.append(temp)
	timeInfo = []
	for key, value in counterData.iteritems():
		temp = []
		temp.append(key.encode('ascii','ignore'))
		temp.append(value)
		timeInfo.append(temp)
	monthYearInfo = []
	for key, value in monthYearCount.iteritems():
		temp = []
		temp.append(key.encode('ascii','ignore'))
		temp.append(value)
		monthYearInfo.append(temp)
	YearInfo = []
	for key, value in YearCount.iteritems():
		temp = []
		temp.append(key.encode('ascii','ignore'))
		temp.append(value)
		YearInfo.append(temp)
	return render_template('chart.djt', statusData = data, timeInfo=timeInfo, monthYearInfo=monthYearInfo, YearInfo=YearInfo)

@app.route('/leaderboard')
def leaderboard():
	redHatProductsList = [line.strip().replace(" ", "%20") for line in open('product/productRevised.txt')]
	assignedTo = []
	reportedBy = []
	no_of_bugs = 0
	for eachProduct in redHatProductsList:
		print eachProduct + ' request Started'
		filepath = 'product/data/'+eachProduct+'.json'
		with open(filepath) as json_file:
			data = json.load(json_file)
		print eachProduct + ' Request Complete'
		result = data["result"]["bugs"]
		no_of_bugs += len(result)
		for objects in result:
			assignedTo.append(objects["assigned_to"])
			reportedBy.append(objects["creator"])
	AssignedList = list(Counter(assignedTo).most_common())
	reporterList = list(Counter(reportedBy).most_common())
	noOfAssignees = len(set(AssignedList))
	noOfReporters = len(set(reporterList))
	return render_template('leaderboard.djt', AssignedList=AssignedList, noOfAssignees=noOfAssignees, reporterList=reporterList, noOfReporters=noOfReporters, no_of_bugs=no_of_bugs)

@app.route('/components')
def components():
	redHatProductsList = [line.strip().replace(" ", "%20") for line in open('product/productRevised.txt')]
	components = []
	for eachProduct in redHatProductsList:
		print eachProduct + ' request Started'
		filepath = 'product/data/'+eachProduct+'.json'
		with open(filepath) as json_file:
			data = json.load(json_file)
		print eachProduct + ' Request Complete'
		result = data["result"]["bugs"]
		for objects in result:
			for component in objects["component"]:
				components.append(component)
	noOfComponents = len(list(set(components)))
	componentList = list(Counter(components).most_common())
	colors = ['aqua','green','blue','yellow','purple','orange','red']
	return render_template('components.djt', noOfComponents=noOfComponents, components=componentList, colors=colors)

@app.route('/')
def screen():
	redHatProductsList = [line.strip().replace(" ", "%20") for line in open('product/productRevised.txt')]
	requestURLs = []
	assignedTo = []
	severity = []
	qaContacts = []
	bugTimeline = []
	ccList = []
	components = []
	bugStatus = []
	no_of_bugs = 0
	for eachProduct in redHatProductsList:
		print eachProduct + ' request Started'
		filepath = 'product/data/'+eachProduct+'.json'
		with open(filepath) as json_file:
			data = json.load(json_file)
		print eachProduct + ' Request Complete'
		result = data["result"]["bugs"]
		no_of_bugs += len(result)
		for objects in result:
			assignedTo.append(objects["assigned_to"])
			qaContacts.append(objects["qa_contact"])
			severity.append(objects["severity"])
			bugStatus.append(objects["status"])
			for members in objects["cc"]:
				ccList.append(members)
			for component in objects["component"]:
				components.append(component)
			temp = []
			temp.append(objects["id"])
			temp.append(datetime.datetime(*map(int, re.split('[^\d]', objects["creation_time"])[:-1])))
			bugTimeline.append(temp)
	noOfPeopleAssigned = len(list(set(assignedTo)))
	noOfQAContacts = len(list(set(qaContacts)))
	severityList = list(Counter(severity).items())
	statusList = list(Counter(bugStatus).items())
	with open('redhatRepos.json') as data:
		repoData = json.load(data)
	repoResult = repoData.keys()
	repoResult.sort()
	noOfRepos = len(repoResult)
	noOfCCParticipants = len(list(set(ccList)))
	noOfComponents = len(list(set(components)))
	componentList = list(Counter(components).items())
	print componentList
	return render_template('index.djt', noOfBugs=no_of_bugs, noOfPeopleAssigned=noOfPeopleAssigned, bugIds=bugTimeline, severityList=severityList, noOfQAContacts=noOfQAContacts, noOfRepos=noOfRepos, repoResult=repoResult, noOfCCParticipants=noOfCCParticipants, noOfComponents=noOfComponents, statusList=statusList)

@app.teardown_appcontext
def close_db():
	"""Closes the database again at the end of the request."""
	get_cursor().close()

if __name__ == '__main__':
	app.debug = True
	app.secret_key=os.urandom(24)
	# app.permanent_session_lifetime = datetime.timedelta(seconds=200)
	app.run(host='0.0.0.0', port=8080)