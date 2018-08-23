'''
Dynamitelaw
Tests and optimizes the NearestNeighbor Algorithm.
'''


import numpy as np
import sys
import os
from scipy import spatial

from scipy import stats
import warnings
import time
import math
import multiprocessing as mp
from usefulThings import printLocation



def NearestNeighborTester(ticker,bs,fields, daterange = None, points = 5, distanceMetric = 'seuclidean', sampleLog = False, ignoreWarnings = True, progressHeader = '', dayBackValue = 0, overideDirectory = False, silencePrint = False):
    '''
    Tests the NearestNeighbor Algorithm on a single stock. Outputs the correlation coefficient. Returns -2 if input stock is lacking suffiecient historical data.

    bs tells the function whether you want the outputs to be desired buy values ('b'), or desired sell values ('s'), or the profitspeed ('ps')

    Fields is an optional list of strings specifying which data columns you want included. Defaults to all fields
        possible fields-> ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close', '2 Day Slope', '5 Day Slope', 'Standard Dev', '2 Day Momentum', '5 Day Momentum', '2D Discrete Moementum', '5D Discrete Moementum']

    Daterange is an optional 2 element list, containing the min and max dates desired for the data.
    Dates must have following format:  'YYYY-MM-DD'
    Dates must be given in increasing order (ie. 2012 before 2015)

    points is how many of the closest dataPoints to include while calculating the prediction. Defaults to 5. 250 hard max (softmax at ~220)

    distanceMetric is the type of distance metric used in calculating distances (no duh). For more info,
        please see cdist documentation: 
        https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.spatial.distance.cdist.html#scipy.spatial.distance.cdist

    Setting sampleLog to True generates a csv file of predicted values vs actual values.

    Setting ignoreWarnings to True supresses all Runtime Warnings

    progressHeader allows you to insert a header in front of the local prograss bar. Must be a single string.

    dayBackValue lets you base the prediction on a certian historical day's data. Needs to be set to 1 for realistic use of the Volume field

    overideDirectory is an optional string to specify which directory to source the data from

    silencePrint prevents this function from printing Progress bar
    '''

    try:
        #Generates data set of stock
        dataSet = GenerateNearestData(ticker,bs, fields, daterange, OutputMultiple = False, includeOptimalDates = True, overideDirectory = overideDirectory)
        dataPoints = dataSet[0]
        outputs = dataSet[1]
        optimals = dataSet[2]

        k = int(dataPoints.shape[0])    #size of data set
        if (k > 251):
            wheel = ["/","--","\ ","|"]
            predictionSet = np.zeros(k)    #NN predictions
            for i in range(0,k-250,1):
                if (not silencePrint):
                    #Progress Bar
                    sys.stdout.write('\r')
                    sys.stdout.write(progressHeader + 'Procressing ' + ticker + ' ' + str((100*i)/(k-250)) + '%  ' + wheel[(i/15)%4])
                    sys.stdout.flush()
                else:
                    pass

                sourcePoint = np.array([dataPoints[i+dayBackValue]])   #prediction based of curent day's data by default
                
                totalPeaks = 0
                for s in range(i,k-1,1):    #historical data input limited to when desired outputs would have been known in real time
                    if (optimals[s] != 0):
                        totalPeaks += 1
                    if (totalPeaks == 2):
                        startIndx = s
                        break

                historicalDataInput = dataPoints[startIndx:,:]
                hOutputs = outputs[startIndx:]

                if ignoreWarnings:         #supresses warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        prediction = NearestPredict(sourcePoint, historicalDataInput, hOutputs, points, distanceMetric)        #predicts output
                        predictionSet[i] = prediction
                else:
                    prediction = NearestPredict(sourcePoint, historicalDataInput, hOutputs, points, distanceMetric)        #predicts output
                    predictionSet[i] = prediction

            correlation = stats.pearsonr(predictionSet,outputs)[0]
            results = np.transpose(np.vstack((predictionSet,outputs)))
            results = results[0:k-251,:]

            if sampleLog:    #generates log
                savepath = 'NearestNeighborSample.csv'
                fout = open(savepath,'w')
                for d in range(0,int(results.shape[0]),1):
                    fout.write(str(results[d,0]) + ',' + str(results[d,1]) + '\n')

                fout.close()

            if (not silencePrint):
                #Clear Progress bar
                sys.stdout.flush()
                sys.stdout.write('\r')
                sys.stdout.write('                                                                     ')
                sys.stdout.flush()
                sys.stdout.write('\r')
            else:
                pass

            return correlation
        else:
            return -2
    except Exception as e:
        return -2
        pass


def NNOptimizer(runTimeName = '', shortenProgress = False, PrinterCarriageNumber = 0, startupSleepTime = 0, overideDirectory = False):
    '''
    Finds the best NearestPredict settings that lead to the highest correlation.
    Returns best settings as a list, of format [distanceMetric, [fields], points, average correlation coefficient].
    Prints best settings to a txt file.
    Keeps track of where in the procressing it left off, allowing you to split up the Procressing among different sessions.
    NNOptimizerSettings.txt alows you to define the optimization ranges, in order to run multiple concurrent instances.

    runTimeName is the label of this particular optimizer thread

    shortenProgress allows you to print a shorter Progress bar

    PrinterCarriageNumber allows you to set the starting location of the Progress bar

    startupSleepTime allows you to delay the start of the process by a certain amount of time (in seconds)

    overideDirectory allows you to overide the directory from which this process obtains it's data.
    Needed to avoid collision slowdowns amongs processes.
    '''

    time.sleep(startupSleepTime)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        print('----------------------------------------------')
        print('Initializing optimizer ' + runTimeName + '...\n')

        pfields = ['Open', 'Volume', '2 Day Slope', '5 Day Slope', 'Standard Dev', '2 Day Momentum', '5 Day Momentum', '2D Discrete Moementum', '5D Discrete Moementum']
        pmetrics = ['braycurtis','canberra','chebyshev','cityblock','correlation','cosine','dice','euclidean','hamming','jaccard','kulsinski','mahalanobis','matching','minkowski','rogerstanimoto','russellrao','seuclidean','sokalmichener','sokalsneath','sqeuclidean','wminkowski','yule']


        try:    #tries to load checkpoint
            path = runTimeName + 'NNOptimizerCheckpoint.txt'
            cfile = open(path,'r')

            checkpoint = []
            for line in cfile:
                checkpoint.append(float(line.rstrip()))

            metricMin = int(checkpoint[0])
            metricTracker = int(checkpoint[1])
            metricMax = int(checkpoint[2])
            fieldPermMin = int(checkpoint[3])
            fieldPermTracker = int(checkpoint[4])
            fieldPermMax = int(checkpoint[5])
            pointMin = int(checkpoint[6])
            pointTracker = int(checkpoint[7])
            pointMax = int(checkpoint[8])
            pointStep = int(checkpoint[9])
            maxCor = int(checkpoint[10])
            tickerTracker = int(checkpoint[11])
            stocksTried = int(checkpoint[12])
            corSum = float(checkpoint[13])

            cfile.close()

            print('Checkpoint found, continuing optimization from... \n')

        except Exception as e:    #loads settings from file
            try:
                path = runTimeName + 'NNOptimizerSettings.txt'
                sfile = open(path,'r')
                
                settings = []
                for line in sfile:
                    settings.append(float(line.rstrip()))

                metricMin = int(settings[0])
                metricTracker = metricMin
                metricMax = int(settings[1])
                fieldPermMin = int(settings[2])
                fieldPermTracker = fieldPermMin
                fieldPermMax = int(settings[3])
                pointMin = int(settings[4])
                pointTracker = pointMin
                pointMax = int(settings[5])
                pointStep = int(settings[6])
                maxCor = 0.0
                tickerTracker = 0
                stocksTried = 0
                corSum = 0.0

                sfile.close()

                print('No checkpoint found. Beginning  from... \n')
            except Exception as e:
                print ('Error: "' + runTimeName + 'NNOptimizerSettings.txt" failed to load \nGenerated default settings file and guide file')

                path = runTimeName + 'NNOptimizerSettings.txt'
                sfile = open(path,'w')
                sfile.write(str(0) + '\n' + str(21) + '\n' + str(1) + '\n' + str(511) + '\n' + str(1) + '\n' + str(220) + '\n' + str(1))
                sfile.close()

                path = runTimeName + 'NNOSettingsGuide.txt'
                sfile = open(path,'w')
                header = "Possible Distance Metrics = ['braycurtis','canberra','chebyshev','cityblock','correlation','cosine','dice','euclidean',\n    'hamming','jaccard','kulsinski','mahalanobis','matching','minkowski','rogerstanimoto','russellrao',\n    'seuclidean','sokalmichener','sokalsneath','sqeuclidean','wminkowski','yule']"
                header = header + "\nPossible Fields = ['Open', 'Volume', '2 Day Slope', '5 Day Slope', 'Standard Dev', '2 Day Momentum', '5 Day Momentum', '2D Discrete Moementum', '5D Discrete Moementum']"
                header = header + '\n---------------------------------------------------------------------------------------------------------------------------'
                sfile.write(header + '\nMetricMin D[0,21]\nMetricMax D[0,21]\nFieldCombinationMin D[1,511]\nFieldCombinationMax D[1,511]\nPointMin D[1,220]\nPointMax D[1,220]\nPointStep D[1,219]')
                sfile.close()

                print(e)
                return


        print('M = ' + str(metricTracker) + '| F = ' + str(fieldPermTracker) + '| P = ' + str(pointTracker) + '| T = ' + str(tickerTracker) + '\n')

        time.sleep(3)
        startTime = time.time()

        for m in range(metricTracker,metricMax + 1,1):        #tries every metric
            metric = pmetrics[m]
            for f in range(fieldPermTracker,fieldPermMax + 1,1):        #tries every field combination

                #converts field Permutation tracker into a 9 bit binary string
                permString = "{0:b}".format(f)
                length = len(permString)
                for i in range(0,9-length,1):
                    permString = '0' + permString

                cfields = []    #included fields
                for i in range(0,9,1):
                    if (permString[i] == '1'):
                        cfields.append(pfields[i])

                for point in range(pointTracker,pointMax + 1,pointStep):    #tries every point value
                    
                    #obtains list of stock files
                    if overideDirectory:
                        tickerlist = os.listdir(overideDirectory)
                    else:
                        tickerlist = os.listdir('Data/PcsData/')
                    length = len(tickerlist)

                    for tickIndx in range(tickerTracker,length,1):    #tries every stock  
                        percentFloat = (100.0/float(metricMax - metricMin + 1))*((m-metricMin) + (float(f - fieldPermMin)/(fieldPermMax - fieldPermMin + 1)) + (float(point - pointMin)/((pointMax - pointMin + 1)*(fieldPermMax - fieldPermMin + 1))) + ((float(tickIndx)*pointStep)/(length*((pointMax - pointMin + 1)*(fieldPermMax - fieldPermMin + 1)))))
                        percentComplete = int(10.0*percentFloat)/10.0
                        if shortenProgress:
                            header = '|' + runTimeName + ':' + str(percentComplete) + '%_' + metric
                        else:
                            header = str(percentComplete) + '%_' + metric + '|f(' + str(fieldPermTracker) + '/' + str(fieldPermMax) + ')-p(' + str(point) + '/' + str(pointMax) + '): '
                      
                        try:
                            corCoef = NearestNeighborTester(tickerlist[tickIndx],'ps',cfields,sampleLog = False, distanceMetric = metric, points = point, progressHeader = header, silencePrint = shortenProgress, overideDirectory = overideDirectory)
                            if ((corCoef != -2) and (not (math.isnan(corCoef)))):
                                corSum += corCoef
                                stocksTried += 1
                            if shortenProgress:        #prints shortened progress bar
                                printLocation (text = header + '(' + tickerlist[tickIndx][:-4] + ') ', x = PrinterCarriageNumber,y = 25)
                                printLocation (text = '|M(' + str(m) + '/' + str(metricMax) + ')F(' + str(fieldPermTracker) + '/' + str(fieldPermMax) + ')P(' + str(point) + '/' + str(pointMax) + ')   ', x = PrinterCarriageNumber, y = 26)
                                printLocation (text = '|T(' + str(tickIndx + 1) + '/' + str(length) +')    ', x = PrinterCarriageNumber, y = 27)

                        except Exception as e:
                            pass

                        if (((tickIndx % 20) == 0) and (tickIndx != 0)):    #updates checkpoint every 20 stocks processed 
                            savepath = runTimeName + 'NNOptimizerCheckpoint.txt'
                            cout = open(savepath,'w')
                            cout.write(str(metricMin) + '\n' + str(m) + '\n' + str(metricMax) + '\n' + str(fieldPermMin) + '\n' + str(f) + '\n' + str(fieldPermMax) + '\n' + str(pointMin) + '\n' + str(point) + '\n' + str(pointMax) + '\n' + str(pointStep) + '\n' + str(maxCor) + '\n' + str(tickIndx) + '\n' + str(stocksTried) + '\n' + str(corSum))
                            cout.close()
                            printLocation (text = header + '(*SVD)', x = PrinterCarriageNumber,y = 25)

                    if (stocksTried > 0):
                        corAvg = corSum / stocksTried
                    else:       #if metric invalid updates checkpoint and moves on with its life
                        savepath = runTimeName + 'NNOptimizerCheckpoint.txt'
                        cout = open(savepath,'w')
                        cout.write(str(metricMin) + '\n' + str((m + 1)) + '\n' + str(metricMax) + '\n' + str(fieldPermMin) + '\n' + str(fieldPermMin) + '\n' + str(fieldPermMax) + '\n' + str(pointMin) + '\n' + str(pointMin) + '\n' + str(pointMax) + '\n' + str(pointStep) + '\n' + str(maxCor) + '\n' + str(0) + '\n' + str(0) + '\n' + str(0))
                        cout.close()
                        printLocation (text = 'Skipping metric ' + str(pmetrics[m]), x = PrinterCarriageNumber,y = 25)
                        NNOptimizer(runTimeName = runTimeName, shortenProgress = shortenProgress, PrinterCarriageNumber = PrinterCarriageNumber, startupSleepTime = startupSleepTime, overideDirectory = overideDirectory)
                        return False

                    if (abs(corAvg) > maxCor):    #saves argument settings if average coefficient is better than past max
                        maxCor = abs(corAvg)
                        savepath = runTimeName + 'NNOptimizerMax.txt'
                        fout = open(savepath,'w')
                        fout.write(metric + '\n' + str(cfields) + '\n' + str(point) + '\n' + str(corAvg))
                        fout.close() 

                    #updates log
                    savepath = runTimeName + 'NNOptimizerMaxLog.csv'
                    try:
                        lfile = open(savepath,'r')
                        row = 0
                        
                        data = np.genfromtxt(filepath,delimiter=',')    #generates data array from file
                        #sfile.close() 
                        data = np.delete(data,0,0)
                        data = np.delete(data,0,1)
                        
                        metricsLog = []
                        for line in lfile:       #obtains list of metrics
                            if row == 0:
                                row += 1
                            else:
                                r = line.split(',')
                               
                                metricsLog.append(r[0])
                        
                        lfile.close()

                        lout = open(savepath,'w')
                        for i in range(0,len(metricsLog),1):
                            line = [metricsLog[i]]
                            dline = data[i,:].tolist()
                            line.extend(dline)
                            lout.write(str(line).strip("[]") + '\n')

                        lout.write(metric + ',' + str(f) + ',' + str(point) + ',' + str(corAvg) + '\n')
                        lout.close()

                    except Exception as e:
                        lout = open(savepath,'w')
                        lout.write(metric + ',' + str(f) + ',' + str(point) + ',' + str(corAvg) + '\n')
                        lout.close()

                    stocksTried = 0
                    corSum = 0.0
                    tickerTracker = 0

                pointTracker = pointMin
                

            fieldPermTracker = fieldPermMin


def main():
    '''
    Main function; creates a multiprocessing pool of NNOptimizer functions.
    Sets up 3 proccess (4 CPU cores - 1 for OS/other overhead)
    '''
    if __name__ == '__main__':
    	pool = mp.Pool(processes = 3)#ChangeMe!!!
    
    	#pool.apply_async(NNOptimizer, [], dict(runTimeName = 'Part1', shortenProgress = True, PrinterCarriageNumber = 0, startupSleepTime = 0, overideDirectory = 'Data/Part1/'))
        #pool.apply(NNOptimizer, [], dict(runTimeName = 'Part2', shortenProgress = True, PrinterCarriageNumber = 35, startupSleepTime = 1, overideDirectory = 'Data/Part2/')) #delete me l8r
    	#pool.apply_async(NNOptimizer, [], dict(runTimeName = 'Part2', shortenProgress = True, PrinterCarriageNumber = 35, startupSleepTime = 1, overideDirectory = 'Data/Part2/'))
    	
        pool.apply(NNOptimizer, [], dict(runTimeName = 'Part3', shortenProgress = True, PrinterCarriageNumber = 70, startupSleepTime = 2, overideDirectory = 'Data/Part3/'))
    
    	print('\n')


    


#----------------------------------------------------------------------------------------------------------------------------
#Let it be known that joey is a ghetto mother f@cker

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


#----------------------------------------------------------------------------------------------------------------------------

main()
#NNOptimizer(runTimeName = 'Part3', shortenProgress = False, PrinterCarriageNumber = 70, startupSleepTime = 2, overideDirectory = 'Data/Part3/');