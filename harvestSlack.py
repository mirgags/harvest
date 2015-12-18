import os
import urllib
import urllib2
import httplib
import json
import base64
import datetime
import sys
import random
import re
import requests
from requests.auth import HTTPBasicAuth

from slack import slack_api
from harvest import harvest_api

if __name__ == "__main__":
    theUsers = harvest_api.getUsers()
    slackStr = 'Ok. Last reminder _today_. If you need to review the new health plans with family *do it tonight*. Applications *must* be in to Mark first thing tomorrow.'
    partTimeList = [
        'nardecky@pint.com',
        'dbekkerman@pint.com',
        'jbogart@pint.com',
        'mchopp@pint.com',
        'cboylan@pint.com',
        'rchang@pint.com',
        'echoi@pint.com',
        'ccoley@pint.com',
        'pdilione@pint.com',
        'jforest@pint.com',
        'jfrederich@pint.com',
        'agian@pint.com',
        'akandukuri@pint.com',
        'jlima@pint.com',
        'jlopez@pint.com',
        'rob@pint.com',
        'aneely@pint.com',
        'anguyen@pint.com',
        'knguyen@pint.com',
        'cnusbaum@pint.com',
        'tpowell@pint.com',
        'presenbeck@pint.com',
        'prodee@pint.com',
        'dsaisho@pint.com',
        'esamuelson@pint.com',
        'cscala@pint.com',
        'mschultz@pint.com',
        'nsletteland@pint.com',
        'jtam@pint.com',
        'htavakoli@pint.com',
        'mwang@pint.com',
        'iyates@pint.com'
    ]
    for user in theUsers:
        if user['is_active'] and not user['is_contractor'] and not user['email'] in partTimeList:
            print 'slacking ' + user['first_name'] + ' ' + user['last_name']
            #harvest_api.toSlack(user['email'], slackStr)
            #slackStr += ' *'+user['first_name']+'*'
            #toSlack(copyEmail, slackStr)

