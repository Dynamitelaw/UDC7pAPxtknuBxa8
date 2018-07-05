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
    generalStats = results["General Stats"]
    statsVsTime = results["Stats vs Time"]
    tradeStats = results["Trade Stats"]

    textColor = (230/255,219/255,116/255)
    facecolor=(39/255,40/255,34/255)
    graphcolor = (49/255,50/255,44/255)

    fig, axes = plt.subplots(facecolor=facecolor,nrows=3, ncols=2)
    axes[0, 1].axis('off')
    axes[1, 1].axis('off')
    axes[2, 1].axis('off')

    assets = statsVsTime["TotalAssets"].plot(ax=axes[0, 0])
    assets.set_facecolor(graphcolor)
    assets.set_ylabel("Total Assets ($)", color=textColor)
    assetsDescription = generalStats["Start Date"] + " to " + generalStats["End Date"] + " | " + str(generalStats["Days Run"]) + " Days\n"
    assetsDescription += "Starting Assets: \$" + str(generalStats["Starting Assets"]) + " | Ending Assets: \$" + str(generalStats["Ending Assets"])
    axes[0,1].text(-0.14, 0.4, assetsDescription, color=textColor)

    statsVsTime.loc[:,"EstYearlyGrowthRate(Past30Days)"] *= 100
    growthRate = statsVsTime["EstYearlyGrowthRate(Past30Days)"].plot(ax=axes[1,0])
    growthRate.set_facecolor(graphcolor)
    growthRate.set_ylabel("Est Growth Rate (%)", color=textColor)
    growthRateDescription = "Estimated Yearly Growth Rate: " + str(int(generalStats["Yearly Growth Rate"] * 10000)/100.0) + "%"
    axes[1,1].text(-0.14, 0.4, growthRateDescription, color=textColor)

    tradeProfitHistogram = tradeStats["Percent Profit"].hist(ax=axes[2,0])
    tradeProfitHistogram.set_facecolor(graphcolor)
    tradeProfitHistogram.set_xlabel("Per Trade Profit (%)", color=textColor)
    tradeProfitHistogram.set_ylabel("Frequency", color=textColor)
    tradeProfitDescription = "Average Trades Per Day: " + str(int(generalStats["Average Trades Per Day"] * 100)/100.0) + "\n"
    tradeProfitDescription += "Average Profit Per Trade: " + str(int(generalStats["Average Trade %Profit"] * 100)/100.0) + "%\n"
    tradeProfitDescription += "Average Hold Length: " + str(int(generalStats["Average Hold Length"] * 100)/100.0) + " days\n"
    axes[2,1].text(-0.14, 0.2, tradeProfitDescription, color=textColor)
    
    plt.tight_layout()
    plt.show()