from harvest.harvest_api import *
import csv

zingProjectList = []
rowDict = {}

curPath = os.getcwd()
with open('%s/harvest/import.csv' % curPath, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        zingProjectList.append(row)
csvfile.close

harvestProjects = getProjects()
for thing in harvestProjects:
    print thing

#for thing in zingProjectList:
#    print thing
