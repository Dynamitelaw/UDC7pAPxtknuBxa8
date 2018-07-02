'''
Dynamitelaw
'''

import utils
from TradingAccount import tradingAccount
from PandaDatabase import database
from TestSelector import TestSelector
import sys


def runSimulation(dateRange, startingBalance, selector, depositAmount=False, depositFrequency=False, comission=10, sampleSize=False, simulationName="SIM", customTickerList=False, genericParams=[]):
    '''
    Runs a single simulation. Saves results to a csv file.

    -Daterange must be a 2 element list, in the following format: [[<start date>], [<end date>]], date format = int YYYYMMDD.
    -depositFrequency is how often (in days) to deposit funds into your trading account.
    -selector is a string denoting which stock selection method to use.
    -Passing a customTickerList will run the simulation using only the tickers included in the list
    '''
    #Instaniate objects
    stockData = database()

    if (customTickerList):
        tickerList = customTickerList
    elif (sampleSize):
        tickerList = stockData.getTickerList(randomize=True, numberOfShuffles=2)[:sampleSize]
    else:
        tickerList = stockData.getTickerList()
    
    account = tradingAccount(stockData)
    account.depositFunds(startingBalance)
    account.setCommision(comission)

    startDate = dateRange[0]
    endDate = dateRange[1]

    #Progress bar header
    headerStartDate = utils.convertDate(startDate, outputFormat="String")
    headerEndDate = utils.convertDate(endDate, outputFormat="String")

    print ("Runing Simulation...")
    print ("Selector: " + selector.name)
    print ("Daterange: "+headerStartDate+" to "+headerEndDate)
    print ("")

    #Begin simulation
    for date in range(startDate, endDate+1, 1):
        if (utils.isWeekday(date)):
            #Selects which stocks to sell
            ownedStocks = account.getOwnedStocks()
            ownedTickers = []
            for ticker in ownedStocks:
                ownedTickers.append(ticker)

            stocksToSell = selector.selectStocksToSell(ownedTickers, date)
            #Sells stocks
            account.placeSellOrders(stocksToSell, date)

            #Selects which stocks to buy
            availibleFunds = account.getBalance()
            numberOfStocksToBuy = selector.numberOfStocksToBuy(availibleFunds)

            stocksToBuy = selector.selectStocksToBuy(numberOfStocksToBuy, date, tickerList)
            buyOrders = []
            for stock in stocksToBuy:
                ticker = stock[0]
                price = stockData.getDataframe(ticker, [date,date], ["Open"]).at[date, "Open"]
                quantity = int((stock[1]*availibleFunds) / price)

                buyOrders.append([ticker, quantity])

            #Buys stocks
            account.placeBuyOrders(buyOrders, date)

            #Progress bar
            percentage = float(int((float(date-startDate)*1000)/(endDate-startDate)))/10
            sys.stdout.write("\r")
            sys.stdout.write(str(percentage)+"%")
            sys.stdout.flush()
            
    #Save results        
    account.saveHistory()


if __name__ == '__main__':
    dateRange = [20150101,20150601]
    startingBalance = 100000
    data = database()
    selector = TestSelector(data)

    runSimulation(dateRange, startingBalance, selector, sampleSize=200)


