'''
Dynamitelaw

TestSelector: a selector that has oracle knowledge of market.
Used only for testing functionality of other interfaces.
Decisions have a degree of randomness for more accurate testing.
'''

import pandas as pd
import PandaDatabase as database
import multiprocessing
from multiprocessing import Pool
import numpy as np
from random import randint
import random
from StockSelectionInterface import stockSelector


class TestSelector(stockSelector):
    def __init__(self, genericParameters=[]):
        '''
        SimpleSlopeSelctor constructor. No genericParameters are required
        '''
        super().__init__(self)
        
        self.name = "TestSelector"

    
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
            argList = []
            for ticker in tickerList:
                argList.append([ticker, date])

            processCount = multiprocessing.cpu_count()-1
            processPool = Pool(processCount)
            results = list(processPool.map(self.getProfitSpeed, argList))
            processPool.close()
            processPool.join()

            for i in range(len(results)-1, -1, -1):
                if (results[i]):
                    pass
                else:
                    del results[i]

            results = sorted(results)
            #print(results)
            
            randomnessFactor = 0.85  #Used to randomize selection so that the selector isn't perfect. 0 is perfect, 1 is completely random

            lengthOfResults = len(results)
            #print(lengthOfResults)
            
            indexesOfChosenStocks = []
            for i in range(0, maxNumberOfStocks, 1):
                if (lengthOfResults-len(indexesOfChosenStocks)>0):
                    #There are still stocks left to chose from
                    while (True):                        
                        indexToUse = randint(int(randomnessFactor*(lengthOfResults-1)), lengthOfResults-1)
                        if (indexToUse in indexesOfChosenStocks):
                            pass
                        else:
                            indexesOfChosenStocks.append(indexToUse)
                            break
                else:
                    #There are no more stocks left to select
                    break

            #print(indexesOfChosenStocks)

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

            processCount = multiprocessing.cpu_count()-1
            processPool = Pool(processCount)
            results = processPool.map(self.getProfitSpeed, argList)
            processPool.close()
            processPool.join()

            for i in range(len(results)-1, -1, -1):
                if (results[i]):
                    pass
                else:
                    del results[i]

            results = sorted(results)
            
            randomnessFactor = 0.5  #Used to randomize selection so that the selector isn't perfect. 0 is perfect, 1 is completely random

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

        try:
            dataframe = database.getDataframe(ticker, dateRange=[date,date], dataFields=["Profit Speed"])# .at[date,"Profit Speed"]
            #print(dataframe)

            try:
                isMissing = pd.isnull(dataframe).loc[date,"Profit Speed"]
            except Exception as e:
                isMissing = True
            if (isMissing):
                #Profit speed data is missing. Return nothing
                del dataframe
                pass
            else:
                profitSpeed = dataframe.loc[date,"Profit Speed"]
                del dataframe
                return [profitSpeed, ticker]
        except:
            pass

        
