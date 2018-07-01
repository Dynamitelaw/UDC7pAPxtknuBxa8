'''
Dynamitelaw

Standard interface for selecting stocks to buy and sell.
All selectors MUST be compatible with the methods included in this class.d
'''


class stockSelector():
    def __init__ (self, selectorName, databaseInterface, genericParams=[]):
        '''
        slecetorName must be a string denoting which selector type to use.
        genericParams is a list where you pass the arguments needed by the constructor
        of your specified selector.
        '''
        if (selectorName == "TestSelector"):
            from TestSelector import selector
            self.selector = selector(databaseInterface, genericParams)

        else:
            raise ValueError("No valid selector name passed.")

    
    def selectStocksToBuy(self, maxNumberOfStocks, date=False, customTickerList=False, genricParameters=[]):
        '''
        Selects which stocks to buy, and the proportion of funds to be allocated to each.
        maximumNumberOfStocks is the highest number of stocks the caller wants to select.
        Passing a date parameter will select stocks for the given date. Ommitting it will
        select stocks based on realtime data.
        Passing a customTickerList will only analyze tickers included in that list.

        Returns a list of in the following format: [ [Ticker1, RatioOfFundAllocation1], [Ticker2, RatioOfFundAllocation2], ... ] .
        All ratios will add up to 1.
        ''' 
        return self.selector.selectStocksToBuy(maxNumberOfStocks, date=date, customTickerList=customTickerList, genricParameters=genricParameters)

    
    def selectStocksToSell(self, listOfOwnedStocks, date=False, genricParameters=[]):
        '''
        Selects which stocks to sell.
        Passing a date parameter will select stocks for the given date. Ommitting it will
        select stocks based on realtime data.

        Returns a list of stocks to sell.
        ''' 
        return self.selector.selectStocksToSell(listOfOwnedStocks, date=date, genricParameters=genricParameters)