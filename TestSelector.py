'''
Dynamitelaw

TestSelector: a selector that has oracle knowledge of market.
Used only for testing functionality of other interfaces.
Decisions have a degree of randomness for more accurate testing.
'''

import pandas as pd
from PandaDatabase import database
import multiprocessing
from multiprocessing import Pool
import numpy as np
from random import randint
import random


class selector():
    def __init__(self, databaseInterface, genericParameters=[]):
        '''
        SimpleSlopeSelctor constructor. No genericParameters are required
        '''
        if ( type(databaseInterface).__name__ !='database'):
            raise ValueError("Invalid parameter. databaseInterface must be of type \"<class 'PandaDatabase.database'>\". Recieved {}".format(type(databaseInterface)))
        
        self.database = databaseInterface

    
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
                tickerList = self.database.getTickerList()
            argList = []
            for ticker in tickerList:
                argList.append([ticker, date])

            processCount = int(float(multiprocessing.cpu_count())*1.5)
            processPool = Pool(processCount)
            results = processPool.map(self.getProfitSpeed, argList)

            for i in range(len(results)-1, -1, -1):
                if (results[i]):
                    pass
                else:
                    del results[i]

            results = sorted(results)
            
            randomnessFactor = 0.8  #Used to randomize selection so that the selector isn't perfect. 0 is perfect, 1 is completely random

            lengthOfResults = len(results)
            indexesOfChosenStocks = []
            for i in range(0, maxNumberOfStocks, 1):
                while (True):
                    indexToUse = randint(int(randomnessFactor*(lengthOfResults-1)), lengthOfResults-1)
                    if (indexToUse in indexesOfChosenStocks):
                        pass
                    else:
                        indexesOfChosenStocks.append(indexToUse)
                        break

            stocksToConsider = []
            for index in indexesOfChosenStocks:
                stocksToConsider.append(results[index])
            
            randomRatios = list(np.random.dirichlet(np.ones(maxNumberOfStocks),size=1)[0])  #https://stackoverflow.com/questions/18659858/generating-a-list-of-random-numbers-summing-to-1
        
            stocksToBuy = []
            for i in range(0, len(stocksToConsider), 1):
                stocksToBuy.append([stocksToConsider[i][1], randomRatios[i]])

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
            
            argList = []
            for ticker in tickerList:
                argList.append([ticker, date])

            processCount = int(float(multiprocessing.cpu_count())*1.5)
            processPool = Pool(processCount)
            results = processPool.map(self.getProfitSpeed, argList)

            for i in range(len(results)-1, -1, -1):
                if (results[i]):
                    pass
                else:
                    del results[i]

            results = sorted(results)
            
            randomnessFactor = 0.2  #Used to randomize selection so that the selector isn't perfect. 0 is perfect, 1 is completely random

            stocksToSell = []
            for stock in results:
                ticker = stock[1]
                profitSpeed = stock[0]

                if (profitSpeed <= 0):
                    if (random.random() > randomnessFactor):
                        stocksToSell.append(ticker)

            return stocksToSell


    #------------------------------------------
    #Private or noninterface methods below here    
    #------------------------------------------
    def getProfitSpeed(self, args):
        '''
        PRIVATE METHOD

        args is a list passed in the following format: [ticker, date]
        Returns a list in the following format: [profitSpeed, ticker]
        '''
        ticker = args[0]
        date = args[1]
        tempDatabaseInterface = database() #instantiate a local database interface in order to support multithreading

        try:
            dataframe = tempDatabaseInterface.getDataframe(ticker, dateRange=[date,date], dataFields=["Profit Speed"])# .at[date,"Profit Speed"]
            
            if (pd.isnull(dataframe).at[date,"Profit Speed"] == True):
                #Profit speed data is missing. Return nothing
                pass
            else:
                profitSpeed = dataframe.at[date,"Profit Speed"]
                return [profitSpeed, ticker]
        except:
            pass

        
