'''
Dynamitelaw

Processes raw stock data for neural network intput. 
Adds 2 day slope, 5 day slope, and 30 day standard deviation.

'''

import numpy as np

def optimalbuy(array)
    '''
    Makes an array marking the optimal buy and sell dates. 
    1 for buy, -1 for sell, 0 OTW
    '''
    
    state = 0
    k = int(data.shape[0])
    
    for i in range(k,0,-1):
        if array[i,1] < array[i-1,1] and array[i,1] < array[i-5,1]
    

def process(ticker):

    '''
    Processes the data for a single stock. Outputs processed data into PcsData directory
    '''
    
    filepath = './Data/StockData/' + ticker + '.csv'
    file = open(filepath,'r')
    row = 0
    
    data = np.genfromtxt(filepath,delimiter=',')    #generates data array from file
    data = np.delete(data,0,0)
    data = np.delete(data,0,1)
    
    k = int(data.shape[0])
    zeros = np.zeros((k,3))
    data = np.hstack((data,zeros))
    
    for i in range(0,k-1,1):        #6th row is the 2 day slope 
        data[i,6] = data[i,0] - data[i+1,0]

    for i in range(0,k-4,1):        #7th row is the 5 day slope
        data[i,7] = data[i,0] - data[i+4,0]
    
    for i in range(0,k-30,1):       #8th row is the month's standard deviation
        data[i,8] = np.std(data[i:i+30,0])

        
    for line in file:       #obtains vertical array of dates
        if row == 0:
            row += 1
        else:
            r = line.split(',')
           
            for i in range(1,7,1):
                r[i] = float(r[i].rstrip())
            
            if row == 1:
                dates = np.array(r[0])
                row += 1
            else:
                arow = np.array(r[0])  
                dates = np.vstack((dates,arow))
    
 
    savepath = './Data/PcsData/' + ticker + '.csv'
    fout = open(savepath,'w')
    for i in range (0,k,1):     #writes processed data to new file
        line = [dates[i,0]]
        dline = data[i,:].tolist()
        line.extend(dline)
        fout.write(str(line).strip("[]") + '\n')
    
    fout.close()
    

ticks = open('./Data/ListOfTickerSymbols.csv','r')

row = 0
for l in ticks:     #process all stocks on the ticker list
    if row == 0:
        row += 1
    else:
        ticker = str(l).rstrip()
        process(ticker)
