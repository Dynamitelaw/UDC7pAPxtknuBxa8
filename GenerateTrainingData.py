'''
Dynamitelaw
Generates Network Input and Output data for the market based on inputed fields.
Writes data to pickle.
Retrieves training data from pickle.
'''

import numpy as np
import pickle
import sys
import os

def GenerateIO(ticker,bs, normalize = False, fields = None, daterange = None):
    '''
    Generates an array of network Level 1 inputs and desired outputs for specified stock for all days.
    The output list has 2 elements; out = [[list of inputs],[list of desired outputs]]

    bs tells the function whether you want the outputs to be desired buy values ('b'), or desired sell values ('s')
    
    Fields is an optional list of strings specifying which data columns you want included. Defaults to all fields
        possible fields-> ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close', '2 Day Slope', '5 Day Slope', 'Standard Dev']
        
    Daterange is an optional 2 element list, containing the min and max dates desired for the data.
    Dates must have following format:  'YYYY-MM-DD'
    Dates must be given in increasing order (ie. 2012 before 2015)
    '''
    
    filepath = 'Data/PcsData/' + ticker 
    sfile = open(filepath,'r')
    try:
        row = 0
        
        data = np.genfromtxt(filepath,delimiter=',')    #generates data array from file
        data = np.delete(data,0,0)
        data = np.delete(data,0,1)
        
        for line in sfile:       #obtains vertical array of dates
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
        
        sfile.close()            
            
        k = int(data.shape[0])      #number of dates in file
        dates = dates[0:k-91]      #assigns dates to output array
        desire = data[:,[10,11]]      #obtains desired outputs
        
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
            ndata = data[:,0:9]
         
       
        tout = []       #total io (input output) array for all days for this stock
        for i in range(0,k-91,1):
            di = ndata[i:i+90,:]
            if normalize == True:       #normalizes input data if specified
                dprice = di[0,0]
                difin = di / dprice
            else:
                difin = di
            day = []        #total io array for that day
            #day.append(ticker)
            day.append(dates[i])
            day.append(difin)
            day.append(desire[i,:])
            
            tout.append(day)
         
        error = False
        if daterange:       #if date range is specified
            if (len(daterange[0]) != 10) or (len(daterange[1]) != 10) or (len(daterange) != 2):     #if daterange is invalid
                print ('Error: Invalid Daterange')
                error = True
            else:
                dates = []      #list containing range of dates
                for d in daterange:
                    date = []
                    year = int(d[0:4])
                    month = int(d[5:7])
                    day = int(d[8:10])
                    date.append(year)
                    date.append(month)
                    date.append(day)
                    dates.append(date)
                    
        if error == False:
            if daterange:       #truncates IO for that stock based on date range (if specified)
                sidx = 0
                delidx = []
                for d in tout:
                    delete = False
                    sdate = d[1][0][1:11]
                    syear = int(sdate[0:4])
                    smonth = int(sdate[5:7])
                    sday = int(sdate[8:10])
                    if (syear < dates[0][0]) or (syear > dates[1][0]):
                        delete = True
                    if (syear == dates[0][0] and smonth < dates[0][1]) or (syear == dates[1][0] and smonth > dates[1][1]):
                        delete = True
                    if (syear == dates[0][0] and smonth == dates[0][1] and sday < dates[0][2]) or (syear == dates[1][0] and smonth == dates[1][1] and sday > dates[1][2]):
                        delete = True
                    
                    if delete == True:
                        delidx.append(sidx)
                    
                    sidx += 1
            
                delidx.sort(reverse = True)
                for i in delidx:
                    del tout[i]        #deletes unwanted dates
        

        din = []        #list of network L1 inputs
        dout = []       #list of corresponding network L1 outputs       
        for d in tout:
            din.append(d[1])
            if bs == 'b':
                dout.append(d[2][0])
            if bs == 's':
                dout.append(d[2][1])

        supremeout = [din,dout]
        
        try:
            sfile.close()
        except:
            pass

        return supremeout
    
    except Exception as e:
        sfile.close()
        print(e)
        pass
        

    
#-----------------------------------------------------------------------------


##########################################
#  For some reason, you can't run GenerateIO
#  for the entire market in one tf session. It breaks
#  after processing about 1000 stocks 
#  Erno 24: Too Many Open Files, even though each
#  file is closed after use. But I can't recreate
#  the error in the script below
##########################################
'''
tickerlist = os.listdir('Data/PcsData/')  
l = len(tickerlist)
z = 0
BreakCount = 0
print ('Starting Test')
for ticker in tickerlist:
    z += 1
    try:
        k = GenerateIO(ticker,'b')
        t = k[0][0]
        print (str((z*100)/l)+'% done')
    except Exception as e:
        print (e)
        print('Process broke at stock '+str(z) + '(' + str(ticker) + ')')
        BreakCount += 1
        
print (str(l) + 'stocks attempted')
print (str(BreakCount) + 'stocks failed')


k = GenerateIO('A.csv','b')
print k[0][0][0]
z = GenerateIO('A.csv','b',normalize = True)
print z[0][0][0]
'''
