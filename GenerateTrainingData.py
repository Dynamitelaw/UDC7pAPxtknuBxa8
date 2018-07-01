'''
Dynamitelaw
Generates Network Input and Output data for the market based on inputed fields.
'''

import numpy as np
import sys
import os
import random


def GenerateIO(ticker,bs, normalize = False, categorical = False, fields = None, daterange = None, OutputMultiple = False, ZeroPruneRatio = False, HistoricalDayLength = 90):
    '''
    Generates an array of network Level 1 inputs and desired outputs for specified stock for all days.
    The output list has 2 elements; out = [[list of inputs],[list of desired outputs]]

    bs tells the function whether you want the outputs to be desired buy values ('b'), or desired sell values ('s'), both ('bs'), their sum ('sum'), or the profitspeed ('ps')

    Setting normalize to True divides all input data points by the historical maximum of that variable tpye.

    Setting categorical to True sets the outputs to be logits denoting descrete categories of possible outputs *currently does not work for 'bs' or 'sum'*.
    
    Fields is an optional list of strings specifying which data columns you want included. Defaults to all fields
        possible fields-> ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close', '2 Day Slope', '5 Day Slope', 'Standard Dev', '2 Day Momentum', '5 Day Momentum']
        ***currently missing Discrete Momentum fields
        
    Daterange is an optional 2 element list, containing the min and max dates desired for the data.
    Dates must have following format:  'YYYY-MM-DD'
    Dates must be given in increasing order (ie. 2012 before 2015)

    OutputMultiple multiplies the desired network output by specified amount. Defaults to 1. Used to provide larger output space

    ZeroPruneRatio is used to reduce the number of zeros in the desired outputs, so that the network doesn't simply fit the regression to all zeros.
    Ex) setting ZeroPruneRatio = 0.2 will only keep 20% of zero outputs

    HistoricalDayLength is how many days of historical data you want the network to take as an input. Defaults to 90, cannot exceed 90.
    '''
    
    filepath = 'Data/PcsData/' + ticker 
    
    try:
        sfile = open(filepath,'r')
        row = 0
        
        data = np.genfromtxt(filepath,delimiter=',')    #generates data array from file
        #sfile.close() 
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
        desire = data[:,[10,11,12]]      #obtains desired outputs
        
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
                if f == '2 Day Momentum':
                    include.append(13)
                if f == '5 Day Momentum':
                    include.append(14)

            ndata = data[:,include]
        else:
            ndata = data[:,[0,1,2,3,4,5,6,7,8,9,13,14]]
         
       
        tout = []       #total io (input output) array for all days for this stock
        for i in range(0,k-91,1):
            di = ndata[i:i+HistoricalDayLength,:]
            if normalize == True:       #normalizes input data if specified
                difin = np.copy(di)

                for f in range(0,di.shape[1]):
                    if ((np.amax(di,0)[f]) != 0):
                        difin[:,f] = difin[:,f] / (np.amax(di,0)[f])
                    else:
                        difin[:,f] = difin[:,f]

            else:
                difin = di
            day = []        #total io array for that day
            #day.append(ticker)
            if ZeroPruneRatio:  #prunes zero outputs if specified
                if ((desire[i,0] == 0) or (desire[i,1] == 0)):
                    if (random.random() < ZeroPruneRatio):
                        day.append(dates[i])
                        day.append(difin)
                        if OutputMultiple: #multiplies outputs if specified 
                            day.append(desire[i,:]*OutputMultiple)
                        else:
                            day.append(desire[i,:])
                        
                        tout.append(day)
                else:
                    day.append(dates[i])
                    day.append(difin)
                    if OutputMultiple:  #multiplies outputs if specified 
                        day.append(desire[i,:]*OutputMultiple)
                    else:
                        day.append(desire[i,:])
                    
                    tout.append(day)
            else:
                day.append(dates[i])
                day.append(difin)
                if OutputMultiple:  #multiplies outputs if specified 
                    day.append(desire[i,:]*OutputMultiple)
                else:
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
                if categorical == True:     #assignes outputs to descrete categories, if specified
                    catout = np.zeros(5)
                    if d[2][0] == 0:
                        catout[0] = 1
                    if d[2][0] == 0.1:
                        catout[1] = 1
                    if d[2][0] == 0.5:
                        catout[2] = 1
                    if d[2][0] == 0.8:
                        catout[3] = 1
                    if d[2][0] == 1:
                        catout[4] = 1
                    dout.append(catout)
                else:
                    dout.append(d[2][0])
            if bs == 's':
                if categorical == True:
                    catout = np.zeros(5)
                    if d[2][0] == 0:
                        catout[0] = 1
                    if d[2][0] == -0.1:
                        catout[1] = 1
                    if d[2][0] == -0.5:
                        catout[2] = 1
                    if d[2][0] == -0.8:
                        catout[3] = 1
                    if d[2][0] == -1:
                        catout[4] = 1
                    dout.append(catout)
                else:
                    dout.append(d[2][1])
            if bs == 'bs':
                dout.append(d[2])
            if bs == 'sum':
                dout.append(d[2][0] + d[2][1])
            if bs == 'ps':
                dout.append(d[2][2])
        supremeout = [din,dout]
        '''
        try:
            sfile.close()
        except:
            pass
            '''
        return supremeout
    
    except Exception as e:
        #sfile.close()
        print(e)
        print (ticker)
        return 0

    sfile.close()
        

    
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



tickerlist = os.listdir('Data/PcsData/')  

k = GenerateIO(tickerlist[0],'sum',normalize = True)
t = k[1][0:20]
print (t)

'''