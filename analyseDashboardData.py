#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 16:11:18 2021

@author: dclabby
"""
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
from os import walk

def importData(dataName):
    pathName = "/home/dclabby/Documents/DataScience/Data Sets/EirgridDashboardAnalysis/" + dataName + "/"
    if dataName == "WindGeneration":
        iData = 2
    else:
        iData = 1
    
    _, _, fileNames = next(walk(pathName))
    dfList = []
    for iFile in fileNames:
        if iFile[-4:] == ".csv":
            dfTmp = pd.read_csv(pathName + iFile, delimiter=',')
            dfTmp[dfTmp.columns[0]] = pd.to_datetime(dfTmp[dfTmp.columns[0]], format="%d %B %Y %H:%M") 
            dfTmp[dfTmp.columns[iData]] = pd.to_numeric(dfTmp[dfTmp.columns[iData]], errors="coerce") 
            dfTmp = dfTmp.dropna(subset=[dfTmp.columns[iData]])
            dfList.append(dfTmp)
    
    df = pd.concat(dfList)
    df = df.drop_duplicates()
    df = df.dropna(subset=[df.columns[iData]])
    df = df.sort_values(by=df.columns[0]) 
    
    return df

def calcStats(timeSeries, dataSeries):
    avgAnnual = []
    avgMonthly = []
    for iYear in range(pd.DatetimeIndex(timeSeries).year.min(), pd.DatetimeIndex(timeSeries).year.max()):
        dfTmp = pd.DataFrame({
            "timeSeries": timeSeries[pd.DatetimeIndex(timeSeries).year == iYear],
            "dataSeries": dataSeries[pd.DatetimeIndex(timeSeries).year == iYear]
            })
        
        avgAnnual.append(dfTmp["dataSeries"].mean())
        for iMonth in range(1,13):
            avgMonthly.append(dfTmp["dataSeries"][pd.DatetimeIndex(dfTmp["timeSeries"]).month == iMonth].mean())
    
    return avgAnnual, avgMonthly

def movAvg(dataSeries, N):
    movAvg = np.convolve(dataSeries, np.ones(N)/N, mode='same')#, mode='valid')
    movAvg[:int(N/2)] = float("NaN")
    movAvg[-int(N/2):] = float("NaN")
    return movAvg

windTmp = importData("WindGeneration")
sysTmp = importData("SystemGeneration")

dfTmp = sysTmp.merge(windTmp, how="inner", on="DATE & TIME") # inner join ensures that no Nans introduced
dfMerged = pd.DataFrame({
    "dateTime": dfTmp["DATE & TIME"], 
    "wind": dfTmp['  ACTUAL WIND(MW)'],
    "sys": dfTmp[' ACTUAL GENERATION(MW)'],
    "windPerSys": 100*dfTmp['  ACTUAL WIND(MW)']/dfTmp[' ACTUAL GENERATION(MW)']
    })

avgAnnualWind, avgMonthlyWind = calcStats(dfMerged["dateTime"], dfMerged["wind"])
avgAnnualSys, avgMonthlySys = calcStats(dfMerged["dateTime"], dfMerged["sys"])

# Average wind power per generated system power:
annualWindPerSys, monthlyWindPerSys = calcStats(dfMerged["dateTime"], dfMerged["windPerSys"])

# Average wind energy per generated system energy:
monthlyEnergy = [100*i/j for i, j in zip(avgMonthlyWind, avgMonthlySys)] # equivalent to sum(avgMonthlyWind*dt)/sum(avgMonthlySys*dt) since (1/N) terms in means cancel
annualEnergy = [100*i/j for i, j in zip(avgAnnualWind, avgAnnualSys)] # equivalent to sum(avgAnnualWind*dt)/sum(avgAnnualSys*dt) since (1/N) terms in means cancel

N = 4*24*30*3
movAvgWind = movAvg(dfMerged["wind"], N)
movAvgSys = movAvg(dfMerged["sys"], N)
movAvgWindPerSys = movAvg(dfMerged["windPerSys"], N)

plt.close('all')

yearVector = [datetime.date(iYear, 6, 15) for iYear in range(2014, 2021)]
monthVector = [datetime.date(iYear, iMonth, 15) for iYear in range(2014, 2021) for iMonth in range(1,13)]

plt.figure(1)
plt.subplot(1, 3, 1)
plt.plot(dfMerged["dateTime"], dfMerged["sys"], '-b', 
         dfMerged["dateTime"], movAvgSys, '-c',
         yearVector, avgAnnualSys, 'or', 
         monthVector, avgMonthlySys, '.k')
plt.title("SystemGeneration")

plt.subplot(1, 3, 2)
plt.plot(dfMerged["dateTime"], dfMerged["wind"], '-b', 
         dfMerged["dateTime"], movAvgWind, '-c',
         yearVector, avgAnnualWind, 'or', 
         monthVector, avgMonthlyWind, '.k')
plt.title("WindGeneration")

plt.subplot(1, 3, 3)
plt.plot(dfMerged["dateTime"], dfMerged["windPerSys"], '-b', 
         dfMerged["dateTime"], movAvgWindPerSys, '-c',
         yearVector, annualWindPerSys, 'or', 
         monthVector, monthlyWindPerSys, '.k')
plt.title("Wind Generation as a percentage of System Generation")


monthVecRadial = [(m/12)*2*np.pi for m in range(0,13)]
n = len(yearVector)
color = plt.cm.winter(np.linspace(0,1,n))# color = plt.cm.cool(np.linspace(0,1,n))# color = plt.cm.summer(np.linspace(1,0,n))# color = plt.cm.ocean(np.linspace(0.5,0,n))#

plt.figure(2)
for i,c in zip(range(n),color):
    plt.bar([y.year for y in yearVector][i], annualWindPerSys[i], color=c)
plt.title("Average Generated Wind Power \n as a percentage of total Generated Power")
plt.ylim((0, 40))

plt.figure(3)
for i,c in zip(range(n),color):
    plt.bar([y.year for y in yearVector][i], annualEnergy[i], color=c)
plt.title("Annual average Generated Wind Energy \n as a percentage of total Generated Energy")
plt.ylim((0, 40))

plt.figure(4)
for i,c in zip(range(n),color):
    if i == n-1:
        plt.polar(monthVecRadial[:-1], monthlyWindPerSys[i*12:(i+1)*12], c=c)
    else:
        plt.polar(monthVecRadial, monthlyWindPerSys[i*12:(i+1)*12 + 1], c=c)
lines, labels = plt.thetagrids( range(0,360,30), ('Jan', 'Feb', 'Mar','Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec') )
plt.legend([y.year for y in yearVector], loc='upper left', bbox_to_anchor=(1.05, 1))
plt.title("Monthly average Wind Generation \n as a percentage of total System Generation")

dayNum = np.array([datetime.date(d.year, d.month, d.day).toordinal() - datetime.date(d.year, 1, 1).toordinal() for d in dfMerged["dateTime"]])
plt.figure(5)
for iYear, c in zip(range(2014, 2021),color):
    b = [d.year==iYear for d in dfMerged["dateTime"]]
    plt.polar((dayNum[b]/365)*np.pi*2, movAvgWindPerSys[b], c=c)

lines, labels = plt.thetagrids( range(0,360,30), ('Jan', 'Feb', 'Mar','Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec') )
plt.legend([y.year for y in yearVector], loc='upper left', bbox_to_anchor=(1.05, 1))
plt.title("Wind Generation as a percentage of total System Generation\n(3 Month Moving Average)")
