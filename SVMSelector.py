import os
import sys
sys.path.insert(0,'SVM_Models/')
from svm_models import createSVMmodel
from StockSelectionInterface import stockSelector
from datetime import date
from PandaDatabase import *
import numpy as np
from sklearn.preprocessing import scale
from random import shuffle

class SVMSelector(stockSelector):
    def __init__(self):
        super().__init__()
        dir="Data/SVM/1PercentGrowth3DaysAway/"
        k=0
        while k<6:
            self.clf,accuracy,buyCount,k,days,self.t_X = createSVMmodel(dir,c=100,gamma=.1,training_percent=.3,date_range=[date(2000,1,1),date(2016,1,1)])
        self.myStocks = [[],[],[],[]]
        self.cycle = 0
    def selectStocksToBuy(self, maxNumberOfStocks, date=False, customTickerList=False, genricParameters=[]):
        '''
        Selects which stocks to buy, and the proportion of funds to be allocated to each.
        maximumNumberOfStocks is the highest number of stocks the caller wants to select.
        Passing a date parameter will select stocks for the given date. Ommitting it will
        select stocks based on realtime data.
        Passing a customTickerList will only analyze tickers included in that list.

        Returns a list of in the following format: [ [Ticker1, RatioOfFundAllocation1], [Ticker2, RatioOfFundAllocation2], ... ] .
        All ratios must add up to 1.
        '''
        data = []
        tickerSubList = []

        if date == False:
            print("No date specified")
            return ValueError

        if customTickerList==False:
            customTickerList = getTickerList()

        sampleTickerList = customTickerList[:]
        shuffle(sampleTickerList)
        for ticker in sampleTickerList:
            tickerDict = getDataframe(ticker, [date,date])
            isMissing = pd.isnull(tickerDict)
            try:
                isMissing = (True in np.isnan(tickerDict.iloc[0].values))
                if tickerDict==False:
                    isMissing = True
            except:
                isMissing = True
            if not isMissing:
                line = tickerDict.iloc[0].drop(columns=["Optimal Dates","Desired Level 1 Out Buy","Desired Level 1 Out Sell","Profit Speed"]).values.tolist()
                data.append(line)
                #print(list(map(float,DatabaseDictionary[customTickerList[i]].loc[date].values.tolist()[0])))
        if len(data)==0:
            return []
        start_index = len(self.t_X)
        data = scale(np.concatenate((self.t_X,data)))
        X = self.clf.predict(data)
        count = 0
        i=len(self.t_X)
        buys=[]
        self.myStocks[self.cycle] = []
        c=0
        while count<maxNumberOfStocks and c<len(sampleTickerList):
            if X[i]==1:
                buys.append([sampleTickerList[c]])
                self.myStocks[self.cycle].append(sampleTickerList[c])
                count +=1
            i+=1
            c+=1
        for i in range(len(buys)):
            buys[i].append(1/float(len(buys)))
        self.cycle = (self.cycle+1)%4
        return buys



    def selectStocksToSell(self, listOfOwnedStocks, date=False, genricParameters=[]):
        '''
        Selects which stocks to sell.
        Passing a date parameter will select stocks for the given date. Ommitting it will
        select stocks based on realtime data.

        Returns a list of stocks to sell.
        ''' 
        if date == False:
            print("No date specified")
            raise ValueError
        
        sellList = []
        for stock in listOfOwnedStocks:
            if isMissing == False:
                pass
            else:
                isMissing = pd.isnull(getDataframe(stock, [date,date]).loc[date,'Close']) 
            if (stock in self.myStocks[self.cycle]) and (not isMissing):
                sellList.append(stock)
        return sellList

    def getName(self):
        '''
        Returns the name of the selector
        '''
        return "SVMSelector"