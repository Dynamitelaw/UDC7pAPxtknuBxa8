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
        while k<2:
            self.clf,accuracy,buyCount,k,days,self.t_X = createSVMmodel(dir,c=1000,gamma=1,training_percent=.5,date_range=[date(2013,1,1),date(2016,1,1)])
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
        
        if maxNumberOfStocks<1:
            self.cycle = (self.cycle+1)%4
            return []
        
        if date == False:
            print("No date specified")
            return ValueError

        if customTickerList==False:
            customTickerList = getTickerList()

        sampleTickerList = customTickerList[:]
        buyTickerList = []
        shuffle(sampleTickerList)
        slopeDict = {}
        for ticker in sampleTickerList:
            tickerDict = getDataframe(ticker, [date,date])
            isMissing = False
            try:
                df=getDataframe(ticker)
                date_index = df.index.get_loc(date)+1
                newDate = str(df.index[date_index].values[0])[:10]
                tickerDict = getDataframe(ticker, [newDate,newDate]).drop(columns=["Optimal Dates","Desired Level 1 Out Buy","Desired Level 1 Out Sell","Profit Speed"])
                if True in np.isnan(tickerDict.iloc[0].values):
                    isMissing = True
            except:
                isMissing = True
            if not isMissing:
                line = tickerDict.iloc[0].values.tolist()
                slopeDict[ticker] = tickerDict.iloc[0].at["5 Day Slope"]
                data.append(line)
                buyTickerList.append(ticker)
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
        while c<len(buyTickerList):
            if X[i] == 0:
                slopeDict.pop(buyTickerList[c],None)
            if X[i] == 1:
                alreadyOwn = False
                for stockList in self.myStocks:
                    if buyTickerList[c] in stockList:
                         alreadyOwn = True
                    if alreadyOwn:
                        slopeDict.pop(buyTickerList[c],None)
            c+=1
            i+=1    
        maxStock = min(slopeDict.keys(), key=(lambda k: slopeDict[k]))
        buys.append([maxStock,1])
        self.myStocks[self.cycle].append(maxStock)
            # if X[i]==1:
            #     alreadyOwn = False
            #     for stockList in self.myStocks:
            #         if buyTickerList[c] in stockList:
            #             alreadyOwn = True
            #     if not alreadyOwn:        
            #         buys.append([buyTickerList[c]])
            #         self.myStocks[self.cycle].append(buyTickerList[c])
            #     count +=1
            # i+=1
            # c+=1
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
            df = getDataframe(stock, [date,date])
            try:    
                if df!=False:
                    isMissing = pd.isnull(df.loc[date,'Close'])
                else:
                    isMissing=True 
            except:
                isMissing = False
            if (stock in self.myStocks[self.cycle]) and (not isMissing):
                sellList.append(stock)
        return sellList

    def getName(self):
        '''
        Returns the name of the selector
        '''
        return "SVMSelector"