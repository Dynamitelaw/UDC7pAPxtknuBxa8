'''
Dynamitelaw

Contains functions to run simulations on historical data,
and to analyze the results of each simulation.
'''

import utils
from TradingAccount import tradingAccount
import PandaDatabase as database
from TestSelector import TestSelector
import sys
import datetime
import pandas as pd


#=============================================================================
#       Historical Simulator
#=============================================================================

def runSimulation(account, dateRange, startingDeposit, selector, sampleSize=False, customTickerList=False, preloadToMemory=False, depositAmount=False, depositFrequency=False, comission=10):
    '''
    Runs a single simulation. Saves results to a csv file.

    -Daterange must be a 2 element list, in the following format: [[<start date>], [<end date>]], date format = string "YYYY-MM-DD".
    -depositFrequency is how often (in days) to deposit funds into your trading account.
    -selector is a StockSelectionInterface object.
    -Passing a customTickerList will run the simulation using only the tickers included in the list.
    '''
    #Check for valid parameters
    if ((depositFrequency) and (not depositAmount)):
        raise ValueError("Deposit frequency set without deposit amount.")
    if ((depositAmount) and (not depositFrequency)):
        raise ValueError("Deposit amount set without deposit frequency.")

    #Instaniate objects
    print("\nGetting tickers...")
    if (customTickerList):
        tickerList = customTickerList
    elif (sampleSize):
        tickerList = database.getTickerList(randomize=True, numberOfShuffles=2)[:sampleSize]
    else:
        tickerList = database.getTickerList()

    if (preloadToMemory):
        print("Preloading stock data to memory...")
        database.loadDatabaseToMemory(tickerList)

    #Set starting balance and comission
    account.depositFunds(startingDeposit)
    account.setCommision(comission)

    #Extract daterange
    startDate = dateRange[0]
    endDate = dateRange[1]

    #Progress bar header
    print ("\nRuning Simulation...\n")
    print ("Selector: " + selector.name)
    print ("Daterange: "+startDate+" to "+endDate)
    print ("-------------------------------------------\n")
    sys.stdout.write("\r")
    sys.stdout.write("0.0%")
    sys.stdout.flush()

    daysSinceLastDeposit = 0

    #Begin simulation
    for date in utils.daterange(startDate, endDate):
        #Check if market is open
        if (utils.isWeekday(date)):
            #Selects which stocks to sell
            ownedStocks = account.getOwnedStocks()
            ownedTickers = []
            for ticker in ownedStocks:
                ownedTickers.append(ticker)

            stocksToSell = selector.selectStocksToSell(ownedTickers, date=date)
            #Sells stocks
            account.placeSellOrders(stocksToSell, date)

            #Selects which stocks to buy
            availibleFunds = account.getBalance()
            numberOfStocksToBuy = selector.numberOfStocksToBuy(availibleFunds)

            stocksToBuy = selector.selectStocksToBuy(numberOfStocksToBuy, date=date, customTickerList=tickerList)
            
            buyOrders = []

            for stock in stocksToBuy:
                ticker = stock[0]
                price = database.getDataframe(ticker, [date,date], ["Open"]).loc[date, "Open"]
                quantity = int((stock[1]*(availibleFunds-(len(stocksToBuy)*comission))) / price)

                buyOrders.append([ticker, quantity])

            #Buys stocks
            account.placeBuyOrders(buyOrders, date)

        if (depositFrequency):
            daysSinceLastDeposit += 1
            if (daysSinceLastDeposit == depositFrequency):
                account.depositFunds(depositAmount)
                daysSinceLastDeposit = 0

        #Progress bar
        completed = utils.getDayDifference(startDate, date)
        totalToDo = utils.getDayDifference(startDate, endDate)
        percentage = int(float(completed*1000)/(totalToDo-1))/10.0
        sys.stdout.write("\r")
        sys.stdout.write(str(percentage)+"%")
        sys.stdout.flush()
            
    #Save results        
    account.saveHistory(selector.name)

#====================END Historical Simulator=================================




#=============================================================================
#       Simulation Data Analysis
#=============================================================================

def analyzeData(tradingHistory, dailyLogs):
    '''
    Analyzes the trading history and daily logs of the passed account. 
    Outputs results as a dictionary, in the following format:
        {
            "General Stats":
            {
                "Start Date":str, "End Date":str, "Days Run":int, "Yearly Growth Rate":float,
                "Average Trades Per Day":float, "Average Trade Profit":float, "Average Hold Length":float
            },
            "Stats vs Time":dataFrame,
            "Trade Stats":dataFrame
        }

    -tradingHistory is the dataframe containing the trading history of an account
    -dailyLogs is a dataframe containing the logs of an account
    '''
    #Get overall statistics
    startDate = dailyLogs.at[0, "Date"]
    endDate = dailyLogs.at[len(dailyLogs)-1, "Date"]
    daysRun = utils.getDayDifference(startDate, endDate)
    
    startingAssets = dailyLogs.at[0, "TotalAssets"]
    endingAssets = dailyLogs.at[len(dailyLogs)-1, "TotalAssets"]

    estimatedYearlyGrowth = utils.estimateYearlyGrowth(startingAssets, endingAssets, daysRun)  #solved for r in compound interest formula, assuming compounding monthly
    
    averageTradesPerDay = len(dailyLogs)/daysRun

    #Get statistics over time
    columns = ["Date", "TotalAssets", "Buys", "Sells", "AssetsInvested", "EstYearlyGrowthRate(Past30Days)"]
    statsOverTime = pd.DataFrame(columns=columns)
    statsOverTime["Date"] = pd.date_range(start=startDate, end=endDate)

    ########## Daily Log Analysis ##########
    #Iterate over daily logs to populate statistics
    logIndex = 0
    for rowIndex in range(0, daysRun+1, 1):
        currentStatDate = str(statsOverTime.at[rowIndex, "Date"])[:10]

        totalBuys = 0
        totalSells = 0

        while (True):
            row = dailyLogs.loc[logIndex]
            
            if (str(row["Date"]) == currentStatDate):  #if still on the same date
                if (row["Action"] == "Buy"):
                    totalBuys += 1
                else:
                    totalSells += 1
                
                logIndex += 1  #go to next log entry
                if (logIndex == len(dailyLogs)):
                    #We're at the end of the log. Fill in final row of stats
                    row = dailyLogs.loc[logIndex-1]  #We hit a transition b/w consecutive dates. Go back one row in logs

                    assets = float(row["TotalAssets"])  #assets at the end of day
                    statsOverTime.at[rowIndex, "TotalAssets"] = assets
                    
                    #Estimate yearly growth rate based on past 30 days
                    if (rowIndex == 0):
                        statsOverTime.at[rowIndex, "EstYearlyGrowthRate(Past30Days)"] = 1
                    else:
                        pastRowIndex = utils.floor(rowIndex-30, floor=0)
                        estRate = utils.estimateYearlyGrowth(statsOverTime.at[pastRowIndex, "TotalAssets"], assets, rowIndex-pastRowIndex)
                        statsOverTime.at[rowIndex, "EstYearlyGrowthRate(Past30Days)"] = estRate

                    #Total Buys and Sells
                    statsOverTime.at[rowIndex, "Buys"] = totalBuys
                    statsOverTime.at[rowIndex, "Sells"] = totalSells

                    #Percent of assets invested
                    statsOverTime.at[rowIndex, "AssetsInvested"] = float(row["StockAssets"]) / assets

                    #Exit loop
                    break

            else:
                if (rowIndex+1<daysRun+1):
                    nextStatRowDate = str(statsOverTime.at[rowIndex+1, "Date"])[:10]
                else:
                    break

                if (utils.compareDates(nextStatRowDate, row["Date"]) == -1):
                    #Gap in the daily logs: use previous date to fill
                    statsOverTime.at[rowIndex, "TotalAssets"] = statsOverTime.at[rowIndex-1, "TotalAssets"]
                    statsOverTime.at[rowIndex, "Buys"] = 0
                    statsOverTime.at[rowIndex, "Sells"] = 0
                    statsOverTime.at[rowIndex, "AssetsInvested"] = statsOverTime.at[rowIndex-1, "AssetsInvested"]
                    statsOverTime.at[rowIndex, "EstYearlyGrowthRate(Past30Days)"] = statsOverTime.at[rowIndex-1, "EstYearlyGrowthRate(Past30Days)"]

                    #Move on to next day in stats
                    break

                else:
                    row = dailyLogs.loc[logIndex-1]  #We hit a transition b/w consecutive dates. Go back one row in logs

                    assets = float(row["TotalAssets"])  #assets at the end of day
                    statsOverTime.at[rowIndex, "TotalAssets"] = assets
                    
                    #Estimate yearly growth rate based on past 30 days
                    if (rowIndex == 0):
                        statsOverTime.at[rowIndex, "EstYearlyGrowthRate(Past30Days)"] = 1
                    else:
                        pastRowIndex = utils.floor(rowIndex-30, floor=0)
                        estRate = utils.estimateYearlyGrowth(statsOverTime.at[pastRowIndex, "TotalAssets"], assets, rowIndex-pastRowIndex)
                        statsOverTime.at[rowIndex, "EstYearlyGrowthRate(Past30Days)"] = estRate

                    #Total Buys and Sells
                    statsOverTime.at[rowIndex, "Buys"] = totalBuys
                    statsOverTime.at[rowIndex, "Sells"] = totalSells

                    #Percent of assets invested
                    statsOverTime.at[rowIndex, "AssetsInvested"] = float(row["StockAssets"]) / assets

                    #Move on to next day in stats
                    break


    ########## Trading History Analysis ##########
    tradeColumns = ["Ticker", "Percent Profit", "Hold Length"]
    tradeStats = pd.DataFrame(columns=tradeColumns)

    tradeStats["Ticker"] = tradingHistory["Ticker"]
    tradeStats["Percent Profit"] = ((tradingHistory["Sell Price"] - tradingHistory["Buy Price"]) / (tradingHistory["Buy Price"]))*100
    tradeStats["Hold Length"] = tradingHistory.apply(lambda row: utils.getDayDifference(row["Date Bought"], row["Date Sold"]), axis=1)  #https://engineering.upside.com/a-beginners-guide-to-optimizing-pandas-code-for-speed-c09ef2c6a4d6

    #More general stats
    averagePercentProfit = tradeStats["Percent Profit"].mean()
    averageHoldLength = tradeStats["Hold Length"].mean()
    
    #Gather return values
    generalResults = {}
    generalResults["Start Date"] = startDate
    generalResults["End Date"] = endDate
    generalResults["Days Run"] = daysRun
    generalResults["Yearly Growth Rate"] =  estimatedYearlyGrowth
    generalResults["Average Trades Per Day"] = averageTradesPerDay
    generalResults["Average Trade %Profit"] = averagePercentProfit
    generalResults["Average Hold Length"] =  averageHoldLength

    returnDict = {}
    returnDict["General Stats"] = generalResults
    returnDict["Stats vs Time"] = statsOverTime
    returnDict["Trade Stats"] = tradeStats

    return returnDict

#====================END Simulation Data Analysis=============================




#=============================================================================
#       Main Entry Point
#=============================================================================
if __name__ == '__main__':
    tradingHistoryPath = "Data\AcountData\TESTACCOUNT\TestSelector_TESTACCOUNT_TradeHistory_1530651828.6322038.csv"
    dailyLogPath = "Data\AcountData\TESTACCOUNT\TestSelector_TESTACCOUNT_Log_1530651828.627204.csv"

    tradingHistory = pd.DataFrame.from_csv(tradingHistoryPath)
    dailyLogs = pd.DataFrame.from_csv(dailyLogPath)

    #print(tradingHistory)
    #print("----------------")
    #print(tradingHistory)
    #print(len(tradingHistory))

    stats = analyzeData(tradingHistory, dailyLogs)
    print (stats)
    '''
    for i in range(3):
        dateRange = ["2017-01-03","2017-03-03"]
        startingBalance = 10000
        selector = TestSelector()
        account = tradingAccount()

        runSimulation(account, dateRange, startingBalance, selector, sampleSize=800, preloadToMemory=True)
        
    utils.emitAsciiBell()
    '''


