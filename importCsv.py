from harvest.harvest_api import *
import csv

zingProjectList = []
putData = {'project': {}}
harvestProjects = getProjects()
config = getConfig()
auth = 'Basic ' + base64.urlsafe_b64encode('%s:%s' % (getUser(), getPass()))
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'PINT_api_tool',
    'Authorization': auth
}

curPath = os.getcwd()
with open('%s/harvest/import.csv' % curPath, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        for thing in harvestProjects:
            zingProjectList.append(row)
            if thing['project']['name'] == row[1]:
                #if thing['project']['name'] == 'ZingChart - Adicio, Inc - Support':
                print thing['project']['name']
                theUrl = 'https://' + config['baseUrl'] + '/projects/' + str(thing['project']['id'])
                putData['project'] = {
                    'name': thing['project']['name'],
                    'active': True,
                    'bill-by': None,
                    'client_id': thing['project']['client_id'],
                    'budget_by': 'project',
                    'budget': None,
                    'billable': False,
                    'hourly_rate': None,
                    'notify_when_over_budget': True
                }
                if row[6] == '':
                    putData['project']['budget'] = 0.0
                else:
                    putData['project']['budget'] = float(row[6])
                r = requests.put(url=theUrl,json=putData,headers=headers)
                print r.status_code
                print r.text
csvfile.close


#for thing in zingProjectList:
#    print thing
