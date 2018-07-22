'''
IlPesce
Contains methods for generating training data for SVM's
'''

import pandas as pd
import numpy as np
from datetime import datetime
import os
from sklearn import svm,preprocessing
import sys
sys.path.append("./")
from PandaDatabase import getDataframe, getTickerList

def XpercentGrowthNDaysAway(x=1,n=3,dir='Data/PcsData/'):
    ''' Iterates through all of the .csv data files in the dir directory and
    creates new data files in /Data/SVM/{x}PercentGrowth{N}DaysAway with an
    additional column "Result" with 0 if the percent change after N days from
    a particular date calculated as  [(N Days "Close")-(0 Days "Open")]/(0 Days "Open")
    is less than x percent and a 1 if greater than x percent. The results ARE NOT
    already normalized for training
    '''
    
    #Ensuring that our data files have a home
    os.makedirs("Data/SVM/{}PercentGrowth{}DaysAway".format(x,n),exist_ok=True)
    
    #Checking to see if we have data
    if not os.path.isdir(dir):
        print("Invalid path to ticker files")
        return
    
    #Crawls through all files/Directories in dir and creates training files
    for root,dirs,files in os.walk(dir):
        for f in files:
            try:
                df = pd.DataFrame.from_csv(os.path.join(dir,f))
                df.index.name = 'date'
                df = df.sort_values('date',ascending=1)
                date = df.index.tolist()
                results = []
                p_change = []
                for i in range(0,len(date)-n-1):
                    open_day_zero = df.at[date[i+1],"Open"]
                    close_day_n = df.at[date[i+1+n],"Close"]
                    percent_change = (close_day_n-open_day_zero)/(open_day_zero)
                    p_change.append(percent_change)
                    if percent_change>float(x)/100.0:
                        results.append(1)
                    else:
                        results.append(0)
                df = df.drop(date[len(results):])
                df = df.drop(columns=["Optimal Dates","Desired Level 1 Out Buy","Desired Level 1 Out Sell","Profit Speed"])
                df["Result"] = results
                df["Percent Results"] = p_change
                df.to_csv(os.path.join("Data/SVM/{}PercentGrowth{}DaysAway".format(x,n),f))
            except:
                pass


def create_5day_2day_training_data(param="Profit Speed", dateRange=["2000-01-01","2015-01-01"]):
    '''
    Creates training data to draw surface for 5dayslope vs 2dayslope vs parameter
    '''

    #Ensuring that our data files have a home
    os.makedirs("Data/SVM/5day_vs_2day_vs_{}".format(param),exist_ok=True)
    
    tickerList = getTickerList()

    for ticker in tickerList:
        df = getDataframe(ticker,dateRange=dateRange,dataFields=["Open","2 Day Slope", "5 Day Slope", param])
        if not(type(df) is bool):
            df["2 Day Slope"] = df["2 Day Slope"]/df["Open"]
            df["5 Day Slope"] = df["5 Day Slope"]/df["Open"]
            df = df.drop(columns=["Open"])
            param_array = df[param].values.tolist()
            class_array = []
            for val in param_array:
                if val>0:
                    class_array.append(1)
                else:
                    class_array.append(0)
            df["Result"] = class_array
            df.to_csv(os.path.join("Data/SVM/5day_vs_2day_vs_{}".format(param),ticker+".csv"))
    
    
    


if __name__=="__main__":
    create_5day_2day_training_data()
    


