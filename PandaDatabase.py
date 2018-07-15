'''
Dynamitelaw

Contains all classes and methods required for retrieving data from
and sending data to the database.
'''

import pandas as pd
import os
import multiprocessing
from multiprocessing import Pool
import utils
from utils import dateParser
import time
import random
from datetime import date

DatabaseLock = multiprocessing.Lock()

DatabaseDictionary = {}
DatabaseProcessedDataPath = "Data\PcsData"

DatabaseTickerList = []
fileList = os.listdir(DatabaseProcessedDataPath)
for fileName in fileList:
    DatabaseTickerList.append(fileName.rstrip(".csv"))


def loadDatabaseToMemory(customTickerList=False):
    '''
    Loads ALL CSVs in PcsData into memory as dataframe objects. 
    Constructs a dictionary of dataframes, with the key value being the ticker.
    Passing a custom ticker list will only load those tickers into memory.
    '''
    global DatabaseDictionary
    global DatabaseProcessedDataPath

    if (customTickerList):
        fileList = []
        for ticker in customTickerList:
            fileList.append(ticker+".csv")
    else:
        fileList = os.listdir(DatabaseProcessedDataPath)
    
    fileList = list(set(fileList))
    processCount = multiprocessing.cpu_count() - 1
    processPool = Pool(processCount)

    results = list(processPool.map(loadDataframeFromFile, fileList))
    processPool.close()
    processPool.join()

    for keyFramePair in results:
        DatabaseDictionary[keyFramePair[0]] = keyFramePair[1]


def loadDataframeFromFile(fileName):
    '''
    PRIVATE METHOD : DO NOT CALL
    Returns a list [ticker, dataframe]
    '''
    DatabaseProcessedDataPath = "Data\PcsData"

    ticker = fileName.rstrip(".csv")
    #print(ticker)
    dataframe = pd.read_csv(DatabaseProcessedDataPath+"\\"+fileName, parse_dates=True)
    dataframe["date"] = pd.to_datetime(dataframe["date"], format='%Y-%m-%d')
    dataframe.set_index("date", inplace=True)
    #print(dataframe)
    return [ticker, dataframe]


def getDataframe(ticker, dateRange=False, dataFields=False, sorting=0, printError=False):
    '''
    Returns the dataframe corresponding to the passed ticker.
    Returns False if dataframe is not present or values requested are not valid.

    Daterange must be a 2 element list, in the following format: [[<start date>], [<end date>]], date format = string "YYYY-MM-DD".
    dateFields must be a list of strings corresponding to the columns of the dataframe you want returned.
    By default the dataframe is descending i.e. df.iloc[0] = 2018-01-01 df.iloc[1] = 2018-01-02 
    '''
    global DatabaseDictionary

    try:
        DatabaseLock.acquire()
        dataframe = DatabaseDictionary[ticker]
        DatabaseLock.release()

        if (dateRange):
            if type(dateRange[0]) is str:
                dateRange = [dateParser(dateRange[0]),dateParser(dateRange[1])]
            if (dataFields):
                mask = (dataframe.index >= dateRange[0]) & (dataframe.index <= dateRange[1])
                dataframeReturn = dataframe.loc[mask,dataFields]
            else:
                mask = (dataframe.index >= dateRange[0]) & (dataframe.index <= dateRange[1])
                dataframeReturn = dataframe.loc[mask]
        elif (dataFields):
            dataframeReturn = dataframe[dataFields]
        else:
            dataframeReturn = dataframe

        if (len(dataframeReturn) == 0):
            #Data is not available
            return False
        else:
            return dataframeReturn
    except:
        #Dataframe has not yet been loaded into memory. Get from file
        DatabaseLock.release()
        try:
            if (dateRange):
                if type(dateRange[0]) is str:
                    dateRange = [dateParser(dateRange[0]),dateParser(dateRange[1])]
                if (dataFields):
                    dataframe = loadDataframeFromFile(ticker+".csv")[1]
                    mask = (dataframe.index >= dateRange[0]) & (dataframe.index <= dateRange[1])
                    dataframe = dataframe.loc[mask,dataFields]
                else:
                    dataframe = loadDataframeFromFile(ticker+".csv")[1]
                    mask = (dataframe.index >= dateRange[0]) & (dataframe.index <= dateRange[1])
                    dataframe = dataframe.loc[mask]
            elif (dataFields):
                    dataframe = loadDataframeFromFile(ticker+".csv")[1][dataFields]
            else:
                dataframe = loadDataframeFromFile(ticker+".csv")[1]

            if (len(dataframe) == 0):
                #Data is not available
                return False
            else:
                #dataframe.sort_values('date',ascending=sorting)
                return dataframe
        except Exception as e:
            if printError:
                print(e)
                print(str(e))
            return False


def saveDataframe(ticker, dataFrame):
    '''
    Saves the passed dataframe to a csv file
    '''
    DatabaseProcessedDataPath = "Data\PcsData"

    dataFrame.to_csv(DatabaseProcessedDataPath+"\\"+ticker+".csv")


def getTickerList(randomize=False, numberOfShuffles=1):
    '''
    Returns a list of tickers present in the database.
    Setting randomize to True will shuffled the locations of tickers in the list
    Number of shuffles can also be specified
    '''
    global DatabaseTickerList

    if (randomize):
        returnList = DatabaseTickerList[:]
        for i in range(0,numberOfShuffles,1):
            random.shuffle(returnList)
        
        return returnList

    return DatabaseTickerList

def getSharedDates(stocks):
    '''
    Returns the range of dates shared by all of the stocks in the list 'stocks'
    '''
    if len(stocks)<2:
        print("Invalid input, 'stocks' should be a list")
        return False

    date_lists = []
    for i in range(len(stocks)):
        date_lists.append(getDataframe(stocks[i]).index)
    
    date_set = set(date_lists[0])

    for date_list in date_lists:
        date_set = date_set & set(date_list)
    
    return list(date_set)



if __name__=="__main__":
    stock = "FNX" 
    df_w_o_date = getDataframe(stock)
    print(df_w_o_date)
    valid_dates = ["1997-08-14","2013-08-15"]
    #print(valid_dates[0]==dateParser('2018-05-22'))
    df = getDataframe(stock,dateRange=[valid_dates[0],valid_dates[1]],dataFields=["Open"])
    print(df)