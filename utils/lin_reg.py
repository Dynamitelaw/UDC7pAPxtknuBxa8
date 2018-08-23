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
from PandaDatabase import getDataframe , getTickerList,getSharedDates
from random import shuffle
from sklearn import linear_model

def compareStocks(stocks,date_range=["2013-01-10","2018-05-22"],show_plot=True,print_stats=True,dataField="Open"):
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


def multivar_lin_reg(X,y,verbose=False):
    '''
    Takes in an series of 'X' variables and a corresponding output 1d array
    of 'y' variables and creates a linear model of the two. Outputs the model
    and model statistics. Prints the model and statistics if verbose
    is set to True
    '''
    lin_model = linear_model.LinearRegression()
    model = lin_model.fit(X,y)

    if verbose:
        print("R-squared: {}".format(model.score(X,y)))
        print("Coefficients")
        print(model.coef_)
        print("Intercept:")
        print(model.intercept_)

    return model, model.score(X,y)


def compareMultipleStocks(stocks,print_stats=True,dataField="Open"):
    '''
    Compares and creates a correlation of the opening price of N different stocks
    over a date range specified by date_range. Plots the regression unless show_plot 
    is set to false by the user. 
    Returns the slope, intercept, r_value, p_value and std_err as a dictionary.
    '''
    
    #Checks stocks input is valid
    if len(stocks)<2:
        print("Invalid input for variable 'stocks'")
        return
    
    stock_prices = []
    dates = getSharedDates(stocks)
    dates.sort()
    for stock in stocks:
        df = getDataframe(stock,dateRange=[dates[0],dates[-1]],dataFields=[dataField],printError=False)
        try:
            if df == False:
                print("Data file for {} does not exist".format(stock))
            else:
                stock_prices.append(df["Open"].tolist())
        except:
            stock_prices.append(df["Open"].tolist())
            pass

    stock_length = len(stock_prices[0]) 
    # for stock in stock_prices:
    #     assert len(stock) == stock_length

    X = []
    y = []
    for i in range(stock_length):
        sample_x = []
        for j in range(len(stock_prices)):
            sample_x.append(stock_prices[j][i])
        X.append(X)
        y.append(stock_prices[0][i])

    print("Starting regression")
    model,score = multivar_lin_reg(X,y)
    
    if print_stats:
        for key in stats_dict.keys():
            print('R_squared: {}'.format(score))
    
    return model



###################################################################
#                     Unit Test Functions                         #
###################################################################

def test_compareStocks():
    passe = False
    while not passe:
        try:
            tickerList = getTickerList()
            shuffle(tickerList)
            compareStocks([tickerList[0],tickerList[1]])
            passe = True
        except:
            pass

def test_multivar_lin_reg():
    X = []
    y = []
    for i in range(100):
        for j in range(100):
            for k in range(100):
                X.append([i,j,k])
                y.append(i+2*j-3*k)
    
    model,score = multivar_lin_reg(X,y,verbose=True)
    print(model.predict([[10,20,30]]))
    print(score)

def test_compareMultipleStocks():
    passe = False
    while not passe:
        try:
            tickerList = getTickerList()
            shuffle(tickerList)
            val = compareMultipleStocks(tickerList[0:3])
            passe = True
        except Exception as e:
            print(e)
            pass

if __name__=="__main__":
    test_compareMultipleStocks()