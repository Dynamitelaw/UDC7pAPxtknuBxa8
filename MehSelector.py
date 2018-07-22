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
import sys
sys.path.append("./SVM_Models")
from svm_models import createSlopesSVMmodel
from numpy.random import uniform, seed
import utils


tickerList = database.getTickerList()
'''
#=============================================================================
#   Normalized Continuous Momentum
#=============================================================================
dataColumns = ["2 Day Normalized Momentum", "5 Day Normalized Momentum", "Profit Speed"]
holderDataframe = pd.DataFrame(columns=dataColumns)

i = 0
numberOfStocks = len(tickerList)
for ticker in tickerList:
    i += 1
    stockData = database.getDataframe(ticker, dataFields=["Open", "2 Day Momentum", "5 Day Momentum", "Profit Speed"], dateRange=["2010-01-01", "2016-06-06"])  #"2010-01-01", "2016-06-06"  |  "2016-06-07", "2018-06-06"
    
    try:
        tempDataframe = pd.DataFrame(columns=dataColumns)

        #Multiple by 1000 for a more convenient scale. Should probably be 100, that way data points would represent % values
        tempDataframe["2 Day Normalized Momentum"] = stockData["2 Day Momentum"] / stockData["Open"] * 1000
        tempDataframe["5 Day Normalized Momentum"] = stockData["5 Day Momentum"] / stockData["Open"] * 1000
        tempDataframe["Profit Speed"] = stockData["Profit Speed"] * 1000

        holderDataframe = holderDataframe.append(tempDataframe, ignore_index=True)
    except:
        pass

    utils.printProgressBar(i, numberOfStocks)

holderDataframe.dropna(axis=0, how='any', inplace=True)

#Filter out extreme  outliers by only plotting the middle 95% of each column
holderDataframe.sort_values(by="2 Day Normalized Momentum", inplace=True)
holderDataframe.reset_index(drop=True, inplace=True)
startingIndex = int(len(holderDataframe) * 0.025)
endingIndex = int(len(holderDataframe) * 0.975)
holderDataframe = holderDataframe.iloc[startingIndex:endingIndex]

holderDataframe.sort_values(by="5 Day Normalized Momentum", inplace=True)
holderDataframe.reset_index(drop=True, inplace=True)
startingIndex = int(len(holderDataframe) * 0.025)
endingIndex = int(len(holderDataframe) * 0.975)
holderDataframe = holderDataframe.iloc[startingIndex:endingIndex]

holderDataframe.sort_values(by="Profit Speed", inplace=True)
holderDataframe.reset_index(drop=True, inplace=True)
startingIndex = int(len(holderDataframe) * 0.025)
endingIndex = int(len(holderDataframe) * 0.975)
holderDataframe = holderDataframe.iloc[startingIndex:endingIndex]
'''
#=============================================================================
#   2D and 5D normalized slopes
#=============================================================================

dataColumns = ["2 Day Normalized Slope", "5 Day Normalized Slope", "Profit Speed"]
holderDataframe = pd.DataFrame(columns=dataColumns)

i = 0
numberOfStocks = len(tickerList)
for ticker in tickerList[0:50]:
    i += 1
    stockData = database.getDataframe(ticker, dataFields=["Open", "2 Day Slope", "5 Day Slope", "Profit Speed"], dateRange=["2016-06-07", "2018-06-06"])  #"2010-01-01", "2016-06-06"
    
    try:
        tempDataframe = pd.DataFrame(columns=dataColumns)

        #Multiple by 1000 for a more convenient scale. Should probably be 100, that way data points would represent % values
        tempDataframe["2 Day Normalized Slope"] = stockData["2 Day Slope"] / stockData["Open"] 
        tempDataframe["5 Day Normalized Slope"] = stockData["5 Day Slope"] / stockData["Open"] 
        tempDataframe["Profit Speed"] = stockData["Profit Speed"] 

        holderDataframe = holderDataframe.append(tempDataframe, ignore_index=True)
    except:
        pass

    utils.printProgressBar(i, numberOfStocks)

holderDataframe.dropna(axis=0, how='any', inplace=True)

#Filter out extreme  outliers by only plotting the middle 95% of each column
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


#=============================================================================
#   Slope Histograms
#=============================================================================

#Generate Bins
numberOfBins = 30
maxProfit = holderDataframe["Profit Speed"].max()
minProfit = holderDataframe["Profit Speed"].min()
binWidth = (maxProfit - minProfit) / numberOfBins
bins = []
bins.append(0)

#Negative Bins
while (True):
    newBin = bins[0] - binWidth
    bins.insert(0, newBin)
    if (newBin < minProfit):
        break

#Postive Bins
while (True):
    newBin = bins[len(bins)-1] + binWidth
    bins.append(newBin)
    if (newBin > maxProfit):
        break

fig, axes = plt.subplots(nrows=2, ncols=1)
histogramAll = holderDataframe["Profit Speed"].plot.hist(ax=axes[0], alpha=0.5, bins=bins)

c = 10000
g = 1
model, accuracy = createSlopesSVMmodel(c = c, gamma= g)

#model.predict()
#Joey's ghetto paint filter (plus removing 0s for more accurate histogram)
#goodRegionDataframe = holderDataframe[holderDataframe.apply(lambda row: (row["2 Day Normalized Slope"] > 2) and (row["5 Day Normalized Slope"] > -45) and (row["5 Day Normalized Slope"] > ((-1.8333*row["2 Day Normalized Slope"])+(13.6666))) and (row["Profit Speed"] != 0), axis=1)]
goodRegionDataframe = holderDataframe[holderDataframe.apply(lambda row: bool(model.predict([[float(row["2 Day Normalized Slope"]), float(row["5 Day Normalized Slope"])]])[0]), axis=1)]
goodRegionHistogram = goodRegionDataframe["Profit Speed"].plot.hist(ax=axes[1], alpha=0.5, bins=bins)
print(len(goodRegionDataframe))

utils.emitAsciiBell()
plt.show()


#=============================================================================
#   Contour Map
#=============================================================================
'''
#Change Column names depending on what you're plotting
x, y, z = np.array(holderDataframe["2 Day Normalized Momentum"].values), np.array(holderDataframe["5 Day Normalized Momentum"].values), np.array(holderDataframe["Profit Speed"].values)

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

#Change title 
plt.title("2 Day Normalized Momentum vs 5 Day Normalized Momentum vs ProfitSpeed")

utils.emitAsciiBell()
plt.show()
'''

