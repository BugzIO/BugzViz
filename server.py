# all the imports
import os,binascii
from flask import Flask, request, session, g, redirect, url_for, abort, \
		render_template, flash
from flaskext.mysql import MySQL
from flask_mail import Mail,Message
from config import config, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
from werkzeug.utils import secure_filename
from flask import send_from_directory
import datetime, json
from pprint import pprint
from collections import Counter
import re, datetime
 
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

def tup2float(tup):
	return float('.'.join(str(x) for x in tup))

def get_cursor():
	return mysql.connect().cursor()

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.route('/')
def screen():
	with open('sample.json') as data_file:
		data = json.load(data_file)
	result = data["result"]["bugs"]
	no_of_bugs = len(result)
	assignedTo = []
	severity = []
	qaContacts = []
	bugTimeline = []
	for objects in result:
		assignedTo.append(objects["assigned_to"])
		qaContacts.append(objects["qa_contact"])
		severity.append(objects["severity"])
		temp = []
		temp.append(objects["id"])
		temp.append(datetime.datetime(*map(int, re.split('[^\d]', objects["creation_time"])[:-1])))
		bugTimeline.append(temp)
	noOfPeopleAssigned = len(list(set(assignedTo)))
	noOfQAContacts = len(list(set(qaContacts)))
	severityList = list(Counter(severity).items())
	with open('redhatRepos.json') as data:
		repoData = json.load(data)
	repoResult = repoData.keys()
	repoResult.sort()
	noOfRepos = len(repoResult)
	return render_template('index.html', noOfBugs=no_of_bugs, noOfPeopleAssigned=noOfPeopleAssigned, bugIds=bugTimeline, severityList=severityList, noOfQAContacts=noOfQAContacts, noOfRepos=noOfRepos, repoResult=repoResult)

@app.teardown_appcontext
def close_db():
	"""Closes the database again at the end of the request."""
	get_cursor().close()

if __name__ == '__main__':
	app.debug = True
	app.secret_key=os.urandom(24)
	# app.permanent_session_lifetime = datetime.timedelta(seconds=200)
	app.run()