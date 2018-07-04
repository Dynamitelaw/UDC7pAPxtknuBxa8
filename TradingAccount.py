'''
Dynamitelaw

Defines the tradingAccount class, which keeps track of balance,
trading history, owned stocks, and handles buy and sell orders.
'''

import pandas as pd
import utils
import PandaDatabase as database
import datetime
import time
import os
import RetrieveStockData as rsd


#=============================================================================
#       tradingAccount class
#=============================================================================

class tradingAccount():
    def __init__(self, name="TESTACCOUNT"):
        '''
        Trading Account constructor. Must be passed a database object.
        '''
        self.stocksOwned = {}
        self.balance = 0  #balance is an integer (in cents), NOT dollars
        self.stockAssets = 0  #assets is an integer (in cents), NOT dollars
        self.commision = 0 #balance is an integer (in cents), NOT dollars
                
        self.name = utils.sanitizeString(name)
        cwd = os.getcwd()
        self.savepath = cwd + "\\Data\AcountData\\" + self.name
 
        if not os.path.exists(self.savepath):
            os.makedirs(self.savepath)


        self.dailyLogColumns = ["Date", "Ticker", "Quantity", "Price", "Action","TimeOfExecution", "TotalAssets", "LiquidFunds", "StockAssets"]
        self.dailyLogs = pd.DataFrame(columns=self.dailyLogColumns)

        self.tradeHistoryColumns = ["Ticker", "Date Bought", "Buy Price", "Date Sold", "Sell Price", "Quantity", "Commission", "Trade Profit"]
        self.tradeHistory = pd.DataFrame(columns=self.tradeHistoryColumns)

    
    def depositFunds(self, dollarValue):
        '''
        Increase (or decrease) account balance
        '''
        if (dollarValue >= 0):
            centValue = int(dollarValue*100)
            self.balance += centValue
        else:
            raise ValueError("Negative deposit value passed")

    
    def withdrawFunds(self, dollarValue):
        '''
        Decreases account balance
        '''
        centValue = int(dollarValue*100)
        if (centValue <= self.balance):
            self.balance -= centValue
        else:
            raise ValueError("Insufficient funds to execute withdrawl")


    def getBalance(self, denomination="Dollars"):
        '''
        Returns the current account balance in specified denomination
        Valid arguments: denomination=["Dollars", "Cents"]
        '''
        if (denomination=="Dollars"):
            return (float(self.balance) / 100)
        elif (denomination=="Cents"):
            return self.balance
        else:
            raise ValueError("Invalid denomination passed")

    
    def getOwnedStocks(self):
        '''
        Returns a dictionary of stocks owned by this account
        '''
        return self.stocksOwned


    def setCommision(self, commision):
        '''
        Sets the commision on each trade (in $)
        '''
        self.commision = int(commision*100)


    def updateAssets(self, date=False):
        '''
        Updates the net value of all currently owned stock assets.
        If date is not included, the current real-time price is used.
        '''
        self.stockAssets = 0

        for ticker in self.stocksOwned:
            quantityOwned = self.stocksOwned.get(ticker)[0]
            if (date):
                tickerData = database.getDataframe(ticker)
                try:
                    isMissing = pd.isnull(tickerData).loc[date,"Open"]
                    if (not isMissing):
                        value = tickerData.loc[date, "Open"]
                    else:
                        value = self.stocksOwned.get(ticker)[3]
                except:
                    #Using old value if current value cannot be found
                    value = self.stocksOwned.get(ticker)[3]
            else:
                value = rsd.getCurrentPrice(ticker)
            
            self.stockAssets += int(value*quantityOwned*100)


    def placeBuyOrders(self, listOfOrders, date, simulation=True):
        '''
        places Sell Order for every order in listOfOrders.
        Each element in listOfOrders is a list in the following format:
            [<str ticker>, <int quantity>]
        Date is the current date, in string format "YYYY-MM-DD".
        Setting simulation to False will actually execute the buy orders (not yet implimented)
        '''
        if (not simulation):
            pass  #actually execute buy orders

        
        action = "Buy"
        executedOrders = []

        for order in listOfOrders:
            ticker = order[0]
            quantity = order[1]

            tickerData = database.getDataframe(ticker)
            openPrice = tickerData.loc[date, "Open"]
            
            self.balance -= self.commision
            tradeCost = int(openPrice*quantity*100)

            if ((self.balance - tradeCost) >= 0):
                #There is enough money for the trade
                self.balance -= tradeCost  #*100 since balance is in cents
                self.stocksOwned[ticker] = quantity, openPrice, date, openPrice  #each element in stocksOwned is ticker: (quantity, buyPrice, dateOfPurchase, mostRecentPrice)

                if (simulation):
                    self.updateAssets(date)
                else:
                    self.updateAssets()

                totalAssets = float(self.balance + self.stockAssets)/100
                
                timeStamp = time.time()
                timeOfExecution = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S')

                executedOrders.append([date, ticker, quantity, float(openPrice), action, timeOfExecution, totalAssets, float(self.balance)/100, float(self.stockAssets)/100])
                
            else:
                raise ValueError("Insufficient funds to execute trade {}".format(order))

        logAdditions = pd.DataFrame(executedOrders, columns=self.dailyLogColumns)
        self.dailyLogs = self.dailyLogs.append(logAdditions, ignore_index=True)

        self.updateAssets(date)


    def placeSellOrders(self, listOfTickers, date, simulation=True):
        '''
        places a sell order for every ticker in list of tickers.
        Will sell ALL stocks owned of that ticker
        Date is the current date, in string format "YYYY-MM-DD".
        Setting simulation to False will actually execute the sell orders (not yet implimented)
        '''
        if (not simulation):
            pass  #actually execute sell orders

        
        action = "Sell"
        executedOrders = []
        completedBuySellCyles = []

        for ticker in listOfTickers:
            tickerData = database.getDataframe(ticker)
            openPrice = tickerData.loc[date, "Open"]
            quantity = self.stocksOwned[ticker][0]
            buyPrice = self.stocksOwned[ticker][1]
            buyDate = self.stocksOwned[ticker][2]
            

            tradeIncome = int(openPrice*quantity*100) - self.commision

            if (ticker in self.stocksOwned):
                #We own the stock
                self.balance += tradeIncome  #*100 since balance is in cents
                del self.stocksOwned[ticker]  #Remove stock from stocksOwned

                if (simulation):
                    self.updateAssets(date)
                else:
                    self.updateAssets()
                    
                totalAssets = float(self.balance + self.stockAssets)/100
                
                timeStamp = time.time()
                timeOfExecution = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S')

                executedOrders.append([date, ticker, quantity, float(openPrice), action, timeOfExecution, totalAssets, float(self.balance)/100, float(self.stockAssets)/100])

                tradeProfit = (tradeIncome - int(quantity*buyPrice*100) - self.commision)/100     #account for commision when you originally bought the stock
                completedBuySellCyles.append([ticker, buyDate, float(buyPrice), date, float(openPrice), quantity, self.commision/100, tradeProfit])

            else:
                raise ValueError("Ticker {} is not a currently owned stock".format(ticker))

        logAdditions = pd.DataFrame(executedOrders, columns=self.dailyLogColumns)
        self.dailyLogs = self.dailyLogs.append(logAdditions, ignore_index=True)

        tradeHistoryAdditions = pd.DataFrame(completedBuySellCyles, columns=self.tradeHistoryColumns)
        self.tradeHistory = self.tradeHistory.append(tradeHistoryAdditions, ignore_index=True)

        self.updateAssets(date)


    def saveHistory(self, SelectorName = "NAN"):
        '''
        Saves daily logs and trading history to seperate CSVs.
        Defualts to <Account Name>_<Logs||Trades>_<timeStamp>.csv
        '''
        timeSaved = str(time.time())

        filepath = self.savepath+"\\"+SelectorName+"_" + self.name + "_Log_" + timeSaved + ".csv"
        self.dailyLogs.to_csv(filepath)

        filepath = self.savepath+"\\"+SelectorName+"_" + self.name + "_TradeHistory_" + timeSaved + ".csv"
        self.tradeHistory.to_csv(filepath)


    def getHistory(self):
        '''
        Returns the trading history for this account as a dataframe
        '''
        return self.tradeHistory

    
    def getLogs(self):
        '''
        Returns the daily account logs as a dataframe
        '''
        return self.dailyLogs

#================END tradingAccount class=====================================
    
            

        
