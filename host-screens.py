#!/usr/bin/env python

from re import match
from pyzabbix import ZabbixAPI

def initZabbix():
    global zapi
    zapi = ZabbixAPI("http://zabbix-admin-hk.prod.spotoption.com/zabbix/")
    zapi.login("admin", "zabbix") 

def createScreen(name, hostid, graphids):
    print graphids
    screenitems = []
    for index, graphid in enumerate(graphids):
       screenitems.append({
           "resourcetype":"0",
           "resourceid":str(graphid),
           "width":"500",
           "height":"100",
           "x": 0,
           "y": index,
           "dynamic": True
       })
    print screenitems

    response = zapi.screen.create(name=name, hsize=1, vsize=len(graphids),screenitems=screenitems)
    screenid = response['screenids']
   

def parseHost(name, id):
    if(not match('.*-hk$',name)):
        return
    print name

    graphids = []
    for graph in zapi.graph.get(output=['graphid','name'], hostids=id):
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
    
