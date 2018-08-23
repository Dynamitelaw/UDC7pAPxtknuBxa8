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
    print(bool(1))

    #print(levels)
    
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

    