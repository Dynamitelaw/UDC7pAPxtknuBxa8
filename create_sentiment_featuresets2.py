'''
Dynamitelaw
Generates Network Input and Output data for every day for a specified stock.
'''

import numpy as np


def GenInputOutput(ticker,fields = None):
    '''
    Generates an array of network Level 1 inputs and desired outputs for specified stock for all days.
    Each element of output list is a 3 element list -> [date,array[day's input], float(desired output)].
    
    Fields is an optional list of strings specifying which data columns you want included. Defaults to all fields
        possible fields) ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close', '2 Day Slope', '5 Day Slope', 'Standard Dev']
    '''
    
    filepath = 'Data/PcsData/' + ticker + '.csv'
    file = open(filepath,'r')
    row = 0
    
    data = np.genfromtxt(filepath,delimiter=',')    #generates data array from file
    data = np.delete(data,0,0)
    data = np.delete(data,0,1)
    
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
                
        
    k = int(data.shape[0])
    dates = dates[0:k-91]      #assigns dates to output array
    desire = data[:,9]      #obtains desired outputs
    
    if fields:      #truncates data array based on specified fields to include. Defaults to all
        include = []
        for f in fields:
            if f == 'Open':
                include.append(0)
            if f == 'High':
                include.append(1)
            if f == 'Low':
                include.append(2)
            if f == 'Close':
                include.append(3)
            if f == 'Volume':
                include.append(4)
            if f == 'Adj Close':
                include.append(5)
            if f == '2 Day Slope':
                include.append(6)
            if f == '5 Day Slope':
                include.append(7)
            if f == 'Standard Dev':
                include.append(8)

        ndata = data[:,include]
    else:
        ndata = data[:,0:10]
     
   
    tout = []       #total io (input output) array for all days for this stock
    for i in range(0,k-91,1):
        di = ndata[i:i+90,:]
        day = []        #total io array for that day
        day.append(dates[i])
        day.append(di)
        day.append(desire[i])
        
        tout.append(day)
        
     
    return tout
    file.close()
    


#-----------------------------------------------------------------------------

l = GenInputOutput('4BV.DU',['Open','High'])
print(l[1])
'''
a = np.array([1,2,3,4,5,6]).reshape((2,3))
#print (a)

a = a[:,[0,2]]
print (a.shape)'''
