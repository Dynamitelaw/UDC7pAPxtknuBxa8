'''
Dynamitelaw

This selector uses the greatest machine learning technique known to man...
pulling shit out of your ass (now with some Neural Networks sprinkled in)
'''

#External Imports
import numpy as np
import multiprocessing
from multiprocessing import Pool
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import numpy.ma as ma
import sys
import pandas as pd
from numpy.random import uniform, seed
from keras.models import load_model

#Custom Imports
sys.path.append("./")
import SystemPathImports
from StockSelectionInterface import stockSelector
import PandaDatabase as database 
import utils


class MehSelector(stockSelector):
    def __init__(self, genericParameters=[]):
        '''
        MehSelector constructor. No genericParameters are required
        '''
        super().__init__(self)
        self.ProfitSpeedFilterModel = load_model("Selectors\\Models\\TestModel_10D.h5")

    
    def selectStocksToBuy(self, maxNumberOfStocks, date=False, customTickerList=False, genricParameters=[]):
        '''
        Selects which stocks to buy, and the proportion of funds to be allocated to each.
        maximumNumberOfStocks is the highest number of stocks the caller wants to select.
        Passing a date parameter will select stocks for the given date. Ommitting it will
        select stocks based on realtime data.
        Passing a customTickerList will only analyze tickers included in that list.

        Returns a list of in the following format: [ [Ticker1, RatioOfFundAllocation1], [Ticker2, RatioOfFundAllocation2], ... ] .
        All ratios will add up to 1.
        '''

        if (not date):
            raise ValueError("Real time selection not availible for this selector")
        else:
            if (customTickerList):
                tickerList = customTickerList
            else:
                tickerList = database.getTickerList()
            
            stocksToConsider = self.filterStocksToConsider(tickerList, date)
        
            if (len(stocksToConsider) > maxNumberOfStocks):
                stocksToConsider = stocksToConsider[0:maxNumberOfStocks]
            else:
                pass

            numberOfStocks = len(stocksToConsider)
            stocksToBuy = [(i,1/numberOfStocks) for i in stocksToConsider]

            return stocksToBuy


    def selectStocksToSell(self, listOfOwnedStocks, date=False, genricParameters=[]):
        '''
        Selects which stocks to sell.
        Passing a date parameter will select stocks for the given date. Ommitting it will
        select stocks based on realtime data.

        Returns a list of stocks to sell.
        ''' 

        if (not date):
            raise ValueError("Real time selection not availible for this selector")
        else:
            tickerList = listOfOwnedStocks
            
            stocksToSell = []
            for ticker in tickerList:
                try:
                    stockData = database.getDataframe(ticker, dataFields= ["2D Discrete Moementum"], dateRange=[date, date])
                    twoDayDiscreteMomentum = float(stockData["2D Discrete Moementum"])
                    if (twoDayDiscreteMomentum < 1):
                        stocksToSell.append(ticker)
                except:
                    pass

            return stocksToSell


    def getName(self):
        return "MehSelector"

    #------------------------------------------
    #Private or noninterface methods below here    
    #------------------------------------------
    def filterStocksToConsider(self, tickerList, date=False):
        '''
        Filters out the inputted list of tickers. Returns a list of stocks to consider buying
        '''
        sortedTickersToConsider = self.NNPositiveProfitSpeedFilter(tickerList, date)
        sortedTickersToConsider = self.heatmapBasedFilter(sortedTickersToConsider, date)

        return sortedTickersToConsider        

    
    def NNPositiveProfitSpeedFilter(self, tickerList, date=False):
        '''
        Filters stocks that have a positive predicted profit speed using the trained NN.
        Sorts the output list based on the probability that the profit speed will be positive.
        '''
        if (not date):
            raise ValueError("Real time selection not availible for this selector")
        else:
            #Get datapoints to feed through the NN
            argList = []
            for ticker in tickerList:
                argList.append((ticker, date))

            processCount = multiprocessing.cpu_count() - 1
            processPool = Pool(processCount)

            results = list(processPool.map(addDatapointsFromStock, argList))
            processPool.close()
            processPool.join()

            allDataPoints = []
            for dataPoints in results:
                if (dataPoints != False):
                    allDataPoints.append(dataPoints)

            if (len(allDataPoints) == 1):
                InputData = allDataPoints[0][1]
            elif (len(allDataPoints) == 0):
                return []
            else:
                InputData = [[i[1] for i in allDataPoints]]
            
            InputTickers = [i[0] for i in allDataPoints]
            
            try:
                #Predict profit speed
                positiveProbabilities = self.ProfitSpeedFilterModel.predict(InputData)
            except Exception as e:
                print("#################################")
                print(e)
                print(InputData)
                print("#################################")
                return []


            stocksToConsider = []

            #Create a list of predicted positve tickers
            for i in range(0, len(positiveProbabilities), 1):
                ticker = InputTickers[i]
                prediction = positiveProbabilities[i][0]
                if (prediction > 0.5):
                    stocksToConsider.append((prediction, ticker))

            #Sort in descending order
            stocksToConsider.sort(reverse=True)

            #Extract tickers from sorted list
            sortedTickers = [i[1] for i in stocksToConsider]

            return sortedTickers

        
    def heatmapBasedFilter(self, tickerList, date=False):
        '''
        Filters stocks that have a positive predicted profit speed using Joey's paint.Net lines
        '''
        if (not date):
            raise ValueError("Real time selection not availible for this selector")

        argList = []
        for ticker in tickerList:
            argList.append((ticker, date))

        processCount = multiprocessing.cpu_count() - 1
        processPool = Pool(processCount)

        results = list(processPool.map(joeysPaintFilter, argList))
        processPool.close()
        processPool.join()

        fitleredTickers = []
        for ticker in results:
            if (ticker != False):
                fitleredTickers.append(ticker)

        return fitleredTickers


def addDatapointsFromStock(args):
    '''
    Returns the datapoints for a single stock, or False if data in unavailable or missing

    args is a tuple passed in the following format: (ticker, date)
    Returns a tuple in the following format:
        (string ticker, array_type datapoints)
    '''

    ticker = args[0]
    date = args[1]

    if (not date):
        raise ValueError("Real time selection not availible for this selector")

    try:
        #Get all data for stock
        dataFields = ["2 Day Normalized Slope", "5 Day Normalized Slope", "2 Day Normalized Momentum", "5 Day Normalized Momentum", "2D Discrete Moementum", "5D Discrete Moementum", "Standard Dev Normalized"]
        stockData = database.getDataframe(ticker, dataFields= dataFields)

        #Get the input datapoints for this day
        daysToPass = 10
        endDateIndex = stockData.index.get_loc(date)[0]
        startDateIndex = endDateIndex + daysToPass
        dataframeSlice = stockData[endDateIndex:startDateIndex]

        #Check for missing data
        dataframeSlice.dropna(inplace = True)
        if (len(dataframeSlice) < daysToPass):
            return False
        
        networkInputs = dataframeSlice.values.flatten()
        returnTuple = (ticker, networkInputs)

        return returnTuple

    except Exception as e:
        #print(e)
        return False


def joeysPaintFilter(args):
    '''
    Filters a single stock based on Joey's beautiful piecewise functions drawn in paint.
    Returns False if the stock did not pass the filter
    '''
    ticker = args[0]
    date = args[1]

    dataFields = ["2 Day Normalized Slope", "5 Day Normalized Slope", "2D Discrete Moementum", "5D Discrete Moementum"]
    stockData = database.getDataframe(ticker, dataFields= dataFields, dateRange=[date, date])
    
    twoDaySlope = float(stockData["2 Day Normalized Slope"])
    fiveDaySlope = float(stockData["5 Day Normalized Slope"])

    if ((twoDaySlope > 0.2) and (fiveDaySlope > -4.5) and (fiveDaySlope > ((-1.8333*twoDaySlope)+1.3666))):
        pass
    else:
        #Doesn't pass the slope piecewise filter
        return False

    twoDayDiscreteMomentum = float(stockData["2D Discrete Moementum"])
    fiveDayDiscreteMomentum = float(stockData["5D Discrete Moementum"])
    
    if ((fiveDayDiscreteMomentum < 3) and (twoDayDiscreteMomentum > 0)):
        pass
    else:
        return False

    return ticker

        
if __name__ == '__main__':
    selector = MehSelector()
    date =  "2018-06-14"
    numberOfStocks = 4000
    tickerList = database.getTickerList(randomize=True)[0:numberOfStocks]
    #tickerList = ["TSLA"]
    selectedStocks = selector.selectStocksToBuy(10, date, tickerList)
    print(selectedStocks)
    for selection in selectedStocks:
        ticker = selection[0]
        stockData = database.getDataframe(ticker, dataFields= ["Profit Speed", "2 Day Normalized Momentum", "5 Day Normalized Momentum", "2D Discrete Moementum", "5D Discrete Moementum"], dateRange=[date, date])
        print(stockData)
    #date2 = "2018-02-08"
    #selector.NNPositiveProfitSpeedFilter(tickerList, date2)

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

#=============================================================================
#   2D and 5D normalized slopes
#=============================================================================

dataColumns = ["2 Day Normalized Slope", "5 Day Normalized Slope", "Profit Speed"]
holderDataframe = pd.DataFrame(columns=dataColumns)

i = 0
numberOfStocks = len(tickerList)
for ticker in tickerList:
    i += 1
    stockData = database.getDataframe(ticker, dataFields=["Open", "2 Day Slope", "5 Day Slope", "Profit Speed"], dateRange=["2016-06-07", "2018-06-06"])  #"2010-01-01", "2016-06-06"
    
    try:
        tempDataframe = pd.DataFrame(columns=dataColumns)

        #Multiple by 1000 for a more convenient scale. Should probably be 100, that way data points would represent % values
        tempDataframe["2 Day Normalized Slope"] = stockData["2 Day Slope"] / stockData["Open"] * 100
        tempDataframe["5 Day Normalized Slope"] = stockData["5 Day Slope"] / stockData["Open"] * 100
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

c = 10
g = 1
model, accuracy = createSlopesSVMmodel(c = c, gamma= g)

#model.predict()
#Joey's ghetto paint filter (plus removing 0s for more accurate histogram)
#goodRegionDataframe = holderDataframe[holderDataframe.apply(lambda row: (row["2 Day Normalized Slope"] > 2) and (row["5 Day Normalized Slope"] > -45) and (row["5 Day Normalized Slope"] > ((-1.8333*row["2 Day Normalized Slope"])+(13.6666))) and (row["Profit Speed"] != 0), axis=1)]
goodRegionDataframe = holderDataframe[holderDataframe.apply(lambda row: bool(model.predict([[float(row["2 Day Normalized Slope"]), float(row["5 Day Normalized Slope"])]])[0]), axis=1)]
goodRegionDataframe = holderDataframe[holderDataframe.apply(lambda row: row["Profit Speed"] != 0, axis=1)]
goodRegionHistogram = goodRegionDataframe["Profit Speed"].plot.hist(ax=axes[1], alpha=0.5, bins=bins)
print(len(goodRegionDataframe))

utils.emitAsciiBell()
plt.show()


#=============================================================================
#   Contour Map
#=============================================================================

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

