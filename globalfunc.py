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

db = mysql.connector.connect(host=login.host,    # your host, usually localhost
                     user=login.sqluser,         # your username
                     passwd=login.sqlpasswd,  # your password
                     db=login.db)        # name of the data base
cur = db.cursor()

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
		try:
			utrsIDs = text.split("{{UTRS-unblock-user|")
			for item in utrsIDs:
				if "UTRSBot" not in item:continue
				if "closed}}" in item:continue
				utrsID = item.split("|")[0]
				print utrsID
				cur.execute("SELECT appealID,status FROM enwikipedia.appeal where appealid=%s;" %(utrsID))
				table = cur.fetchall()
				for row in table:
					if int(row[0]) != int(utrsID):
						print row[0]," - ",utrsID
						raise Exception('Failure to sync numbers')
					if row[1] == "CLOSED":
						templateString = text.split("{{UTRS-unblock-user|"+str(utrsID))[1].split("}}")[0]
						print "templateString: ", templateString
						newstring = templateString +"|closed"
						newstring = "{{UTRS-unblock-user|"+str(utrsID)+newstring+"}}"
						text = text.replace("{{UTRS-unblock-user|"+str(utrsID)+templateString+"}}",newstring,1)
						print "Old: ","{{UTRS-unblock-user|"+str(utrsID)+templateString+"}}"
						print "New: ",newstring
						page.save(text,"Syncing closed UTRS appeal status manually")
						time.sleep(5)
					elif row[1] =="INVALID":
						templateString = text.split("{{UTRS-unblock-user|"+str(utrsID))[1].split("}}")[0]
						print "templateString: ", templateString
						text = text.replace("{{UTRS-unblock-user|"+str(utrsID)+templateString+"}}","",1)
						page.save(text,"Removing invalid appeal - please ignore this appeal")
					else:
						print "Appeal #",utrsID," is not closed. SKIPPING"
		except:
			print "Failed to get page for: ",user
			continue
processMembers()