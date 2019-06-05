from datetime import datetime
import sys
import platform
import time
import json
import re
import mysql.connector

#import localconfig
import mwclient
import login

masterwiki =  mwclient.Site('en.wikipedia.org')
masterwiki.login(login.username,login.password)

#db = mysql.connector.connect(host=accountinfo.host,    # your host, usually localhost
#                     user=accountinfo.user,         # your username
#                     passwd=accountinfo.passwd,  # your password
#                     db=accountinfo.db)        # name of the data base
#cur = db.cursor()

def callAPI(params):
    return masterwiki.api(**params)

def getCurrentMembers(category):
    category = "Category:" + category
    params = {'action': 'query',
        	'list': 'categorymembers',
        	'cmtitle': category,
                'cmnamespace':'3',
                'cmlimit':'500',
                'format':'json',
                'rawcontinue':'1'
                }
    raw = callAPI(params)
    reg = raw["query"]["categorymembers"]
    reg = formatArray(reg)
    return reg

def formatArray(database):
    items = []
    for entry in database:
        items = items + [entry["title"]]
    return items

def processMembers():
	memberlist = getCurrentMembers("Requests for unblock on UTRS")
	for user in memberlist:
		page = masterwiki.pages[user]
		text = page.text()
		print text.split("{{UTRS-unblock-user|")[1].split("|")[0]
		try:
			one=1
		except:
			print "Failed to get page for: ",user
			continue
	
processMembers()