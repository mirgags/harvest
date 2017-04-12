#!/usr/bin/env
# -*- coding: utf-8 -*-

import harvest_api
import json
import base64

def getActiveUsers():
    activeUsers = []
    # Get all Harvest Users
    usersJson = harvest_api.getUsers()
    for user in usersJson:
        if user['is_active']:
            activeUsers.append(user)
    
    return activeUsers

class Project:
    def __init__(self, projectID):
        self.projectID = projectID
        projUrl = 'https://pint.harvestapp.com/projects/' + str(projectID)
        resp = harvest_api.getUrl(projUrl)
        respJson = json.loads(resp.read())
        self.data = respJson['project']

def putUrl(url, data):
    auth = 'Basic ' + base64.urlsafe_b64encode('%s:%s' % (harvest_api.getUser(), harvest_api.getPass()))
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'PINT_api_tool',
        'Authorization': auth
    }
    print url
    print data
    resp = harvest_api.requests.put(url=url,data=json.dumps(data),headers=headers)   
    print resp.text

def getPtoData(userEmail):
    activeUsers = getActiveUsers()
    f = open('harvest/ptoEligibility.json', 'rb')
    ptoJson = json.loads(f.read())
    f.close()
    for user in activeUsers:
        if user['email'] == userEmail:
            return ptoJson[user['first_name'] + ' ' + user['last_name']]


if __name__ == '__main__':
    activeUsers = getActiveUsers()
    marksProject = Project(11500315)
    print 'budget:' + str(marksProject.data['budget'])
    newBudget = float(marksProject.data['budget']) + 10
    marksProject.data['budget'] = newBudget
    marksProject.data['estimate'] = newBudget
    marksProject.data['name'] = 'Vacation - Mark Miraglia Test'
    print 'budget:' + str(marksProject.data['budget'])
    url = 'https://pint.harvestapp.com/projects/'+ str(marksProject.data['id'])
    reqJson = {"project": marksProject.data}
    putUrl(url, reqJson)
    mark = getPtoData('mmiraglia@pint.com')
    print json.dumps(mark)

