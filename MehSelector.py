'''
Dynamitelaw

Uses the greatest machine learning technique known by man...
pulling shit out of your ass
'''

import PandaDatabase as database 
import pandas as pd

import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import numpy.ma as ma
from numpy.random import uniform, seed
import utils


tickerList = database.getTickerList()

dataColumns = ["2 Day Normalized Slope", "5 Day Normalized Slope", "Profit Speed"]
holderDataframe = pd.DataFrame(columns=dataColumns)

i = 0
numberOfStocks = len(tickerList)
for ticker in tickerList:
    i += 1
    stockData = database.getDataframe(ticker, dataFields=["Open", "2 Day Slope", "5 Day Slope", "Profit Speed"], dateRange=["2010-01-01", "2016-06-06"])
    
    try:
        tempDataframe = pd.DataFrame(columns=dataColumns)

        tempDataframe["2 Day Normalized Slope"] = stockData["2 Day Slope"] / stockData["Open"] * 1000
        tempDataframe["5 Day Normalized Slope"] = stockData["5 Day Slope"] / stockData["Open"] * 1000
        tempDataframe["Profit Speed"] = stockData["Profit Speed"] * 1000

        holderDataframe = holderDataframe.append(tempDataframe, ignore_index=True)
    except:
        pass

    utils.printProgressBar(i, numberOfStocks)

holderDataframe.dropna(axis=0, how='any', inplace=True)

holderDataframe.sort_values(by="2 Day Normalized Slope", inplace=True)
holderDataframe.reset_index(drop=True, inplace=True)
startingIndex = int(len(holderDataframe) * 0.025)
endingIndex = int(len(holderDataframe) * 0.975)
holderDataframe = holderDataframe.iloc[startingIndex:endingIndex]

holderDataframe.sort_values(by="5 Day Normalized Slope", inplace=True)
holderDataframe.reset_index(drop=True, inplace=True)
startingIndex = int(len(holderDataframe) * 0.025)
endingIndex = int(len(holderDataframe) * 0.975)
holderDataframe = holderDataframe.iloc[startingIndex:endingIndex]

holderDataframe.sort_values(by="Profit Speed", inplace=True)
holderDataframe.reset_index(drop=True, inplace=True)
startingIndex = int(len(holderDataframe) * 0.025)
endingIndex = int(len(holderDataframe) * 0.975)
holderDataframe = holderDataframe.iloc[startingIndex:endingIndex]

print("\n" + str(len(holderDataframe)) + " datapoints")
# histogram = holderDataframe["Profit Speed"].plot.hist()
# plt.show()

x, y, z = np.array(holderDataframe["2 Day Normalized Slope"].values), np.array(holderDataframe["5 Day Normalized Slope"].values), np.array(holderDataframe["Profit Speed"].values)

# define grid.
xi = np.linspace(np.amin(x),np.amax(x),100)
yi = np.linspace(np.amin(y), np.amax(y),100)
# grid the data.
zi = griddata((x, y), z, (xi[None,:], yi[:,None]), method='cubic')

# contour the gridded data, plotting dots at the randomly spaced data points.

levels = list(np.linspace(np.amin(z)*1.1, 0, 4))
levelToInsert = (levels[-1]+levels[-2])/3
levels.insert(1, levelToInsert)
levelsToAppend = list(np.linspace(0, np.amax(z)*1.1, 4))
levelToInsert = (levelsToAppend[0]+levelsToAppend[1])/3
levelsToAppend.insert(1, levelToInsert)
levels += levelsToAppend
levels = sorted(list(set(levels)))

CS = plt.contour(xi,yi,zi,15,linewidths=0.5,colors='k', vmin=np.amin(z), vmax=np.amax(z), levels=levels)
CS = plt.contourf(xi,yi,zi,15,cmap=plt.cm.jet, vmin=np.amin(z), vmax=np.amax(z), levels=levels)
plt.colorbar() # draw colorbar
# plot data points.
# plt.scatter(x,y,marker='o',c='b',s=5)
plt.xlim(np.amin(x),np.amax(x))
plt.ylim(np.amin(y),np.amax(y))
plt.title("2 Day Normalized Slope vs 5 Day Normalized Slope vs ProfitSpeed")

utils.emitAsciiBell()

plt.show()
