'''
Dynamitelaw

Plotter for simulation results
'''

import matplotlib.pyplot as plt 


def plotResults(results):
    '''
    Plots the results of a simulation run. results must be a dictionary
    in the following format:
        {
            "General Stats":
            {
                "Start Date":str, "End Date":str, "Days Run":int, "Yearly Growth Rate":float,
                "Average Trades Per Day":float, "Average Trade %Profit":float, "Average Hold Length":float
            },
            "Stats vs Time":dataFrame,
            "Trade Stats":dataFrame
        }
    '''
    #Extract Stats
    generalStats = results["General Stats"]
    statsVsTime = results["Stats vs Time"]
    tradeStats = results["Trade Stats"]

    #RGB Color Values
    textColor = (230/255,219/255,116/255) #Sublime Text Yello
    facecolor=(39/255,40/255,34/255) #Sublime Dark Grey
    graphcolor = (49/255,50/255,44/255) #Slightly lighter grey
    axisColor = (200/255,200/255,200/255) #Mostly White

    #Set up Subplots
    fig, axes = plt.subplots(facecolor=facecolor,nrows=2, ncols=2)
    axes[0, 1].axis('off')
    axes[1, 1].axis('off')
    #axes[2, 1].axis('off') (76/255,255/255,0/255)

    #Assets over Time
    if (generalStats["Ending Assets"] > generalStats["Starting Assets"]):
        assetLineColor = (76/255,255/255,0/255) #Green
    else:
        assetLineColor = (255/255,20/255,0/255) #Red

    assets = statsVsTime["TotalAssets"].plot(ax=axes[0, 0], color=assetLineColor)
    assets.set_facecolor(graphcolor)
    assets.spines['bottom'].set_color(axisColor)
    assets.spines['top'].set_color(axisColor) 
    assets.spines['right'].set_color(axisColor)
    assets.spines['left'].set_color(axisColor)
    assets.tick_params(axis='x', colors=axisColor)
    assets.tick_params(axis='y', colors=axisColor)
    assets.yaxis.label.set_color(axisColor)
    assets.xaxis.label.set_color(axisColor)
    assets.set_ylabel("Total Assets ($)", color=textColor)

    assetsDescription = generalStats["Start Date"] + " to " + generalStats["End Date"] + " | " + str(generalStats["Days Run"]) + " Days\n"
    assetsDescription += "Starting Assets: \$" + str(generalStats["Starting Assets"]) + " | Ending Assets: \$" + str(generalStats["Ending Assets"]) + "\n"
    assetsDescription += "Estimated Yearly Growth Rate: " + str(int(generalStats["Yearly Growth Rate"] * 10000)/100.0) + "%"
    axes[0,1].text(-0.14, 0.4, assetsDescription, color=textColor)

    '''
    #Growth Rate over Time
    statsVsTime.loc[:,"EstYearlyGrowthRate(Past30Days)"] *= 100
    growthRate = statsVsTime["EstYearlyGrowthRate(Past30Days)"].plot(ax=axes[1,0])
    growthRate.set_facecolor(graphcolor)
    growthRate.set_ylabel("Est Growth Rate (%)", color=textColor)
    growthRateDescription = "Estimated Yearly Growth Rate: " + str(int(generalStats["Yearly Growth Rate"] * 10000)/100.0) + "%"
    axes[1,1].text(-0.14, 0.4, growthRateDescription, color=textColor)
    '''

    #Trade Histogram
    maxProfit = tradeStats["Percent Profit"].max()
    minProfit = tradeStats["Percent Profit"].min()
    numberOfBins = 20
    numberPositiveBins = int(numberOfBins * (maxProfit / (maxProfit + abs(minProfit))))
    numberNegativeBins = numberOfBins - numberPositiveBins

    binsList = []
    
    tradeProfitHistogram = tradeStats["Percent Profit"].hist(ax=axes[1,0])
    tradeProfitHistogram.set_facecolor(graphcolor)
    tradeProfitHistogram.spines['bottom'].set_color(axisColor)
    tradeProfitHistogram.spines['top'].set_color(axisColor) 
    tradeProfitHistogram.spines['right'].set_color(axisColor)
    tradeProfitHistogram.spines['left'].set_color(axisColor)
    tradeProfitHistogram.tick_params(axis='x', colors=axisColor)
    tradeProfitHistogram.tick_params(axis='y', colors=axisColor)
    tradeProfitHistogram.yaxis.label.set_color(axisColor)
    tradeProfitHistogram.xaxis.label.set_color(axisColor)
    tradeProfitHistogram.set_xlabel("Per Trade Profit (%)", color=textColor)
    tradeProfitHistogram.set_ylabel("Frequency", color=textColor)
    tradeProfitDescription = "Average Trades Per Day: " + str(int(generalStats["Average Trades Per Day"] * 100)/100.0) + "\n"
    tradeProfitDescription += "Average Profit Per Trade: " + str(int(generalStats["Average Trade %Profit"] * 100)/100.0) + "%\n"
    tradeProfitDescription += "Average Hold Length: " + str(int(generalStats["Average Hold Length"] * 100)/100.0) + " days\n"
    axes[1,1].text(-0.14, 0.2, tradeProfitDescription, color=textColor)
    
    #Show Plot
    plt.tight_layout()  #NOTE https://matplotlib.org/users/tight_layout_guide.html
    plt.show()