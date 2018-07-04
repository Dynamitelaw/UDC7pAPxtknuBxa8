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







if __name__ == '__main__':
    date = "2017-01-04"
    ticker = "GM"
    quantityOwned = 1
    stocksOwned = {}
    stocksOwned["GM"] = (0,0,0,0)
    if (date):
        tickerData = database.getDataframe(ticker)
        try:
            isMissing = pd.isnull(tickerData).loc[date,"Open"]
            print(isMissing.bool())
            if (not isMissing):
                value = tickerData.loc[date, "Open"]
            else:
                value = stocksOwned.get(ticker)[3]
        except Exception as e:
            #Using old value if current value cannot be found
            print(e)
            value = stocksOwned.get(ticker)[3]
    else:
        pass

    print (tickerData.loc[date, "Open"])
    
    print (date + ": "+ticker + "  $" + str(float(value)))


    
    
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

    