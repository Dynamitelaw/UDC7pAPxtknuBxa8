'''
Dynamitelaw
Tests and optimizes the NearestNeighbor Algorithm.
'''


import numpy as np
import sys
import os
import NearestNeighborBackend as knb
from scipy import stats
import warnings
import time


def NearestNeighborTester(ticker,bs,fields, daterange = None, points = 5, distanceMetric = 'seuclidean', sampleLog = False, ignoreWarnings = True, progressHeader = '', dayBackValue = 0):
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
    '''

    try:
        #Generates data set of stock
        dataSet = knb.GenerateNearestData(ticker,bs, fields, daterange, OutputMultiple = False, includeOptimalDates = True)
        dataPoints = dataSet[0]
        outputs = dataSet[1]
        optimals = dataSet[2]

        k = int(dataPoints.shape[0])    #size of data set
        if (k > 251):
            wheel = ["/","--","\ ","|"]
            predictionSet = np.zeros(k)    #NN predictions
            for i in range(0,k-250,1):
                #Progress Bar
                sys.stdout.write('\r')
                sys.stdout.write(progressHeader + 'Procressing ' + ticker + ' ' + str((100*i)/(k-250)) + '%  ' + wheel[(i/15)%4])
                sys.stdout.flush()

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
                        prediction = knb.NearestPredict(sourcePoint, historicalDataInput, hOutputs, points, distanceMetric)        #predicts output
                        predictionSet[i] = prediction
                else:
                    prediction = knb.NearestPredict(sourcePoint, historicalDataInput, hOutputs, points, distanceMetric)        #predicts output
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

            #Clear Progress bar
            sys.stdout.flush()
            sys.stdout.write('\r')
            sys.stdout.write('                                                                     ')
            sys.stdout.flush()
            sys.stdout.write('\r')

            return correlation
        else:
            return -2
    except Exception as e:
        return -2
        pass


def NNOptimizer():
    '''
    Finds the best NearestPredict settings that lead to the highest correlation.
    Returns best settings as a list, of format [distanceMetric, [fields], points, average correlation coefficient].
    Prints best settings to a txt file.
    Keeps track of where in the procressing it left off, allowing you to split up the Procressing among different sessions.
    NNOptimizerSettings.txt alows you to define the optimization ranges, in order to run multiple concurrent instances.
    '''

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        print('Initializing optimizer...\n')

        pfields = ['Open', 'Volume', '2 Day Slope', '5 Day Slope', 'Standard Dev', '2 Day Momentum', '5 Day Momentum', '2D Discrete Moementum', '5D Discrete Moementum']
        pmetrics = ['braycurtis','canberra','chebyshev','cityblock','correlation','cosine','dice','euclidean','hamming','jaccard','kulsinski','mahalanobis','matching','minkowski','rogerstanimoto','russellrao','seuclidean','sokalmichener','sokalsneath','sqeuclidean','wminkowski','yule']


        try:    #tries to load checkpoint
            path = 'NNOptimizerCheckpoint.txt'
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
                path = 'NNOptimizerSettings.txt'
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
                print ('Error: "NNOptimizerSettings.txt" failed to load \nGenerated default settings file and guide file')

                path = 'NNOptimizerSettings.txt'
                sfile = open(path,'w')
                sfile.write(str(0) + '\n' + str(21) + '\n' + str(1) + '\n' + str(511) + '\n' + str(1) + '\n' + str(220) + '\n' + str(1))
                sfile.close()

                path = 'NNOSettingsGuide.txt'
                sfile = open(path,'w')
                header = "Possible Distance Metrics = ['braycurtis','canberra','chebyshev','cityblock','correlation','cosine','dice','euclidean',\n    'hamming','jaccard','kulsinski','mahalanobis','matching','minkowski','rogerstanimoto','russellrao',\n    'seuclidean','sokalmichener','sokalsneath','sqeuclidean','wminkowski','yule']"
                header = header + "\nPossible Fields = ['Open', 'Volume', '2 Day Slope', '5 Day Slope', 'Standard Dev', '2 Day Momentum', '5 Day Momentum', '2D Discrete Moementum', '5D Discrete Moementum']"
                header = header + '\n---------------------------------------------------------------------------------------------------------------------------'
                sfile.write(header + '\nMetricMin D[0,21]\nMetricMax D[0,21]\nFieldCombinationMin D[1,511]\nFieldCombinationMax D[1,511]\nPointMin D[1,220]\nPointMax D[1,220]\nPointStep D[1,219]')
                sfile.close()

                print(e)
                return


        print('M = ' + str(metricTracker) + '| F = ' + str(fieldPermTracker) + '| P = ' + str(pointTracker) + '| T = ' + str(tickerTracker) + '\n')

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
                    percentComplete = int((1000.0/float(metricMax - metricMin + 1))*((m-metricMin) + (float(f - fieldPermMin)/(fieldPermMax - fieldPermMin + 1)) + (float(point - pointMin)/((pointMax - pointMin + 1)*(fieldPermMax - fieldPermMin + 1)))))/10.0
                    header = str(percentComplete) + '%_' + metric + '|f(' + str(fieldPermTracker) + '/' + str(fieldPermMax) + ')-p(' + str(point) + '/' + str(pointMax) + '): '
                    
                    tickerlist = os.listdir('Data/PcsData/')
                    for tickIndx in range(tickerTracker,len(tickerlist),1):    #tries every stock    
                        try:
                            corCoef = NearestNeighborTester(tickerlist[tickIndx],'ps',cfields,sampleLog = False, distanceMetric = metric, points = point, progressHeader = header)
                            if (corCoef != -2):
                                corSum += corCoef
                                stocksTried += 1

                        except Exception as e:
                            pass

                        if (((tickIndx % 45) == 0) and (tickIndx != 0)):    #updates checkpoint every 45 stocks processed (~every 15 min)
                            savepath = 'NNOptimizerCheckpoint.txt'
                            cout = open(savepath,'w')
                            cout.write(str(metricMin) + '\n' + str(m) + '\n' + str(metricMax) + '\n' + str(fieldPermMin) + '\n' + str(f) + '\n' + str(fieldPermMax) + '\n' + str(pointMin) + '\n' + str(point) + '\n' + str(pointMax) + '\n' + str(pointStep) + '\n' + str(maxCor) + '\n' + str(tickIndx) + '\n' + str(stocksTried) + '\n' + str(corSum))
                            cout.close() 

                    corAvg = corSum / stocksTried

                    if (abs(corAvg) > maxCor):    #saves argument settings if average coefficient is better than past max
                        maxCor = abs(corAvg)
                        savepath = 'NNOptimizerMax.txt'
                        fout = open(savepath,'w')
                        fout.write(metric + '\n' + str(cfields) + '\n' + str(point) + '\n' + str(corAvg))
                        fout.close() 

                    #updates log
                    savepath = 'NNOptimizerMaxLog.csv'
                    lout = open(savepath,'rw')
                    lout.write(metric + ',' + str(cfields) + ',' + str(point) + ',' + str(corAvg) + '\n')
                    lout.close()

                    stocksTried = 0
                    corSum = 0.0
                    tickerTracker = 0

                pointTracker = pointMin
                

            fieldPermTracker = fieldPermMin



#----------------------------------------------------------------------------------------------------------------------------

NNOptimizer()
#print('Hello World')
print('Optimization Complete!')
print('Close out of program? (y/n)')
answer = raw_input()
print('K,bye!')
time.sleep(1)