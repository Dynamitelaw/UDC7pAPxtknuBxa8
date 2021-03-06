'''
Dynamitelaw
Processes raw stock data for neural network intput. 
Adds 2 day slope, 5 day slope, 30 day standard deviation, optimal buy and sell dates, and desired network outputs.
'''

#External Imports
import numpy as np
import io
import os
import multiprocessing
from multiprocessing import Process
from multiprocessing import Pool
import sys
import time
import pandas as pd
import tqdm

#Custom Imports
import SystemPathImports
import utils



def optimalbuy(array):
    '''
    Makes an array marking the optimal buy and sell dates, as well as desired outputs for Network Level 1. 
    1 for buy, -1 for sell, 0 OTW
    '''
    
    state = 0       #state = 0 if no stock is owned
    k = int(array.shape[0])
    opt = np.zeros((k,1))
    
    for i in range(k-8,6,-1):       #edits array opt to show optimal buying and selling times
        
        if state == 0:
            if array[i,0] < array[i-1,0] and array[i,0] < array[i-7,0]:
                idx = np.argmin(array[i-7:i+7,0])       #index of local minimum price
                opt [idx+i-7] = 1
                state = 1
        
        if state == 1:
            if array[i,0] > array[i-1,0] and array[i,0] > array[i-3,0]:
                idx = np.argmax(array[i-3:i+3,0])       #index of local maximum price
                opt [idx+i-3] = -1
                state = 0

    bought = 0
    for i in range(k-1,0,-1):
        #corrects for double buys
        if opt[i] == 1 and bought == 1:
            opt[i] = 0
        if opt[i] == 1 and bought == 0:
            bought = 1      
        #corrects for double sells
        if opt[i] == -1 and bought == 0:
            opt[i] = 0
        if opt[i] == -1 and bought == 1:
            bought = 0
        
                
    desire = np.zeros((k,2))
    
    output = np.hstack((opt,desire))
    
    for i in range(0,k,1):      #creates columns of desired outputs for Network Level 1
        #buying
        if output[i,0] == 1:
            output[i,1] = 1
        try:
            if (output[i-1,0] == 1 or output[i+1,0] == 1) and i >= 1 and i <= k-2:
                output[i,1] = 0.8
        except:
            pass
        try:
            if (output[i-2,0] == 1 or output[i+2,0] == 1) and i >= 2 and i <= k-3:
                if output[i,1] < 0.8 and output[i,1] > 0:       #averages buy overlap
                    output[i,1] = (output[i,1] + 0.5)/2
                if output[i,1] == 0:
                    output[i,1] = 0.5
        except:
            pass
        try:
            if (output[i-3,0] == 1 or output[i+3,0] == 1) and i >= 3 and i <= k-4:
                if output[i,1] < 0.8 and output[i,1] > 0:       #averages buy overlap
                    output[i,1] = (output[i,1] + 0.1)/2
                if output[i,1] == 0:
                    output[i,1] = 0.1
        except:
            pass
        
        #selling
        if output[i,0] == -1:
            output[i,2] = -1
        try:
            if (output[i-1,0] == -1 or output[i+1,0] == -1) and i >= 1 and i <= k-2:
                output[i,2] = -0.8
        except:
            pass
        try:
            if (output[i-2,0] == -1 or output[i+2,0] == -1) and i >= 2 and i <= k-3:
                if output[i,2] > -0.8 and output[i,2] < 0:      #averages sell overlap
                    output[i,2] = (output[i,2] - 0.5)/2
                if output[i,2] == 0:
                    output[i,2] = -0.5          
        except:
            pass
        try:
            if (output[i-3,0] == -1 or output[i+3,0] == -1) and i >= 3 and i <= k-4:
                if output[i,2] > -0.8 and output[i,2] < 0:      #averages sell overlap
                    output[i,2] = (output[i,2] - 0.1)/2
                if output[i,2] == 0:
                    output[i,2] = -0.1       
        except:
            pass
     
    
    return output
    

def ProfitSpeed(array):
    '''
    Generates a column of profit speeds (%profit/dt). Desired output of Network Level 2
    Array must have already gone through optimalbuy(). 
    '''
    
    k = int(array.shape[0])
    ps = np.zeros((k,1))
    
    for i in range(k-1,0,-1):
        if array[i,9] == 1:     #if date i is an optimal buy date
            sindx = i - 1
            z = True
            while z==True:
                sindx = sindx - 1
                if sindx > 0 or sindx == 0:
                    if array[sindx,9] == -1:        #sindx = index of next optimal sell day
                        z = False
                if sindx < 0:
                    z = False
                    
            if sindx > 0 or sindx == 0:
                if (((array[i,0]) * (i - sindx)) == 0):
                    raise ValueError("Divide by zero in profit speed")
                
                Pspeed = ((array[sindx,0] - array[i,0]) / ((array[i,0]) * (i - sindx)))*100       #profit/(time*price at buy in). x100 so that Pspeed represents % per day
                ps[i] = Pspeed 

                #finds profit speed before optimal buy date
                z = True
                d = 0
                while z == True:
                    d += 1
                    if (i+d)<k and array[i+d,9] == 0:
                        if (((array[i+d,0]) * d) == 0):
                            raise ValueError("Divide by zero in profit speed")
                            
                        Pspeedp1 = ((array[i,0] - array[i+d,0]) / ((array[i+d,0]) * d))*100  #~  RuntimeWarning: divide by zero encountered in double_scalars. x100 so that Pspeed represents % per day
                        ps[i+d] = Pspeedp1 
                    else:
                        z = False
               
                #finds profit speed after optimal buy date
                for r in range(i-1,sindx,-1):
                    Pspeedr = ((array[sindx,0] - array[r,0]) / ((array[r,0]) * (r - sindx)))*100  #x100 so that Pspeed represents % per day
                    ps[r] = Pspeedr
            
    
    return ps
  
 
def slopeMomentum(array):
    '''
    Generates 2 columns indicating 2 day and 5 day slop momentum
    Must be used after slope calculation in the main process function
    '''

    k = int(array.shape[0])
    slopeMom = np.zeros((k,4))

    TwoSlopeCounter = 0
    FiveSlopeCounter = 0
    TwoDiscrete = 0
    FiveDiscrete = 0

    for i in range(k-1,0,-1):   #starts at the beginning date

        if array[i,6] > 0:      #if 2 day slope is positive
            if TwoSlopeCounter < 0:
                TwoSlopeCounter = 0
                TwoDiscrete = 0
            TwoSlopeCounter += array[i,6]
            TwoDiscrete += 1

        if array[i,6] < 0:      #if 2 day slope is negative
            if TwoSlopeCounter > 0:
                TwoSlopeCounter = 0
                TwoDiscrete = 0
            TwoSlopeCounter += array[i,6]
            TwoDiscrete += -1

        if array[i,7] > 0:      #if 5 day slope is positive
            if FiveSlopeCounter < 0:
                FiveSlopeCounter = 0
                FiveDiscrete = 0
            FiveSlopeCounter += array[i,7]
            FiveDiscrete += 1

        if array[i,7] < 0:      #if 5 day slope is negative
            if FiveSlopeCounter > 0:
                FiveSlopeCounter = 0
                FiveDiscrete = 0
            FiveSlopeCounter += array[i,7]
            FiveDiscrete += -1

        slopeMom[i,0] = TwoSlopeCounter
        slopeMom[i,1] = FiveSlopeCounter
        slopeMom[i,2] = TwoDiscrete
        slopeMom[i,3] = FiveDiscrete



    return slopeMom


def process(ticker, dataframe=False):

    '''
    Processes the data for a single stock. Creates a pandas dataframe.
    If the parameter dataframe is passed, it will use the passed dataframe rather than a file in StockData (NOT YET IMPLIMENTED).
    Saves dataframe to CSV file.
    '''
    try:
        filepath = 'Data/StockData/' + ticker + '.csv'
        dataframe = pd.DataFrame.from_csv(filepath)
        dataframe.index.name="date"
        dataframe.sort_values("date",ascending=0).to_csv(filepath)

        try:
            file = open(filepath,'r')
        except:
            return

        row = 0
        
        data = np.genfromtxt(filepath,delimiter=',')    #generates data array from file

        if (data.shape[1] == 6):
            #Data is missing the AdjClose column (not included in current API data).
            #Since it's not really used, we'll replace the column with zeros
            height = data.shape[0]
            zeros = np.zeros(height)
            zeros = zeros.reshape(height, 1)
            data = np.hstack((data, zeros))

        data = np.delete(data,0,0)
        data = np.delete(data,0,1)
        
        k = int(data.shape[0])
        zeros = np.zeros((k,3))
        data = np.hstack((data,zeros))
        
        for i in range(0,k-1,1):        #6th column is the 2 day slope 
            data[i,6] = data[i,0] - data[i+1,0]

        for i in range(0,k-4,1):        #7th column is the 5 day slope
            data[i,7] = data[i,0] - data[i+4,0]
        
        for i in range(0,k-30,1):       #8th column is the month's standard deviation
            data[i,8] = np.std(data[i:i+30,0])

            
        for line in file:       #obtains vertical array of dates
            if row == 0:
                row += 1
            else:
                r = line.split(',')
                
                if row == 1:
                    dates = np.array(r[0])
                    row += 1
                else:
                    arow = np.array(r[0])  
                    dates = np.vstack((dates,arow))
        
                    
        optimal = optimalbuy(data)
        data = np.hstack((data,optimal))        #9th column optimal buy and sell dates, 10 and 11 column desired Level 1 Outputs
        sprofit = ProfitSpeed(data)
        
        indx = 0
        while True:     #finds index of most recent sell date
            if sprofit[indx,0] >0:
                indx = indx - 1
                break
            else:
                indx += 1
        
        data = np.hstack((data,sprofit))        #12th column is the profit speed for that day

        #********************************
        #10-2-2017: Tacked on data columns, added running sum of pos or negative slopes for
        #both 2 and 5 days. Added to far end of processed data file to avoid fucking up 
        #any location based dependencies
        #********************************

        slopeMomem = slopeMomentum(data)
        data = np.hstack((data,slopeMomem))     #13 column is the 2 day slope momentum, 14 column is the 5 day slope momentum, 15 column is 2 Day Discrete Momomentum, 16 column is 5 Day Discrete Momentum

        
        data = data[indx:k-31,:]     #truncates unprocessed data at beggining of date range and the end week of date range
        dates = dates[indx:k-31,:]       #truncates dates list   
        dates = dates.tolist()
        
        for i in range(0, len(dates), 1):
            dates[i] = dates[i][0]
        
        header = ["Open", "High", "Low", "Close", "Volume", "Adj Close", "2 Day Slope", "5 Day Slope", "Standard Dev", "Optimal Dates", "Desired Level 1 Out Buy", "Desired Level 1 Out Sell", "Profit Speed", "2 Day Momentum", "5 Day Momentum", "2D Discrete Moementum", "5D Discrete Moementum"]

        dataFrame = pd.DataFrame(data=data, index = dates, columns = header)
        dataFrame.index.name = "date"

        #Adding new data column processing under here, so we don't have to deal with our arcane legacy numpy code
        dataFrame["2 Day Normalized Slope"] = dataFrame["2 Day Slope"] / dataFrame["Open"] * 100  #Multiple by 100, that way data points would represent % values
        dataFrame["5 Day Normalized Slope"] = dataFrame["5 Day Slope"] / dataFrame["Open"] * 100

        dataFrame["2 Day Normalized Momentum"] = dataFrame["2 Day Momentum"] / dataFrame["Open"] * 100
        dataFrame["5 Day Normalized Momentum"] = dataFrame["5 Day Momentum"] / dataFrame["Open"] * 100

        dataFrame["Standard Dev Normalized"] = dataFrame["Standard Dev"] / dataFrame["Open"] * 100

        #Create PcsData direcetory if not present
        if not os.path.isdir("Data/PcsData"):
            os.mkdir("Data/PcsData")

        #Save processed data
        savepath = 'Data/PcsData/' + ticker + '.csv'
        dataFrame.to_csv(savepath)

    except Exception as e:
        #print(e)
        pass
    
    
def processAllTickers():
    '''
    Creates pandas dataframe CSVs for every ticker included in ListOfTicjerSymbols.csv
    '''

    tickerFile = open('Data/ListOfTickerSymbols.csv','r') #opens ticker file
    
    listOfTickers = []
    for line in tickerFile:	
        listOfTickers.append(line.rstrip())

    tickerFile.close()
 
    processCount = multiprocessing.cpu_count() - 1

    pool = Pool(processCount)

    for _ in tqdm.tqdm(pool.imap_unordered(process, listOfTickers), total=len(listOfTickers)):
        pass

#-------------------------------------------------------------------------------------------

if __name__ == '__main__':
    processAllTickers()  
    utils.emitAsciiBell()
    



