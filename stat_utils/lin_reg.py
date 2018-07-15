'''
ilPesce

A collection of methods that can be used for statistical regression of variables.
'''

from scipy.stats import linregress as lgr
from matplotlib import pyplot as plt
import numpy as np
import os.path
import sys
sys.path.append("./")
from PandaDatabase import getDataframe,getTickerList
from random import shuffle

def compareStocks(stocks,date_range=["2017-01-10","2018-05-22"],show_plot=True,print_stats=True,dataField="Open"):
    '''
    Compares and creates a correlation of the opening price of two different stocks
    over a date range specified by date_range. Plots the regression unless show_plot 
    is set to false by the user. 
    Returns the slope, intercept, r_value, p_value and std_err as a dictionary.
    '''
    
    #Checks stocks input is valid
    if len(stocks)!=2:
        print("Invalid input for variable 'stocks'")
        return
    
    stock_prices = []
    dates = []
    for stock in stocks:
        df = getDataframe(stock,dateRange=date_range,dataFields=[dataField],printError=False)
        try:
            if df == False:
                print("Data file for {} does not exist".format(stock))
                return False
        except:
            pass
        dates = df.index.tolist()
        stock_prices.append(df["Open"].tolist())
    
    assert len(stock_prices[0])==len(stock_prices[1])

    slope, intercept, r_value, p_value, std_err = lgr(stock_prices[0],stock_prices[1])
    stats_dict = {'slope':slope, 'intercept':intercept, 'r_value':r_value, 'p_value':p_value, 'std_err':std_err}
         
    if print_stats:
        for key in stats_dict.keys():
            print('{}: {}'.format(key,stats_dict[key]))
    
    if show_plot:
        plt.scatter(stock_prices[0],stock_prices[1],marker='x')
        xmin = np.min(stock_prices[0])
        xmax = np.max(stock_prices[0])
        plt.plot([xmin,xmax],[intercept+slope*xmin,intercept+slope*xmax])


        plt.show()

    return stats_dict



if __name__=="__main__":
    passe = False
    while not passe:
        try:
            tickerList = getTickerList()
            shuffle(tickerList)
            compareStocks([tickerList[0],tickerList[1]])
            passe = True
        except:
            pass