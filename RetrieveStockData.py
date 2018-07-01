'''
Dynamitelaw

This is the interface we use to retrive stock data, both historical and current.
These function interfaces SHOULD NOT be changed.
If we have to switch APIs, we will change the function implimentations

*NOTE when installing iexfinance, it will install an older version of pandas that breaks everything else.
You must uninstall and reinstall pandas to the newest version after installing iexfinance
iexfinance documentation: https://pypi.org/project/iexfinance/
'''

import iexfinance as iex
import utils
from datetime import datetime
import pandas as pd
import sys
import multiprocessing
from multiprocessing import Pool
import tqdm


def getHistoricalData(ticker, daterange):
    '''
    Will download the historical data for the given ticker and return it as a pandas dataframe.
    Daterange must be a 2 element list, in the following format: [[<start date>], [<end date>]], date format = int YYYYMMDD
    '''
    startYear, startMonth, startDay = utils.convertDate(daterange[0])
    endYear, endMonth, endDay = utils.convertDate(daterange[1])

    start = datetime(startYear, startMonth, startDay)
    end = datetime(endYear, endMonth, endDay)

    dataframe = iex.get_historical_data(ticker, start=start, end=end, output_format='pandas')
    dataframe.head()

    return dataframe


def getCurrentPrice(ticker):
    '''
    Returns the current price of passed ticker
    '''
    return iex.Stock(ticker).get_price()

def getOpenPrice(ticker):
    '''
    Returns the most recent open price of passed ticker
    '''
    return iex.Stock(ticker).get_open()


def getNewestTickers():
    '''
    Will retrieve all tickers available through current API.
    Returns tickers as a list. This function is innefficient, so only call
    it when you need to update your ticker list.
    '''
    symbolJsonList = iex.get_available_symbols(output_format='pandas')

    listOfTickers = list(map(utils.extractTicker, symbolJsonList))
    return listOfTickers


def getCurrentTickers():
    '''
    Reads ListOfTickerSymbols.csv and returns a list of tickers
    '''
    tickerFile = open('Data/ListOfTickerSymbols.csv','r') #opens current ticker file
    
    listOfCurrentTickers = []
    for line in tickerFile:	
        listOfCurrentTickers.append(line.rstrip())

    tickerFile.close()

    return listOfCurrentTickers


def updateTickerList():
    '''
    Updates our list of tickers
    '''
    tickerFile = open('Data/ListOfTickerSymbols.csv','r') #opens current ticker file
    
    listOfCurrentTickers = []
    for line in tickerFile:	
        listOfCurrentTickers.append(line.rstrip())

    tickerFile.close()

    #Finds the unions of our current tickers with the new tickers
    updatedTickerList = list(set(listOfCurrentTickers) | set(getNewestTickers()))
    
    newTickerFile = open('Data/ListOfTickerSymbols.csv','w') 

    #Writes to file
    for ticker in updatedTickerList:
        newTickerFile.write(ticker + "\n")
    newTickerFile.close()


def updateStock(ticker):
    '''
    Will download historical data for this ticker and write csv file to the StockData folder
    '''
    startDate=20130101
    endDate = 20180628
    savepath = 'Data/StockData/'

    try:
        dataframe = getHistoricalData(ticker, [startDate, endDate])
        filepath = savepath + ticker + ".csv"
        dataframe.to_csv(filepath)
    except Exception as e:
        #print (e)
        pass


def updateStockDataFolder():
    '''
    Will download all historical data possible and write csv files to the StockData folder
    '''
    tickerList = getCurrentTickers()

    processCount = multiprocessing.cpu_count()*6
    processPool = Pool(processCount)
    for _ in tqdm.tqdm(processPool.imap_unordered(updateStock, tickerList), total=len(tickerList)):
        pass

    utils.emitAsciiBell()
        
if __name__ == '__main__':
    updateTickerList()
    updateStockDataFolder()