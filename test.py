import multiprocessing
from multiprocessing import Pool
import sys
import utils
from utils import printLocation
import time
import numpy as np
import PandaDatabase as database
from TestSelector import TestSelector
from TradingAccount import tradingAccount
import os
import pandas as pd
from PandaDatabase import *






if __name__ == '__main__':
    ticker = "AAPL"
    date = "2015-01-02"
    df=getDataframe(ticker)
    date_index = df.index.get_loc(date)+1
    newDate = str(df.index[date_index].values[0])[:10]
    tickerDict = getDataframe(ticker, [newDate,newDate])
    print(tickerDict)
    print(newDate)
    
    
    #fixAllDates()
    #fixDates("APHB.csv")
    '''
    d = database()
    d.loadDatabaseToMemory(["TSLA"])
    #d.getDataframe("TSLA")
    #d.getDataframe("FBC")

    for i in range(10,21,1):
        #time.sleep(1)
        percentage = int((float(i-10)*100)/10)
        sys.stdout.write("\r")
        sys.stdout.write(str(percentage)+"%")
        sys.stdout.flush()


    #import StockSelectionInterface 
    tickerList = d.getTickerList(randomize=True)[:200]
    selector = TestSelector(d)

    results = selector.selectStocksToSell(tickerList, date=20150506)
    #print("---------------------------------------")
    print(results)


    #k = d.getDataframe("TSLA", dateRange=[20150502,20150507], dataFields=["Profit Speed"]).at[20150506,"Profit Speed"]

    #print(k)'''

    