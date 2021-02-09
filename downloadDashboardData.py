#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 12:41:03 2021

@author: dclabby
"""


import datetime
import time
import requests

startTime = datetime.date(2014, 1, 1)
endTime = datetime.date(2014, 10, 28)#datetime.date.today()#datetime.date(2021, 2, 2)
blockSize = 30
tableName = "SystemGeneration"#"SystemDemand"#"WindGeneration"
linkStr = "http://smartgriddashboard.eirgrid.com/DashboardService.svc/csv?area=<tableID>&region=ALL&datefrom=<blockStart>%2000:00&dateto=<blockEnd>%2023:59"
savePath = "/home/dclabby/Documents/DataScience/Data Sets/EirgridDashboardAnalysis/" + tableName + "/"
maxLoops = 100

blockStart = startTime
blockEnd = blockStart + datetime.timedelta(blockSize-1)
loopCounter = 0

if tableName == "WindGeneration":
    tableID = "windActual"
elif tableName == "SystemDemand":
    tableID = "demandActual"
elif tableName == "SystemGeneration":
    tableID = "generationActual"


while (blockEnd.toordinal() < endTime.toordinal() + blockSize) and (loopCounter < maxLoops): 
    if blockEnd.toordinal() > endTime.toordinal():
        url = linkStr.replace("<blockStart>", blockStart.strftime("%d-%b-%Y")).replace("<blockEnd>", endTime.strftime("%d-%b-%Y")).replace("<tableID>", tableID)
        filename = tableName + "_" + blockStart.strftime("%Y-%m-%d") + "_" + endTime.strftime("%Y-%m-%d") + ".csv"
    else:
        url = linkStr.replace("<blockStart>", blockStart.strftime("%d-%b-%Y")).replace("<blockEnd>", blockEnd.strftime("%d-%b-%Y")).replace("<tableID>", tableID)
        filename = tableName + "_" + blockStart.strftime("%Y-%m-%d") + "_" + blockEnd.strftime("%Y-%m-%d") + ".csv"
    print("...")
    print("Downloading " + filename)
    t1 = time.time()   
    r = requests.get(url, allow_redirects=True)    
    open(savePath + filename, "wb").write(r.content)
    print("Download completed & file written in " + "{:.2f}".format(time.time() - t1) + "s")
    
    blockStart = blockEnd + datetime.timedelta(1)
    blockEnd = blockStart + datetime.timedelta(blockSize-1)
    loopCounter += 1
    