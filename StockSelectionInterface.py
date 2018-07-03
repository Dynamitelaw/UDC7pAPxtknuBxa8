'''
Dynamitelaw

Standard interface for selecting stocks to buy and sell.
All selectors MUST be compatible with the methods included in this class.
'''
from abc import ABC,abstractmethod


class stockSelector(ABC):
    def __init__ (self, selectorName, genericParams=[]):
        '''
        selecetorName must be a string denoting which selector type to use.
        genericParams is a list where you pass the arguments needed by the constructor
        of your specified selector.
        '''
        self.minimumPurchase = 2500 

    @abstractmethod
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

    @abstractmethod
    def selectStocksToSell(self, listOfOwnedStocks, date=False, genricParameters=[]):
        '''
        Selects which stocks to sell.
        Passing a date parameter will select stocks for the given date. Ommitting it will
        select stocks based on realtime data.

        Returns a list of stocks to sell.
        ''' 

    def numberOfStocksToBuy(self, funds):
        '''
        Returns how many stocks you should buy based on your availible funds.
        '''
        return (int(funds/self.minimumPurchase))