'''
IlPesce
Contains methods for generating training data for SVM's
'''

import pandas as pd
import numpy as np
from datetime import datetime
import os
from sklearn import svm,preprocessing

def XpercentGrowthNDaysAway(x=1,n=1,dir='Data/PcsData/'):
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
                df = df.sort_values('date',ascending=0)
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

if __name__=="__main__":
    XpercentGrowthNDaysAway()
    


