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
import time
import random


class database:
    '''
    Class used for storing and retrieving data from PcsData
    *Note: Dates are used as row idexes, but are stored as integers
        rather than strings (more efficient), in the following format: YYYYMMDD
    '''

    def __init__(self):
        '''
        Database constructor. 
        '''
        self.dataframeDict = {}
        self.processedDataPath = "Data\PcsData"
        
        self.tickerList = []
        fileList = os.listdir(self.processedDataPath)
        for fileName in fileList:
            self.tickerList.append(fileName.rstrip(".csv"))


    def loadDatabaseToMemory(self, customTickerList=False):
        '''
        Loads ALL CSVs in PcsData into memory as dataframe objects. 
        Constructs a dictionary of dataframes, with the key value being the ticker.
        Passing a custom ticker list will only load those tickers into memory.
        '''
        if (customTickerList):
            fileList = []
            for ticker in customTickerList:
                fileList.append(ticker+".csv")
        else:
            fileList = os.listdir(self.processedDataPath)
        
        processCount = multiprocessing.cpu_count() - 1
        processPool = Pool(processCount)

        results = list(processPool.map(self.loadDataframeFromFile, fileList))
        processPool.close()
        processPool.join()

        for keyFramePair in results:
            self.dataframeDict[keyFramePair[0]] = keyFramePair[1]


    def loadDataframeFromFile(self, fileName):
        '''
        PRIVATE METHOD : DO NOT CALL
        Returns a list [ticker, dataframe]
        '''
        ticker = fileName.rstrip(".csv")
        dataframe = pd.read_csv(self.processedDataPath+"\\"+fileName, index_col=0)
        return [ticker, dataframe]

    
    def getDataframe(self, ticker, dateRange=False, dataFields=False):
        '''
        Returns the dataframe corresponding to the passed ticker.
        Returns False if dataframe is not present or values requested are not valid.

        Daterange must be a 2 element list, in the following format: [[<start date>], [<end date>]], date format = int YYYYMMDD.
        dateFields must be a list of strings corresponding to the columns of the dataframe you want returned.
        '''
        try:
            dataframe = self.dataframeDict[ticker]

            if (dateRange):
                if (dataFields):
                    dataframeReturn = dataframe.loc[dateRange[0]:dateRange[1],dataFields]
                else:
                    dataframeReturn = dataframe.loc[dateRange[0]:dateRange[1]]
            elif (dataFields):
                if (dateRange):
                    dataframeReturn = dataframe.loc[dateRange[0]:dateRange[1],dataFields]
                else:
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

            try:
                if (dateRange):
                    if (dataFields):
                        dataframe = self.__loadDataframeFromFile(ticker+".csv")[1].loc[dateRange[0]:dateRange[1],dataFields]
                    else:
                        dataframe = self.__loadDataframeFromFile(ticker+".csv")[1].loc[dateRange[0]:dateRange[1]]
                elif (dataFields):
                    if (dateRange):
                        dataframe = self.__loadDataframeFromFile(ticker+".csv")[1].loc[dateRange[0]:dateRange[1],dataFields]
                    else:
                        dataframe = self.__loadDataframeFromFile(ticker+".csv")[1][dataFields]
                else:
                    dataframe = self.__loadDataframeFromFile(ticker+".csv")[1]

                if (len(dataframe) == 0):
                    #Data is not available
                    return False
                else:
                    return dataframe
            except:
                return False

    
    def saveDataframe(self, ticker, dataFrame):
        '''
        Saves the passed dataframe to a csv file
        '''
        dataFrame.to_csv(self.processedDataPath+"\\"+ticker+".csv")

    
    def getTickerList(self, randomize=False, numberOfShuffles=1):
        '''
        Returns a list of tickers present in the database.
        Setting randomize to True will shuffled the locations of tickers in the list
        Number of shuffles can also be specified
        '''
        if (randomize):
            returnList = self.tickerList[:]
            for i in range(0,numberOfShuffles,1):
                random.shuffle(returnList)
            
            return returnList

        return self.tickerList




       