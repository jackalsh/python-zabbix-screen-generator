#!/usr/bin/env python

from re import match
from pyzabbix import ZabbixAPI

def initZabbix():
    global zapi
    zapi = ZabbixAPI("http://zabbix-admin-hk.prod.spotoption.com/zabbix/")
    zapi.login("admin", "zabbix") 

def jsonScreenItems(graphids):
    screenitems = []
    for index, graphid in enumerate(graphids):
       screenitems.append({
           "resourcetype":"0",
           "resourceid":str(graphid),
           "width":"500",
           "height":"100",
           "x": 0,
           "y": index
       })
    return screenitems

def createScreen(name, hostid, graphids):
    if(zapi.screen.exists(name = name)):
        screenid = zapi.screen.get(output=['name','screenid'], filter={"name":name})[0]['screenid']
        zapi.screen.update(screenid = screenid, size=1, vsize=len(graphids), screenitems=jsonScreenItems(graphids))
        print "Screen updated"
    else:
       response = zapi.screen.create(name=name, hsize=1, vsize=len(graphids),screenitems=jsonScreenItems(graphids))
       screenid = response['screenids']
       print "Screen created"

def calcRank(graph):
    graph['rank'] = 0
    if(graph['name'] == "CPU load"):
        graph['rank'] = 100
    elif(match("^Network traffic.*", graph['name'])):
        graph['rank'] = 90
    elif(graph['name'] == "Memory usage"):
        graph['rank'] = 100
    elif(match("^Disk usage.*", graph['name'])):
        graph['rank'] = 90
    return graph


def compareGraph(graph1, graph2):
    if (calcRank(graph1)['rank'] < calcRank(graph2)['rank']):
        return 1
    elif(calcRank(graph1)['rank'] > calcRank(graph2)['rank']):
        return -1
    else:
        return 0

def parseHost(name, id):
    if(not match('.*-hk$',name)):
        return
    print name

    graphids = []
    graphs = sorted(zapi.graph.get(output=['graphid','name'], hostids = id), cmp = compareGraph)
    for graph in graphs:
        print "  * %s" % (graph['name'])
        graphids.append(graph['graphid'])
    createScreen(name, id, graphids)    


def parseHosts():
    for host in zapi.host.get(output=["host","hostid"]):
        parseHost(host['host'],host['hostid'])

def main():
    initZabbix()
    print "Connected to Zabbix API Version %s" % zapi.api_version()

    parseHosts()

if __name__ == "__main__":
    main()
    
