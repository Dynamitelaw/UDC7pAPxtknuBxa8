'''
Dynamitelaw
Backend for Nearest Neighbor predictions.
'''


import numpy as np
from scipy import spatial
import sys


def GenerateNearestData(ticker,bs, fields = None, daterange = None, OutputMultiple = False, includeOptimalDates = False, overideDirectory = False):
    '''
    Generates an array of network data points for calculating distance and desired outputs for specified stock for all days.
    The output list has 2 elements; out = [array of reference data points, array of desired outputs]

    bs tells the function whether you want the outputs to be desired buy values ('b'), or desired sell values ('s'), or the profitspeed ('ps')

    Fields is an optional list of strings specifying which data columns you want included. Defaults to all fields
        possible fields-> ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close', '2 Day Slope', '5 Day Slope', 'Standard Dev', '2 Day Momentum', '5 Day Momentum', '2D Discrete Moementum', '5D Discrete Moementum']
        
    Daterange is an optional 2 element list, containing the min and max dates desired for the data.
    Dates must have following format:  'YYYY-MM-DD'
    Dates must be given in increasing order (ie. 2012 before 2015)

    OutputMultiple multiplies the desired output by specified amount. Defaults to 1. Used to provide larger output space

    Setting includeOptimalDates to True adds a 3rd element to the output list: a column of trinary optimal dates.
    Useful for accurate historical testing.

    overideDirectory is an optional string to specify which directory to source the data from
    '''
    if overideDirectory:
        filepath = overideDirectory + ticker
    else:
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
        
        desire = data[:,[10,11,12]]      #obtains desired outputs
        optimals = data[:,9]        #trinary optimal dates

        if (bs == 'b'):
            desire = desire[:,0]
        if (bs == 's'):
            desire = desire[:,1]
        if (bs == 'ps'):
            desire = desire[:,2]
        if OutputMultiple:
            desire = desire * OutputMultiple

        
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
                if f == '2D Discrete Moementum':
                    include.append(15)
                if f == '5D Discrete Moementum':
                    include.append(16)

            ndata = data[:,include]
        else:
            ndata = data[:,[0,1,2,3,4,5,6,7,8,13,14,15,16]]
         
		
        error = False
        if daterange:       #if date range is specified
            if (len(daterange[0]) != 10) or (len(daterange[1]) != 10) or (len(daterange) != 2):     #if daterange is invalid
                print ('Error: Invalid Daterange')
                error = True
            else:
                dateRangeList = []      #list containing range of dates
                for d in daterange:
                    date = []
                    year = int(d[0:4])
                    month = int(d[5:7])
                    day = int(d[8:10])
                    date.append(year)
                    date.append(month)
                    date.append(day)
                    dateRangeList.append(date)
                    
        if error == False:
            if daterange:       #truncates IO for that stock based on date range (if specified)
                startIndx = 0   #first index in the array where date range is valid
                for i in range(0,k,1):
                    delete = False
                    sdate = dates[i][0][1:11]
                    syear = int(sdate[0:4])
                    smonth = int(sdate[5:7])
                    sday = int(sdate[8:10])
                    if (syear > dateRangeList[1][0]):
                        delete = True
                    if (syear == dateRangeList[1][0] and smonth > dateRangeList[1][1]):
                        delete = True
                    if (syear == dateRangeList[1][0] and smonth == dateRangeList[1][1] and sday > dateRangeList[1][2]):
                        delete = True
                    
                    if delete == True:
                        startIndx += 1
                    else:
                        break

                endIndx = k-1   #last index in the array where date range is valid
                for i in range(k-1,1,-1):
                    delete = False
                    sdate = dates[i][0][1:11]
                    syear = int(sdate[0:4])
                    smonth = int(sdate[5:7])
                    sday = int(sdate[8:10])
                    if (syear < dateRangeList[0][0]):
                        delete = True
                    if (syear == dateRangeList[0][0] and smonth < dateRangeList[0][1]):
                        delete = True
                    if (syear == dateRangeList[0][0] and smonth == dateRangeList[0][1] and sday < dateRangeList[0][2]):
                        delete = True
                    
                    if delete == True:
                        endIndx -= 1
                    else:
                        break

                #truncates output based on date range
                dates = dates[startIndx:endIndx,:]
                ndata = ndata[startIndx:endIndx,:]
                desire = desire[startIndx:endIndx,:]
                optimals = optimals[startIndx:endIndx,:]
                k = int(dates.shape[0])

        tout = [ndata , desire]
        if includeOptimalDates:
            tout.append(optimals)
        return tout
    
    except Exception as e:
        #sfile.close()
        print(e)
        print (ticker)
        return 0

    sfile.close()


def NearestPredict(sourcePoint, dataPoints, outputs, points = 5, distanceMetric = 'seuclidean', dataPointWeights = False):
    '''
    Outputs a single predicted value using Nearest Neighbor. Each data point's contribution
    to the prediction is inversely proportional to it's distance from the source point.

    sourcePoint is the data vector of the day you want to predict.
    dataPoints is an array of historical data vectors.
    outputs is an array of historical outputs, corresponding with the dataPoints

    points is how many of the closest dataPoints to include while calculating the prediction. Defaults to 5.

    distanceMetric is the type of distance metric used in calculating distances (no duh). For more info,
        please see cdist documentation: 
        https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.spatial.distance.cdist.html#scipy.spatial.distance.cdist

    dataPointWeights is not yet implemented
    '''

    ko = int(outputs.shape[0])
    kd = int(dataPoints.shape[0])
    wd = int(dataPoints.shape[1])
    ws = int(sourcePoint.shape[1])

    #Checks to make sure that the dimensions of all input arrays match
    try:
        if (wd != ws):
            print('Error: SourcePoint of dimension ' + str(ws) + ' does not match dataPoints of dimension ' + str(wd))
        elif (ko != kd):
            print('Error: dataPoints of dimension ' + str(kd) + ' does not match outputs of dimension ' + str(ko))
        else:
            distanceArray = np.transpose(spatial.distance.cdist(sourcePoint,dataPoints,distanceMetric))     #calculate distances from source to points
            
            indxArray = np.zeros((ko,1))
            for i in range(0,ko,1):
                indxArray[i,0] = i 

            distanceArray = np.hstack((distanceArray,indxArray))
            distanceArray = distanceArray[distanceArray[:,0].argsort()]     #sorts indexes by distance

            #takes the weighted average of outputs, treating their distances as experimental uncertainties
            uncertaintySum = 0
            measurementSum = 0
            for p in range(0,points,1):
                uncertaintySum += 1/((distanceArray[p,0])**2)
                measurementSum += (outputs[int(distanceArray[p,1])])/((distanceArray[p,0])**2)


            prediction = measurementSum / uncertaintySum
            if ((prediction < 0) or (prediction > 0) or (prediction == 0)):
                return prediction
            else:
                return 0

    except Exception as e:
        #print (e + '\n')
        return 0


#------------------------------------------------------------------------------------------------------------
'''
s = np.array([[5.0,5.0]])
X = np.array([[0,0],[4.1,4.1],[8.1,8.1],[9.1,9.1]])
Y = np.array([[0],[4],[8],[9]])

print(NearestPredict(s,X,Y,points = 2, distanceMetric = 'euclidean'))

print(X)
X = X[X[:,1].argsort()]
print("")
print(X)
#P = [x,y,z,a,b,c,d]
k = np.transpose(spatial.distance.cdist(o,X,'seuclidean'))
#GenerateNearestData('DIS.csv','ps', OutputMultiple = 1000)
#print(k)
'''