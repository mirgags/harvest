#!/usr/bin/env
# -*- coding: utf -*-

import os
import urllib
import urllib2
import json
import base64
import datetime
import sys
import random
import re
import requests
from requests.auth import HTTPBasicAuth

sys.path.append('~/Projects/Python')

#if __name__ == "__main__" and __package__ is None:
#    __package__ = "~/Projects/Python/slack"

from slack import slack_api
from googleBiz import googleApi

#sys.path.append('~/Projects/Python')

#from slack import slack_api

def getConfig():
    curPath = os.getcwd()
    data = []
    with open('%s/harvest/config.txt' % curPath, 'rb') as f:
        data = json.load(f)
#    print json.dumps(data)
#    for thing in data:
#        print thing + ': ' + data[thing]
    f.close()
    return data

def getUser():
    data = getConfig()
    return data['user']

def getPass():
    data = getConfig()
    return data['password']

def getString():
    data = getConfig()
    return data['strings'][random.randint(0,len(data['strings'])-1)]

def getUrl(theurl, userParam=None, data=None):
    auth = 'Basic ' + base64.urlsafe_b64encode('%s:%s' % (getUser(), getPass()))
    if not data:
        theurl += '.json'
    if userParam:
        theurl += '?of_user=' + userParam
    print theurl
    req = urllib2.Request(theurl)
    req.add_header('Content-Type', 'application/xml')
    req.add_header('Accept', 'application/xml'),
    req.add_header('User-Agent', 'PINT_api_tool')
    if data:
        data = req.add_data(data)
#        print data
    req.add_header('Authorization', auth)
    
    req.add_header('user-agent', getUser())
    #print 'METHOD: ' + req.get_method()
    #print 'HEADERS: ' + json.dumps(req.header_items())
    #print 'FULL URL: ' + req.get_full_url()
    #print 'DATA: ' + json.dumps(req.get_data())
    pagehandle = urllib2.urlopen(req)
    return pagehandle


def getProjects():
    config = getConfig()
    theBaseUrl = config['baseUrl']
    response = getUrl('https://' + theBaseUrl + '/projects')
    theList = json.loads(response.read())
#    print json.dumps(theList)
    return theList


def getUsers():
    config = getConfig()
    theBaseUrl = config['baseUrl']
    response = getUrl('https://' + theBaseUrl + '/people')
    theDict = json.loads(response.read())
    theList = []
    for user in theDict:
        #print json.dumps(user)
        theList.append(user['user'])
    return theList

def getSchedule():
    curPath = os.getcwd()
    data = []
    with open('%s/harvest/users.txt' % curPath, 'rb') as f:
        data = json.load(f)
    f.close()
    return data

def getTimeEntries(theDay, theYear, theUser):
    config = getConfig()
    theBaseUrl = config['baseUrl']
    print theBaseUrl
    response = getUrl('https://'+theBaseUrl+'/daily/' + theDay + '/'+\
    theYear, theUser)
    theList = json.loads(response.read())
    return theList

def updateTimeEntry(theID, theUser, theData):
    config = getConfig()
    theBaseUrl = config['baseUrl']
    try:
        response = getUrl('https://%s/daily/update/%s' % (theBaseUrl, theID), str(theUser), theData)
        #print 'resp code: '
        return response.read()
    except urllib2.HTTPError as e:
        return e.code

def postTimeEntry(theUser, theData):
    config = getConfig()
    theBaseUrl = config['baseUrl']
    try:
        response = getUrl('https://%s/daily/add' % theBaseUrl, None, theData)
        #print 'resp code: '
        return response.read()
    except urllib2.HTTPError as e:
        return e.code

def roundTime(harvestTimeEntry):
    item = harvestTimeEntry
    timeString = str(item['hours'])
    hours = int(timeString.split('.')[0])
    #print 'hours: ' + str(hours)
    integer = int(timeString.split('.')[1])
    #print 'minutes: ' + str(integer)
    if integer > 0 and integer <= 25:
        minutes = 25
    if integer > 25 and integer <= 50:
        minutes = 50
    if integer > 50 and integer <= 75:
        minutes = 75
    if integer > 75:
        minutes = 0
        hours = hours + 1              
    #print 'rounded time: ' + str(hours) + '.' + str(minutes)

    return float(str(hours) + '.' + str(minutes))

# Parameters should all be strings
def roundUserTime(day, year, userID):
    theJson = getTimeEntries(day,year,userID)
    for item in theJson['day_entries']:
        print json.dumps(item)
        if item['hours'] % 0.25 != 0:
            roundedTime = roundTimeEntry(item)
            #payload = '{request:{notes:%s,hours:%s,spent_at:%s,project_id:%s,task_id:%s}}' % \
            #    (item['notes'],roundedTime,item['spent_at'],item['project_id'],item['task_id'])
            payload = '<request><notes>%s</notes><hours>%s</hours><spent_at>%s</spent_at><project_id>%s</project_id><task_id>%s</task_id></request>' % (item['notes'],str(roundedTime),item['spent_at'],item['project_id'],item['task_id'])
            print json.dumps(payload)
            resp = postTimeEntries(item['id'],payload)

def getDay():
    today = datetime.date.today()
    yearStart = datetime.date(today.year,1,1)
    days = today - yearStart
    days = days.days
    days = datetime.datetime.now().timetuple().tm_yday
    print days
    return days

def editTimeEntry(item):
    roundedTime = roundTime(item)
    #print 'Date From Harvest: ' + item['spent_at']
    dateList = item['spent_at'].split('-')
    dateObject = datetime.date(int(dateList[0]),int(dateList[1]),int(dateList[2]))
    dateStr = dateObject.strftime('%a, %d %b %Y')
    #print 'Date String: ' + dateStr
    payload = '<request><notes>%s</notes><hours>%s</hours><spent_at type="date">%s</spent_at><project_id>%s</project_id><task_id>%s</task_id></request>' % (item['notes'],str(roundedTime),dateStr,item['project_id'],item['task_id'])
    #print 'payload: ' + json.dumps(payload)
    resp = updateTimeEntry(item['id'], item['user_id'], payload)

def checkUserTimeToday(singleUser=None):
    day = datetime.date.today().strftime('%d')
    year = datetime.date.today().strftime('%Y')
    #print 'day: ' + day + '\nyear: ' + year
    if singleUser:
        singleUserID = int(getUserID(singleUser))
        #print singleUserID
        userList = [ {'id': singleUserID } ]
    else:
        userList = getUsers()
    #print json.dumps(userList)
    for user in userList:
        theJson = getTimeEntries(day, year, str(user['id']))
        for item in theJson['day_entries']:
            if item['hours'] % 0.25 != 0:
                #print json.dumps(item)
                editTimeEntry(item)

def getUserID(userEmail):
    userList = getUsers()
    for user in userList:
        if user['email'] == userEmail:
            return user['id']

def totalTimers(timers):
    total = 0
    for timer in timers['day_entries']:
        total += timer['hours']
        print timer['client'] + ' ' + timer['project'] + ' - ' +\
        timer['task'] + ', ' + str(timer['hours']) + ' hours'
    return total

def toSlack(email, msg):
    data = slack_api.getConfig()
    payload = {
    'token': data['key'],
    'text': msg,
    'icon_url': 'http://www.getharvest.com/assets/favicon-e22ef918d9134fa729c41dafa0916ed9.ico',
    'username': 'HarvestBot'
    }
    slack_api.sendSlackMsg(email, payload)

def changePMStatus(email):
    config = getConfig()
    print json.dumps(config)
    projects = getProjects()
    #print projects
    users = getUsers()
    print config['user'] + ' ' + config['password']
    auth = 'Basic ' + base64.urlsafe_b64encode('%s:%s' % (getUser(), getPass()))
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'PINT_api_tool',
        'Authorization': auth
    }
    
    for user in users:
        if user['email'] == email:
            data = {
                "user_assignment": {
                    "user_id": int(user['id']),
                    "deactivated": False,
                    "hourly_rate": 0.00,
                    "is_project_manager": True
                }
            }
            for project in projects:
                if project['project']['name'].find('ZingChart') == -1:
                #if project['project']['id'] == 3186242:
                #if project['project']['active'] == True:
                    data['user_assignment']['project_id'] = int(project['project']['id'])
                    #data = '<user-assignment>' +\
                    #    '<user-id type="integer">' + str(user['id']) +\
                    #    '</user-id>' +\
                    #    '<project-id type="integer">' +\
                    #    str(project['project']['id']) + '</project-id>' +\
                    #    '<deactivated type="boolean">false</deactivated>'+\
                    #    '<hourly-rate type="decimal">0.00</hourly-rate>'+\
                    #    '<is-project-manager type="boolean">true' +\
                    #    '</is-project-manager></user-assignment>'
                    print project['project']['name'] + ': ' + str(project['project']['id'])
                    theUrl = 'https://' + config['baseUrl'] + '/projects/' + str(project['project']['id']) + '/user_assignments'
                    r = requests.get(url=theUrl,headers=headers)
                    assignmentList = json.loads(r.text)
                    for assignment in assignmentList:
                        if assignment['user_assignment']['user_id'] == int(user['id']):
                            userAssignmentId = assignment['user_assignment']['id']
                    theUrl = 'https://pint.harvestapp.com/projects/' + str(project['project']['id']) + '/user_assignments/' + str(userAssignmentId)
                    #print json.dumps(data)
                    #r = putPMStatus(theUrl, data)
                    r = requests.put(url=theUrl,data=json.dumps(data),headers=headers)
                    #r = requests.get(url='https://pint.harvestapp.com/people/'+str(user['id']),auth=(str(config['user']), str(config['password'])))
                    print r.status_code
                    #print r.text
#    print theUrl
#    r = requests.get(url='https://'+config['baseUrl']+'/projects.json',auth=auth,params=data)
#    r = requests.put(url=theUrl,data=data,auth=auth)
#    print r.status_code
#    print r.text

def strTimeRegex(string):
    try:
        print string
    except:
        pass
    regex = re.compile(r"(\d+:\d+)|(\d+\SM)|(\d+\s\SM)", re.U)
    theList = regex.findall(string)
    try:
        print json.dumps(theList)
    except:
        pass
    try:
        print 'match length: ' + str(len(theList))
        returnList = []
        for i in range(len(theList)):
            print i
            theHour = int(str(theList[i][0]).split(':')[0])
            if theHour < 8 :
                theHour = theHour + 12
            returnList.append(int(theHour))
        print json.dumps(returnList)
        return returnList
    except Exception as e:
        print e
        return None

def getDateTime():
    thisDay = datetime.date.today()
    if thisDay.weekday() == 0:
        daysBack = 3
    else:
        daysBack = 1 
    dayInt = getDay() - daysBack
    theDate = datetime.date.today() - datetime.timedelta(days=daysBack)
    return [
        dayInt,
        datetime.datetime.combine(theDate, datetime.time(1,0,0))
    ]

def getPartTimeSchedule(calendarList):
    nameList = []
    for item in calendarList:
        timeList = strTimeRegex(item)
        index = str(item.split(' ')[0])
        nameList.append({index: []})
        if timeList:
            for i in timeList:
                nameList[(len(nameList) - 1)][index].append(i)
    return nameList

def functionalMess():
    #    changePMStatus('cscala@pint.com')
    print sys.path
    thisDay = datetime.date.today()
    if thisDay.weekday() == 0:
        daysBack = 3
    else:
        daysBack = 1 
    dayInt = getDay() - daysBack
    theDate = datetime.date.today() - datetime.timedelta(days=daysBack)
    theDateTime = datetime.datetime.combine(theDate, datetime.time(1,0,0))
    calendarList = googleApi.getEvents(theDateTime);
    for item in calendarList:
        print item
    usersJson = getUsers()
    usersSchedule = getSchedule()
    print usersSchedule
    curPath = os.getcwd()
#    with open('%s/harvest_report.csv' % curPath, 'ab') as f:
    with open('%s/harvest/harvest_report.csv' % curPath, 'wb') as f:
       for user in usersJson:
            print user
            if user['email'] in usersSchedule:
                print user['first_name'] + \
                ' ' + user['last_name']
                timers = getTimeEntries(str(dayInt),'2017',str(user['id']))
                total = 0
                if len(timers['day_entries']) > 0:
                    print timers['day_entries'][0]['spent_at']
                    total = totalTimers(timers)
                print 'Total Hours: ' + str(total)
                includeBool = True
                if user['first_name'] <= 'Merrily':
                    includeBool = False
                if total < usersSchedule[user['email']] and includeBool:
                    link = 'https://pint.harvestapp.com/' +\
                    'time/day/%s/%s/%s/%s' % \
                    (theDate.strftime('%Y'),theDate.strftime('%m'),\
                    theDate.strftime('%d'),str(user['id']))
                    csvLine = user['first_name'] + \
                    ' ' + user['last_name'] + ',' + str(total) + ',' +\
                    link + ',' + \
                    theDate.strftime('%m/%d/%Y') + '\n'
                    f.write(csvLine)
                    slackStr = '\n'
                    #slackStr += '*It\'s the End of the Month!!*\n'
                    #slackStr += '*We NEED your hours!!*\n'
                    #' Total Hours Recorded: '+ str(total) + '\n' + link
                    slackStr += getString()+'\n'+\
                    ' Total Hours Recorded: '+ str(total) + '\n' + link
                    toSlack(user['email'], slackStr)
                    slackStr += ' *'+user['first_name']+'*'
                    copyEmail = getUser()
                    toSlack(copyEmail, slackStr)
    f.close()

def workInProgress():
#    changePMStatus('cscala@pint.com')
    print sys.path
    dateInfo = getDateTime()
    dayInt = dateInfo[0]
    theDateTime = dateInfo[1]
    calendarList = googleApi.getEvents(theDateTime);
    print calendarList
    #partTimeList = getPartTimeSchedule(calendarList)
    #print json.dumps(partTimeList)
    usersJson = getUsers()
    usersSchedule = getSchedule()
    print usersSchedule
    curPath = os.getcwd()
#    with open('%s/harvest_report.csv' % curPath, 'ab') as f:
    with open('%s/harvest/harvest_report.csv' % curPath, 'wb') as f:
       for user in usersJson:
            print user
            if user['email'] in usersSchedule:
                print user['first_name'] + \
                ' ' + user['last_name']
                timers = getTimeEntries(str(dayInt),'2016',str(user['id']))
                total = 0
                if len(timers['day_entries']) > 0:
                    print timers['day_entries'][0]['spent_at']
                    total = totalTimers(timers)
                print 'Total Hours: ' + str(total)
                if total < usersSchedule[user['email']] and user['email'] == 'mmiraglia@pint.com':
                    if not any(user['first_name'] in s for s in nameList):
                        print 'slacking ' + user['first_name']
                        link = 'https://pint.harvestapp.com/' +\
                        'time/day/%s/%s/%s/%s' % \
                        (theDate.strftime('%Y'),theDate.strftime('%m'),\
                        theDate.strftime('%d'),str(user['id']))
                        csvLine = user['first_name'] + \
                        ' ' + user['last_name'] + ',' + str(total) + ',' +\
                        link + ',' + \
                        theDate.strftime('%m/%d/%Y') + '\n'
                        f.write(csvLine)
                        slackStr = '*It\'s getting towards End of Month*\n'+\
                        ' Total Hours Recorded: '+ str(total) + '\n' + link
                        slackStr += getString()+'\n'+\
                        ' Total Hours Recorded: '+ str(total) + '\n' + link
                        toSlack(user['email'], slackStr)
                        slackStr += ' *'+user['first_name']+'*'
                        copyEmail = getUser()
                        toSlack(copyEmail, slackStr)
                    else:
                        print 'omitting ' + user['first_name']
    f.close()
    #print '*****  START PYTHON SCRIPT *****'
#print '*****  START PYTHON SCRIPT *****'
    #checkUserTimeToday(userEmailString)
#    checkUserTimeToday()
    #print '\n*****\n'
 


if __name__ == '__main__':
    functionalMess()
#    emails = ['rob@pint.com']
#    for email in emails:
#        changePMStatus(email)

