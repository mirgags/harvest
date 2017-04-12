import json
import csv

fPath = './harvestRpt.csv'

class harvestReport:
    def __init__(self):
        self.timeEntries = []
        with open(fPath, 'rb') as csvfile:
            theReader = csv.DictReader(csvfile)
            taskDict = {}
            for row in theReader:
                dept = row['Task'].split(' - ')[0].strip()
                task = row['Task']
                self.timeEntries.append(row)
                if not dept in taskDict:
                    taskDict[dept] = {'deptTotal':0}
                    #taskDict[dept]['deptTotal'] = 0
                if not task in taskDict[dept]:
                    taskDict[dept][task] = 0
                taskDict[dept][task] += float(row['Hours Rounded'])
        for key in taskDict:
            for subKey in taskDict[key]:
                if key != 'deptTotal':
                    taskDict[key]['deptTotal'] += float(taskDict[key][subKey])
        self.timeTotals = taskDict

if __name__ == '__main__':
    colorList = [
        "#559cbe",
        "#8aab57",
        "#4885a2",
        "#595959"
    ]

    f = open('harvestChart.js', 'wb')
    r = harvestReport()
    taskList = []
    taskString = ''
    for key in r.timeTotals:
        for subkey in r.timeTotals[key]:
            if subkey != 'deptTotal' and subkey != "'---select a task---":
                taskList.append(subkey + ': ' + str(r.timeTotals[key][subkey]) + '\\n')
    taskList.sort()
    for i in taskList:
        taskString += i

    chartObj = {
      "type": "pie",
      "title": {
        "text": "PINT Harvest Task Hours 1Q2013 - 2Q2017"
      },
      "plot": {
        "borderColor": "#2B313B",
        "borderWidth": "1px",
        "value-box": {
          "placement": "out",
          "text": "%t - %v Hours"
        },
        "animation": {
          "effect": 2,
          "method": 5,
          "speed": 2000,
          "sequence": 1,
          "delay": 3000
        }
      },
      "labels": [{
              "x": "10px",
              "text-align": "left",
              "text": taskString
            }],
      "series": []
    }
    counter = 0
    colorMod = len(colorList)
    threshold = 1000
    for key in r.timeTotals:
        if r.timeTotals[key]['deptTotal'] > threshold:
            inputSeries = {
              "text": key,
              "values": [r.timeTotals[key]['deptTotal']],
              "backgroundColor": colorList[counter % colorMod]
            }
            chartObj['series'].append(inputSeries)
            counter += 1
    print json.dumps(chartObj, indent=2, sort_keys=True)
    #jsString = '''
    #  var myConfig = {
    #    type: "pie",
    #    title: {
    #      text: "PINT Harvest Task Hours 1Q2013 - 2Q2017",
    #    },
    #    plot: {
    #      borderColor: "#2B313B",
    #      borderWidth: "1px",
    #      "value-box": {
    #        placement: "out",
    #        text: "%t - %v Hours"
    #      },
    #      animation: {
    #        effect: 2,
    #        method: 5,
    #        speed: 2000,
    #        sequence: 1,
    #        delay: 3000
    #      }
    #    },
    #    labels: [{
    #      x: "10px",
    #      "text-align": "left",
    #      text: "'''
    #jsString += taskString
    #jsString += '"}],series: ['

    #counter = 0
    #colorMod = len(colorList)
    #threshold = 1000
    #for key in r.timeTotals:
    #    if r.timeTotals[key]['deptTotal'] > threshold:
    #        if not counter == 0:
    #          jsString += ',\n'
    #        jsString += '{values:\n[' + str(r.timeTotals[key]['deptTotal']) + '],\ntext:"' + key
    #        jsString += '",\nbackgroundColor:"' 
    #        jsString += colorList[counter % colorMod]
    #        jsString += '"}'
    #        counter += 1
    #jsString += ']};'
    #jsString += '''
    renderObj = {
        "id": "myChart",
        "data": chartObj,
        "height": "100%",
        "width": "100%"
    };
    f.write('var myConfig = ' + json.dumps(chartObj) + ';' + 'zingchart.render(' + json.dumps(renderObj) + ');')
    #f.write(jsString)
    f.close()


