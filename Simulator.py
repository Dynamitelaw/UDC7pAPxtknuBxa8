'''
Dynamitelaw

Contains functions to run simulations on historical data,
and to analyze the results of each simulation.
'''

#External Modules
import sys
import os
import time
from shutil import copyfile
from multiprocessing import Pool
import datetime
import pandas as pd

#Custom Modules
import SystemPathImports
import utils
from utils import Silence
from TradingAccount import tradingAccount
import PandaDatabase as database
from TestSelector import TestSelector
import ResultsPlotter as rplotter
from SVMSelector import SVMSelector
from MehSelector import MehSelector


#=============================================================================
#       Historical Simulator
#=============================================================================
def runSimulation(account, dateRange, startingDeposit, selector, sampleSize=False, customTickerList=False, preloadToMemory=False, depositAmount=False, depositFrequency=False, comission=10, PrintToTerminal=True):
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
    if (PrintToTerminal):
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
    if (PrintToTerminal):
        print ("\nRuning Simulation...\n")
        print ("Selector: " + selector.getName())  #NOTE Don't forget to set your self.name property in you selector constructor
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
                if quantity>0:
                    buyOrders.append([ticker, quantity])

            #Buys stocks
            account.placeBuyOrders(buyOrders, date)

        if (depositFrequency):
            daysSinceLastDeposit += 1
            if (daysSinceLastDeposit == depositFrequency):
                account.depositFunds(depositAmount)
                daysSinceLastDeposit = 0

        #Progress bar
        if (PrintToTerminal):
            completed = utils.getDayDifference(startDate, date)
            totalToDo = utils.getDayDifference(startDate, endDate)
            percentage = int(float(completed*1000)/(totalToDo-1))/10.0
            sys.stdout.write("\r")
            sys.stdout.write(str(percentage)+"%")
            sys.stdout.flush()

    if (PrintToTerminal):
        print("\n")    
    #Save logs        
    account.saveHistory(selector.getName())

    #====================END Historical Simulator=============================


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
                "Start Date":str, "End Date":str, "Days Run":int, "Starting Assets":float, "Ending Assets":float, 
                Yearly Growth Rate":float, "Average Trades Per Day":float, "Average Trade %Profit":float, "Average Hold Length":float
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
                elif (row["Action"] == "Buy"):
                    totalSells += 1
                elif (logIndex>0):  
                    if ((row["Action"] == "CHECKPOINT") and (str(dailyLogs.loc[logIndex-1]["Date"]) != str(row["Date"]))):  #No trades were conducted on that day, but we still need to update our assets
                        assets = float(row["TotalAssets"])
                        statsOverTime.at[rowIndex, "TotalAssets"] = assets
                        statsOverTime.at[rowIndex, "Buys"] = 0
                        statsOverTime.at[rowIndex, "Sells"] = 0
                        statsOverTime.at[rowIndex, "AssetsInvested"] = float(row["StockAssets"])/ assets
                        statsOverTime.at[rowIndex, "EstYearlyGrowthRate(Past30Days)"] = statsOverTime.at[rowIndex-1, "EstYearlyGrowthRate(Past30Days)"]
                        pastRowIndex = utils.floor(rowIndex-30, floor=0)
                        estRate = utils.estimateYearlyGrowth(statsOverTime.at[pastRowIndex, "TotalAssets"], assets, rowIndex-pastRowIndex)
                        statsOverTime.at[rowIndex, "EstYearlyGrowthRate(Past30Days)"] = estRate
                        logIndex +=1 
                        break
                
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

                if (utils.compareDates(nextStatRowDate, row["Date"]) == -1) and (currentStatDate != str(dailyLogs.loc[logIndex-1]["Date"])):
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
                        if (rowIndex < 20):
                            statsOverTime.at[rowIndex, "EstYearlyGrowthRate(Past30Days)"] = 1
                        else:
                            statsOverTime.at[rowIndex, "EstYearlyGrowthRate(Past30Days)"] = estRate

                    #Total Buys and Sells
                    statsOverTime.at[rowIndex, "Buys"] = totalBuys
                    statsOverTime.at[rowIndex, "Sells"] = totalSells

                    #Percent of assets invested
                    statsOverTime.at[rowIndex, "AssetsInvested"] = float(row["StockAssets"]) / assets

                    #Move on to next day in stats
                    break

    statsOverTime["Date"] = pd.to_datetime(statsOverTime["Date"], format='%Y-%m-%d')
    statsOverTime.set_index("Date", inplace=True)


    ########## Trading History Analysis ##########
    tradeColumns = ["Ticker", "Date Bought", "Buy Price", "Date Sold", "Sell Price", "Quantity", "Buy In Amount", "Commission", "Trade Profit", "Percent Profit", "Hold Length"]
    tradeStats = pd.DataFrame(columns=tradeColumns)

    tradeStats[["Ticker", "Date Bought", "Buy Price", "Date Sold", "Sell Price", "Quantity", "Commission", "Trade Profit"]] = tradingHistory[["Ticker", "Date Bought", "Buy Price", "Date Sold", "Sell Price", "Quantity", "Commission", "Trade Profit"]]
    tradeStats["Percent Profit"] = ((tradingHistory["Sell Price"] - tradingHistory["Buy Price"]) / (tradingHistory["Buy Price"]))*100  #NOTE Excludes commission
    tradeStats["Hold Length"] = tradingHistory.apply(lambda row: utils.getDayDifference(row["Date Bought"], row["Date Sold"]), axis=1)  #https://engineering.upside.com/a-beginners-guide-to-optimizing-pandas-code-for-speed-c09ef2c6a4d6
    tradeStats["Buy In Amount"] = tradingHistory["Buy Price"] * tradingHistory["Quantity"]

    #More general stats
    averagePercentProfit = tradeStats["Percent Profit"].mean()
    averageHoldLength = tradeStats["Hold Length"].mean()
    
    #Gather return values
    generalResults = {}
    generalResults["Start Date"] = startDate
    generalResults["End Date"] = endDate
    generalResults["Days Run"] = daysRun
    generalResults["Starting Assets"] = startingAssets
    generalResults["Ending Assets"] = endingAssets
    generalResults["Yearly Growth Rate"] =  estimatedYearlyGrowth
    generalResults["Average Trades Per Day"] = averageTradesPerDay
    generalResults["Average Trade %Profit"] = averagePercentProfit
    generalResults["Average Hold Length"] =  averageHoldLength

    returnDict = {}
    returnDict["General Stats"] = generalResults
    returnDict["Stats vs Time"] = statsOverTime
    returnDict["Trade Stats"] = tradeStats

    return returnDict

    #====================END Simulation Data Analysis=========================


#=============================================================================
#       Save Simulation Results
#=============================================================================
def saveResults(results, SelectorName, TimeStamp):
    '''
    Saves the analyzed simulation results to a directory in Data/SimulationData.
    '''
    savePath = "Data\SimulationData\\"
    saveDirectory = SelectorName + "_" + TimeStamp

    savePath += saveDirectory

    if not os.path.exists(savePath):
            os.makedirs(savePath)

    #Save general stats
    generalStatsFilename = "GeneralStats.json"
    filePath = savePath + "\\" + generalStatsFilename
    file = open(filePath, 'w')
    file.write(str(results["General Stats"]))
    file.close

    #Save stats vs time
    statsVsTimeFilename = "StatsOverTime.csv"
    filePath = savePath + "\\" + statsVsTimeFilename
    results["Stats vs Time"].to_csv(filePath)

    #Save trade stats
    tradingStatsFilename = "TradingStats.csv"
    filePath = savePath + "\\" + tradingStatsFilename
    results["Trade Stats"].to_csv(filePath)

    #Copy logs from AccountData to the simulation directory
    logPath = "Data\AccountData\TESTACCOUNT\\" + SelectorName + "_TESTACCOUNT_Log_" + TimeStamp + ".csv"
    try:
        copyfile(logPath, savePath +"\\"+ "Log.csv")
    except Exception as e:
        print("Unable to copy log file")
        print(e)

    #====================END saveResults=============================


#=============================================================================
#       Run Multiple Simulations
#=============================================================================
def runMultiSim(numberOfSimulations, selectorName, dateRange, startingDeposit, sampleSize=False, customTickerList=False, preloadToMemory=False, depositAmount=False, depositFrequency=False, comission=10, PrintToTerminal=True):
    '''
    Runs multiple simulations and analyzes the results as a set.

    -Daterange must be a 2 element list, in the following format: [[<start date>], [<end date>]], date format = string "YYYY-MM-DD".
    '''

    inputArguments = []
    for i in range(numberOfSimulations):
        arguments = dateRange, startingDeposit, selectorName, sampleSize, customTickerList, preloadToMemory, depositAmount, depositFrequency, comission, PrintToTerminal
        inputArguments.append(arguments)

    results = []
    i = 1
    for arguments in inputArguments:
        if (PrintToTerminal):
            print("##############################################")
            print("Simulation " + str(i) + "/" + str(numberOfSimulations))
            print("##############################################")
            i += 1

        result = simulationWrapper(*arguments)
        results.append(result)

    if (PrintToTerminal):
        print("Your patience has been rewarded. I bestow upon you the results of your CPU's tireless efforts")

    return results


def simulationWrapper(dateRange, startingDeposit, selectorName, sampleSize, customTickerList, preloadToMemory, depositAmount, depositFrequency, comission, PrintToTerminal):
    '''
    Wrapper for the runSimulation function to support analyzing multiple simulations
    '''
    #Instantiate selector
    if (selectorName == "TestSelector"):
        selector = TestSelector()
    elif (selectorName == "SVMSelector"):
        selector = SVMSelector()
    elif (selectorName == "MehSelector"):
        selector = MehSelector()
    
    else:
        raise ValueError ("{} is not a valid selector name".format(selectorName))

    #Instantiate account
    account = tradingAccount()

    #Run simulation
    runSimulation(account, dateRange, startingDeposit, selector, sampleSize=sampleSize, customTickerList=customTickerList, preloadToMemory=preloadToMemory, depositAmount=depositAmount, depositFrequency=depositFrequency, comission=comission, PrintToTerminal=PrintToTerminal)
    results = analyzeData(account.getHistory(), account.getLogs())
    saveResults(results, selector.getName(), account.timeSaved)

    return results

    #====================END Run Multiple Simulations=============================


#=============================================================================
#       Main Entry Point
#=============================================================================
if __name__ == '__main__':
    
    # numberOfSimulations = 2
    # selectorName = "MehSelector"
    dateRange = ["2017-01-03","2017-02-07"]
    startingBalance = 100000

    # results = runMultiSim(numberOfSimulations, selectorName, dateRange, startingBalance, sampleSize=1000, preloadToMemory=True,  comission=0)
    # utils.emitAsciiBell()
    # rplotter.plotMultipleResults(results)
    
    
    selector = MehSelector()  #NOTE Just put your selector here Cole
    account = tradingAccount()

    startTime = time.time()
    runSimulation(account, dateRange, startingBalance, selector, sampleSize=4000, preloadToMemory=True, PrintToTerminal=True,comission=0)
    results = analyzeData(account.getHistory(), account.getLogs())
    saveResults(results, selector.getName(), account.timeSaved)
    endTime = time.time()
    print ("Total simulation time: " + time.strftime('%H:%M:%S', time.gmtime(endTime - startTime)))

    utils.emitAsciiBell()

    rplotter.plotResults(results)
  

    
    # tradingHistoryPath1 = "Data\AccountData\TESTACCOUNT\TestSelector_TESTACCOUNT_TradeHistory_1531086427.924168.csv"
    # dailyLogPath1 = "Data\AccountData\TESTACCOUNT\TestSelector_TESTACCOUNT_Log_1531086427.924168.csv"
    # tradingHistoryPath2 = "Data\AccountData\TESTACCOUNT\TestSelector_TESTACCOUNT_TradeHistory_1531086026.0894861.csv"
    # dailyLogPath2 = "Data\AccountData\TESTACCOUNT\TestSelector_TESTACCOUNT_Log_1531086026.0894861.csv"

    # tradingHistory1 = pd.DataFrame.from_csv(tradingHistoryPath1)
    # dailyLogs1 = pd.DataFrame.from_csv(dailyLogPath1)
    # tradingHistory2 = pd.DataFrame.from_csv(tradingHistoryPath2)
    # dailyLogs2 = pd.DataFrame.from_csv(dailyLogPath2)

    # results1 = analyzeData(tradingHistory1, dailyLogs1)
    # results2 = analyzeData(tradingHistory2, dailyLogs2)

    # rplotter.plotMultipleResults([results1, results2])
    
    


