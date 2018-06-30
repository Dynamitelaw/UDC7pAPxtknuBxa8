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


    def loadEntireDatabase(self):
        '''
        Loads ALL CSVs in PcsData into memory as dataframe objects. 
        Constructs a dictionary of dataframes, with the key value being the ticker
        '''
        fileList = os.listdir(self.processedDataPath)
        
        processCount = multiprocessing.cpu_count() - 1
        processPool = Pool(processCount)

        results = list(processPool.map(self.loadDataframeFromFile, fileList))
        processPool.close()
        processPool.join()

        for keyFramePair in results:
            self.dataframeDict[keyFramePair[0]] = keyFramePair[1]


    def __loadDataframeFromFile(self, fileName):
        '''
        PRIVATE METHOD : DO NOT CALL
        Returns a list [ticker, dataframe]
        '''
        ticker = fileName.rstrip(".csv")
        dataframe = pd.read_csv(self.processedDataPath+"\\"+fileName, index_col=0)
        return [ticker, dataframe]

    
    def getDataframe(self, ticker):
        '''
        Returns the dataframe corresponding to the passed ticker.
        Returns False if dataframe is not present
        '''
        try:
            return self.dataframeDict[ticker]
        except:
            try:
                return self.__loadDataframeFromFile(ticker+".csv")[1]
            except:
                return False

    
    def saveDataframe(self, ticker, dataFrame):
        '''
        Saves the passed dataframe to a csv file
        '''
        dataFrame.to_csv(self.processedDataPath+"\\"+ticker+".csv")




       