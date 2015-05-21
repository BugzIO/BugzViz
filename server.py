# all the imports
import os,binascii
from flask import Flask, request, session, g, redirect, url_for, abort, \
		render_template, flash, Blueprint
from flaskext.mysql import MySQL
from flask_mail import Mail,Message
from config import config, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, AUTH_TOKEN
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

# Global Load lists
redHatProductsList = [line.strip().replace(" ", "%20") for line in open('product/productRevised.txt')]
createdTime = []
status = []
assignedTo = []
reportedBy = []
monthYear = []
Year = []
month = []
assignedTo = []
reportedBy = []
platforms = []
components = []
no_of_bugs = 0
requestURLs = []
severity = []
qaContacts = []
bugTimeline = []
ccList = []
bugStatus = []
classification = []
BugStatusMap = []
severityMap = []

# External Folders path

CONTRIBUTORS_PATH = 'product/data/github/contributorsCommits'
LANGUAGES_PATH = 'product/data/github/languages'
GITHUB_PATH = 'product/data/github'

GLUSTER_REPOS = GITHUB_PATH+'/glusterrepos.json'
GLUSTER_MEMBERS = GITHUB_PATH+'/glustermembers.json'
OPENSTACK_REPOS = GITHUB_PATH+'/openstackrepos.json'
OPENSTACK_MEMBERS = GITHUB_PATH+'/openstackmembers.json'

contributorFiles = os.listdir(CONTRIBUTORS_PATH)
languageFiles = os.listdir(LANGUAGES_PATH)

pprint(contributorFiles)
pprint(languageFiles)
## Files list loaded

print "Server is setting up, please wait... Querying the required information\n\n"
for eachProduct in redHatProductsList:
	print eachProduct + ' request Started'
	filepath = 'product/data/'+eachProduct+'.json'
	with open(filepath) as json_file:
		data = json.load(json_file)
	print eachProduct + ' Request Complete'
	result = data["result"]["bugs"]
	no_of_bugs += len(result)
	for objects in result:
		bugDateTime = datetime.datetime.strptime(objects["creation_time"], '%Y-%m-%dT%H:%M:%SZ').date().strftime('%m/%d/%Y')
		createdTime.append(bugDateTime)
		monthYear.append(datetime.datetime.strptime(objects["creation_time"], '%Y-%m-%dT%H:%M:%SZ').date().strftime('%m/%Y'))
		Year.append(datetime.datetime.strptime(objects["creation_time"], '%Y-%m-%dT%H:%M:%SZ').date().strftime('%Y'))
		status.append(objects["status"])
		assignedTo.append(objects["assigned_to"])
		reportedBy.append(objects["creator"])
		assignedTo.append(objects["assigned_to"])
		reportedBy.append(objects["creator"])
		platforms.append(objects["platform"])
		for component in objects["component"]:
			components.append(component)
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
		Mapper = []
		Mapper.append(objects["id"])
		Mapper.append(objects["creator"])
		Mapper.append(objects["creation_time"])
		Mapper.append(objects["product"])
		Mapper.append(objects["component"])
		Mapper.append(objects["severity"])
		Mapper.append(objects["status"])
		BugStatusMap.append(Mapper)
		classification.append(objects["classification"])

# Filters
## BugStatusMap => Has the status of all the bugs
## Contains severity and status

print "The server is now Online.\n You can access the server at localhost:8080"

def tup2float(tup):
	return float('.'.join(str(x) for x in tup))

def get_cursor():
	return mysql.connect().cursor()

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.djt'), 404

@app.route('/status/<status>')
def statusfunc(status=None):
	param = status
	statusRelated = []
	severityStatusRelated = []
	componentStatusRelated = []
	productStatusRelated = []
	creatorStatusRelated = []
	severityInfo = {}
	componentInfo = {}
	productInfo = {}
	creatorInfo = {}
	for bugObject in BugStatusMap:
		if bugObject[6] == param:
			statusRelated.append(bugObject)
			severityStatusRelated.append(bugObject[5])
			for component in bugObject[4]:
				componentStatusRelated.append(component)
			productStatusRelated.append(bugObject[3])
			creatorStatusRelated.append(bugObject[1])
	pprint(statusRelated)
	severityCounter = dict(list(Counter(severityStatusRelated).items()))
	componentCounter = dict(list(Counter(componentStatusRelated).items()))
	productCounter = dict(list(Counter(productStatusRelated).items()))
	creatorCounter = dict(list(Counter(creatorStatusRelated).items()))
	for key, value in severityCounter.iteritems():
		severityInfo[str(key)] = value
	for key, value in componentCounter.iteritems():
		componentInfo[str(key)] = value
	for key, value in productCounter.iteritems():
		productInfo[str(key)] = value
	for key, value in creatorCounter.iteritems():
		creatorInfo[key.encode('ascii','ignore')] = value
	severityInfoList = [ [k,v] for k,v in severityInfo.items() ]
	componentInfoList = [ [k,v] for k,v in componentInfo.items() ]
	productInfoList = [ [k,v] for k,v in productInfo.items() ]
	creatorInfoList = [ [k,v] for k,v in creatorInfo.items() ]
	return render_template('status.djt',creatorInfoList=creatorInfoList,productInfo=productInfo,componentInfo=componentInfo,severityInfo=severityInfo, status=status)

@app.route('/severity/<severity>')
def severityfunc(severity=None):
	param = severity
	severityRelated = []
	statusRelated = []
	componentRelated = []
	productRelated = []
	creatorRelated = []
	statusInfo = {}
	componentInfo = {}
	productInfo = {}
	creatorInfo = {}
	for bugObject in BugStatusMap:
		if bugObject[5] == param:
			severityRelated.append(bugObject)
			statusRelated.append(bugObject[6])
			for component in bugObject[4]:
				componentRelated.append(component)
			productRelated.append(bugObject[3])
			creatorRelated.append(bugObject[1])
	statusCounter = dict(list(Counter(statusRelated).items()))
	componentCounter = dict(list(Counter(componentRelated).items()))
	productCounter = dict(list(Counter(productRelated).items()))
	creatorCounter = dict(list(Counter(componentRelated).items()))
	for key, value in statusCounter.iteritems():
		statusInfo[key.encode('ascii','ignore')] = value
	for key, value in componentCounter.iteritems():
		componentInfo[key.encode('ascii','ignore')] = value
	for key, value in productCounter.iteritems():
		productInfo[key.encode('ascii','ignore')] = value
	for key, value in creatorCounter.iteritems():
		creatorInfo[key.encode('ascii','ignore')] = value
	return render_template('severity.djt', statusInfo=statusInfo, componentInfo=componentInfo, productInfo=productInfo, creatorInfo=creatorInfo, severity=severity)

@app.route('/github')
def github():
	IndividualContributions = {}
	repoWiseContributions = {}
	with open(GLUSTER_REPOS) as gluster_data:
		data = json.load(gluster_data)
	with open(OPENSTACK_REPOS) as open_stack_data:
		openstack_data = json.load(open_stack_data)
	with open(GLUSTER_MEMBERS) as gluster_members:
		memberData = json.load(gluster_members)
	with open(OPENSTACK_MEMBERS) as openstack_members:
		openstackmemberData = json.load(openstack_members)
	for dataFile in contributorFiles:
		filename = CONTRIBUTORS_PATH+'/'+dataFile
		noOfCommits = 0
		with open(filename) as contribData:
			contributions = json.load(contribData)
		for objects in contributions:
			noOfCommits += objects["contributions"]
			IndividualContributions[str(objects["login"])] = objects["contributions"]
		repoWiseContributions[str(dataFile)] = noOfCommits

	# Need to filter these from repoWise Contributions
	OPENSTACKREPOLIST = []
	GLUSTERFSREPOLIST = []
	for objects in openstack_data:
		OPENSTACKREPOLIST.append(objects["name"])
	for objects in data:
		GLUSTERFSREPOLIST.append(objects["name"])
	openstackContributions = {}
	glusterfsContributions = {}
	openstacklanguageInfo = {}
	glusterfslanguageInfo = {}
	OPENSTACKCOMMITS = 0
	GLUSTERFSCOMMITS = 0
	# openStack and gluster repos present at openstack_data and data
	for key, value in repoWiseContributions.iteritems():
		if key in OPENSTACKREPOLIST:
			openstackContributions[str(key)] = value
			OPENSTACKCOMMITS += value
		else:
			glusterfsContributions[str(key)] = value
			GLUSTERFSCOMMITS += value

	for dataFile in OPENSTACKREPOLIST:
		filename = LANGUAGES_PATH+'/'+dataFile
		with open(filename) as json_data:
			languageData = json.load(json_data)
		for key, value in languageData.iteritems():
			if key in openstacklanguageInfo:
				val = openstacklanguageInfo[key]
				newval = val + value
				openstacklanguageInfo[str(key)] = newval
			else:
				openstacklanguageInfo[str(key)] = value

	for dataFile in GLUSTERFSREPOLIST:
		filename = LANGUAGES_PATH+'/'+dataFile
		with open(filename) as json_data:
			languageData = json.load(json_data)
		for key, value in languageData.iteritems():
			if key in glusterfslanguageInfo:
				val = glusterfslanguageInfo[key]
				newval = val + value
				glusterfslanguageInfo[str(key)] = newval
			else:
				glusterfslanguageInfo[str(key)] = value

	pprint(glusterfslanguageInfo)
	pprint(openstacklanguageInfo)

	NoOfRepos = len(data)
	NoOfMembers = len(memberData)
	MemberInfo = []
	OpenStackMemberInfo = []
	forks = []
	for objects in data:
		forks.append(objects["fork"])
	for objects in memberData:
		temp = []
		temp.append(objects["login"])
		temp.append(objects["avatar_url"])
		MemberInfo.append(temp)
	for objects in openstackmemberData:
		temp = []
		temp.append(objects["login"])
		temp.append(objects["avatar_url"])
		OpenStackMemberInfo.append(temp)
	forkDict = dict(list(Counter(forks).items()))
	forkInfo = {}
	for key, value in forkDict.iteritems():
		forkInfo[str(key)] = value
	pprint(forkInfo)
	return render_template('github.djt', forkInfo=forkInfo, MemberInfo=MemberInfo, OpenStackMemberInfo=OpenStackMemberInfo, OPENSTACKCOMMITS=OPENSTACKCOMMITS, NoOfRepos=NoOfRepos, repoWiseContributions=repoWiseContributions, IndividualContributions=IndividualContributions, openstackContributions=openstackContributions, glusterfsContributions=glusterfsContributions, GLUSTERFSCOMMITS=GLUSTERFSCOMMITS, openstacklanguageInfo=openstacklanguageInfo, glusterfslanguageInfo=glusterfslanguageInfo)

@app.route('/users/<username>')
def users(username=None):
	AssignedDict = dict(list(Counter(assignedTo).most_common()))
	reporterDict = dict(list(Counter(reportedBy).most_common()))
	ccListDict = dict(list(Counter()))
	a = AssignedDict[username]
	b = reporterDict[username]
	return render_template('user.djt', user=username)

@app.route('/charts')
def charts():
	AssignedDict = dict(list(Counter(assignedTo).most_common()))
	reporterDict = dict(list(Counter(reportedBy).most_common()))
	counterData = dict(list(Counter(createdTime).items()))
	statusCount = dict(list(Counter(status).items()))
	monthYearCount = dict(list(Counter(monthYear).items()))
	YearCount = dict(list(Counter(Year).items()))
	platformDict = dict(list(Counter(platforms).items()))
	classificationDict = dict(list(Counter(classification).items()))
	data = []
	# Unicode to String conversions
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
	AssignedInfo = []
	ReporterInfo = []
	for key, value in AssignedDict.iteritems():
		temp = []
		temp.append(key.encode('ascii','ignore'))
		temp.append(value)
		AssignedInfo.append(temp)
	for key, value in reporterDict.iteritems():
		temp = []
		temp.append(key.encode('ascii','ignore'))
		temp.append(value)
		ReporterInfo.append(temp)
	platformInfo = []
	for key, value in platformDict.iteritems():
		temp = []
		temp.append(key.encode('ascii','ignore'))
		temp.append(value)
		platformInfo.append(temp)
	classificationInfo = {}
	for key, value in classificationDict.iteritems():
		classificationInfo[str(key)] = value
	return render_template('chart.djt', statusData = data, timeInfo=timeInfo, monthYearInfo=monthYearInfo, YearInfo=YearInfo, AssignedInfo=AssignedInfo, ReporterInfo=ReporterInfo, platformInfo=platformInfo, classificationInfo=classificationInfo)

@app.route('/leaderboard')
def leaderboard():
	AssignedList = list(Counter(assignedTo).most_common())
	reporterList = list(Counter(reportedBy).most_common())
	noOfAssignees = len(set(AssignedList))
	noOfReporters = len(set(reporterList))
	return render_template('leaderboard.djt', AssignedList=AssignedList, noOfAssignees=noOfAssignees, reporterList=reporterList, noOfReporters=noOfReporters, no_of_bugs=no_of_bugs)

@app.route('/component')
def component():
	noOfComponents = len(list(set(components)))
	componentList = list(Counter(components).most_common())
	colors = ['aqua','green','blue','yellow','purple','orange','red']
	return render_template('components.djt', noOfComponents=noOfComponents, components=componentList, colors=colors)

@app.route('/')
def screen():
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
	return render_template('index.djt', noOfBugs=no_of_bugs, noOfPeopleAssigned=noOfPeopleAssigned, bugIds=bugTimeline, severityList=severityList, noOfQAContacts=noOfQAContacts, noOfRepos=noOfRepos, repoResult=repoResult, noOfCCParticipants=noOfCCParticipants, noOfComponents=noOfComponents, statusList=statusList)

@app.teardown_appcontext
def close_db(self):
	"""Closes the database again at the end of the request."""
	get_cursor().close()

if __name__ == '__main__':
	app.debug = True
	app.secret_key=os.urandom(24)
	# app.permanent_session_lifetime = datetime.timedelta(seconds=200)
	app.run(host='0.0.0.0', port=8080)