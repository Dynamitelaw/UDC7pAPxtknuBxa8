import multiprocessing
from multiprocessing import Pool
import sys
import utils
from utils import printLocation
import time
import numpy as np
from PandaDatabase import database
from TestSelector import TestSelector
from TradingAccount import tradingAccount
import os


def fixDates(filename):
    filepath = "Data\PcsData\\" + filename

    infile = open(filepath,'r')
    outfile = open("Data\PcsData\\"+ filename + ".tmp", 'w')

    top = True
    for line in infile:
        if (top):
            outfile.write(line)
            top = False
        else:
            lineList = line.split(",")
            dateInteger = lineList[0]
            dateString = utils.convertDate(dateInteger, outputFormat="String")
            outfile.write(dateString+",")
            for i in range(1, len(lineList)-1, 1):
                outfile.write(lineList[i]+",")
            outfile.write(lineList[-1])

    infile.close()
    outfile.close()

    os.remove(filepath)
    os.rename("Data\PcsData\\"+ filename + ".tmp",filepath)
    

def fixAllDates():
    filesToFix = os.listdir("Data\PcsData")
    
    
    p = Pool(4)
    p.map(fixDates, filesToFix)


if __name__ == '__main__':
    fixAllDates()
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

    