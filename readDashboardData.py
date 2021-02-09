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

def calcStats(df, iData=1):
    avgAnnual = []
    avgMonthly = []
    yearVector = []
    monthVector = []
    for iYear in range(pd.DatetimeIndex(df[df.columns[0]]).year.min(), pd.DatetimeIndex(df[df.columns[0]]).year.max()):
        yearVector.append(datetime.date(iYear, 6, 15))
        dfTmp = df[pd.DatetimeIndex(df[df.columns[0]]).year == iYear]
        
        avgAnnual.append(dfTmp[dfTmp.columns[iData]].mean())
        for iMonth in range(1,13):
            monthVector.append(datetime.date(iYear, iMonth, 15))            
            avgMonthly.append(dfTmp[dfTmp.columns[iData]][pd.DatetimeIndex(dfTmp[dfTmp.columns[0]]).month == iMonth].mean())
    
    N = 4*24*30*3
    movAvg = np.convolve(df[df.columns[iData]], np.ones(N)/N, mode='same')#, mode='valid')
    return avgAnnual, avgMonthly, yearVector, monthVector, movAvg


sysGen = importData("SystemGeneration")
windGen = importData("WindGeneration")

dfTmp = sysGen.merge(windGen, how="inner", on="DATE & TIME") # inner join ensures that no Nans introduced
windPerSys = pd.DataFrame({"DATE & TIME": dfTmp["DATE & TIME"], "Wind per Sys": 100*dfTmp['  ACTUAL WIND(MW)']/dfTmp[' ACTUAL GENERATION(MW)']})

avgAnnualWind, avgMonthlyWind, _, _, movAvgWind = calcStats(windGen, 2)
avgAnnualSys, avgMonthlySys, _, _, movAvgSys = calcStats(sysGen, 1)
annualWindPerSys, monthlyWindPerSys, yearVector, monthVector, movAvgWindPerSys = calcStats(windPerSys, 1)


plt.close('all')

plt.figure(1)
plt.subplot(1, 3, 1)
plt.plot(sysGen[sysGen.columns[0]], sysGen[sysGen.columns[1]], '-b', 
         sysGen[sysGen.columns[0]], movAvgSys, '-c',
         yearVector, avgAnnualSys, 'or', 
         monthVector, avgMonthlySys, '.k')
plt.title("SystemGeneration")

plt.subplot(1, 3, 2)
plt.plot(windGen[windGen.columns[0]], windGen[windGen.columns[2]], '-b', 
         windGen[windGen.columns[0]], movAvgWind, '-c',
         yearVector, avgAnnualWind, 'or', 
         monthVector, avgMonthlyWind, '.k')
plt.title("WindGeneration")

plt.subplot(1, 3, 3)
plt.plot(windPerSys['DATE & TIME'], windPerSys["Wind per Sys"], '-b', 
         windPerSys[windPerSys.columns[0]], movAvgWindPerSys, '-c',
         yearVector, annualWindPerSys, 'or', 
         monthVector, monthlyWindPerSys, '.k')
plt.title("Wind Generation as a percentage of System Generation")



monthVecRadial = [(m/12)*2*np.pi for m in range(0,13)]
n = len(yearVector)
# color = plt.cm.cool(np.linspace(0,1,n))
# color = plt.cm.summer(np.linspace(1,0,n))
# color = plt.cm.ocean(np.linspace(0.5,0,n))
color = plt.cm.winter(np.linspace(0,1,n))

plt.figure(2)
for i,c in zip(range(n),color):
    if i == n-1:
        plt.polar(monthVecRadial[:-1], monthlyWindPerSys[i*12:(i+1)*12], c=c)
    else:
        plt.polar(monthVecRadial, monthlyWindPerSys[i*12:(i+1)*12 + 1], c=c)
lines, labels = plt.thetagrids( range(0,360,30), ('Jan', 'Feb', 'Mar','Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec') )
plt.legend([y.year for y in yearVector], loc='center left', bbox_to_anchor=(1.2, 0.5))
plt.title("Monthly average Wind Generation \n as a percentage of total System Generation")

plt.figure(3)
for i,c in zip(range(n),color):
    plt.bar([y.year for y in yearVector][i], annualWindPerSys[i], color=c)
plt.title("Annual average Wind Generation \n as a percentage of total System Generation")

N = 4*24*30*3
dayNum = np.array([datetime.date(d.year, d.month, d.day).toordinal() - datetime.date(d.year, 1, 1).toordinal() for d in windPerSys["DATE & TIME"]])
plt.figure(4)
for iYear, c in zip(range(2014, 2021),color):
    b = [d.year==iYear for d in windPerSys["DATE & TIME"]]
    if iYear == 2014:
        plt.polar((dayNum[b][N:]/365)*np.pi*2, movAvgWindPerSys[b][N:], c=c)
    elif iYear == 2020:
        plt.polar((dayNum[b][:-N]/365)*np.pi*2, movAvgWindPerSys[b][:-N], c=c)
    else:
        plt.polar((dayNum[b]/365)*np.pi*2, movAvgWindPerSys[b], c=c)

lines, labels = plt.thetagrids( range(0,360,30), ('Jan', 'Feb', 'Mar','Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec') )
plt.legend([y.year for y in yearVector], loc='center left', bbox_to_anchor=(1.2, 0.5))
plt.title("Wind Generation as a percentage of total System Generation\n(3 Month Moving Average)")



#moving average using convolution:
#np.convolve(x, np.ones(N)/N, mode='valid')


# avgAnnualWind = []
# avgAnnualSys = []
# avgMonthlyWind = []
# avgMonthlySys = []
# yearVector = []
# monthVector = []
# for iYear in range(pd.DatetimeIndex(windGen[windGen.columns[0]]).year.min(), pd.DatetimeIndex(windGen[windGen.columns[0]]).year.max()):
#     yearVector.append(datetime.date(iYear, 6, 15))
#     windTmp = windGen[pd.DatetimeIndex(windGen[windGen.columns[0]]).year == iYear]
#     sysTmp = sysGen[pd.DatetimeIndex(sysGen[sysGen.columns[0]]).year == iYear]
    
#     avgAnnualWind.append(windTmp[windTmp.columns[2]].mean())
#     avgAnnualSys.append(sysTmp[sysTmp.columns[1]].mean())
#     # avgAnnualWind.append(windGen[windGen.columns[2]][pd.DatetimeIndex(windGen[windGen.columns[0]]).year == iYear].mean())
#     # avgAnnualSys.append(sysGen[sysGen.columns[1]][pd.DatetimeIndex(sysGen[sysGen.columns[0]]).year == iYear].mean())
#     for iMonth in range(1,13):
#         monthVector.append(datetime.date(iYear, iMonth, 15))
        
#         avgMonthlyWind.append(windTmp[windTmp.columns[2]][pd.DatetimeIndex(windTmp[windTmp.columns[0]]).month == iMonth].mean())
#         avgMonthlySys.append(sysTmp[sysTmp.columns[1]][pd.DatetimeIndex(sysTmp[sysTmp.columns[0]]).month == iMonth].mean())
        
#         # avgMonthlyWind.append(windGen[windGen.columns[2]][pd.DatetimeIndex(windGen[windGen.columns[0]]).month == iMonth].mean())
#         # avgMonthlySys.append(sysGen[sysGen.columns[1]][pd.DatetimeIndex(sysGen[sysGen.columns[0]]).month == iMonth].mean())


# monthlyWindPerSys = [100*(i / j) for i, j in zip(avgMonthlyWind, avgMonthlySys)]
# annualWindPerSys = [100*(i / j) for i, j in zip(avgAnnualWind, avgAnnualSys)]

# plt.figure(3)
# # plt.polar([(m.month/12)*2*np.pi for m in monthVector], monthlyWindPerSys, '-k')
# plt.polar(monthVecRadial, monthlyWindPerSys[0:13], '-c',
#           monthVecRadial, monthlyWindPerSys[12:25], '-y',
#           monthVecRadial, monthlyWindPerSys[24:37], '-m',
#           monthVecRadial, monthlyWindPerSys[36:49], '-r',
#           monthVecRadial, monthlyWindPerSys[48:61], '-g',
#           monthVecRadial, monthlyWindPerSys[60:73], '-b',
#           monthVecRadial[:-1], monthlyWindPerSys[72:85], '-k'
#           )

# print("First 10:")
# print(df[0:10])
# print("...")
# print("Last 10:")
# print(df[-10:])


# try:
#     dn = df[df[df.columns[iData]] != '-'].to_numpy()
# except:
#     dn = df.to_numpy()

# t = [datetime.strptime(dTmp, "%d %B %Y %H:%M").toordinal() for dTmp in dn[:,0]]
# dn[:,iData] = [int(dTmp) for dTmp in dn[:,iData]]
# dn=np.c_[dn,t]
# dn = dn[np.argsort(dn[:, -1])]

# print("First 10:")
# print(dn[0:10,:])
# print("...")
# print("Last 10:")
# print(dn[-10:,:])

# plt.figure()
# plt.plot(dn[:,-1], dn[:,iData])
# plt.title(dataName)
    