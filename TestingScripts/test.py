import multiprocessing
from multiprocessing import Pool
import sys
import time
import numpy as np
import os
import pandas as pd
from random import uniform
from random import shuffle
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

sys.path.append("./")
import SystemPathImports
import utils
import PandaDatabase as database

#Global Variables
daysToPass = 15
NNModel = False

# baseline model
def create_baseline():
    # create model
    model = Sequential()
    model.add(Dense(7*daysToPass, input_dim=7*daysToPass, kernel_initializer='normal', activation='relu'))
    model.add(Dense(30, kernel_initializer='normal', activation='relu'))
    model.add(Dense(20, kernel_initializer='normal', activation='relu'))
    model.add(Dense(10, kernel_initializer='normal', activation='relu'))
    model.add(Dense(1, kernel_initializer='normal', activation='sigmoid'))
    # Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    global NNModel
    NNModel = model
    return model


def addDatapointsFromStock(ticker):
    DataPoints = []

    try:
        dataFields = ["2 Day Normalized Slope", "5 Day Normalized Slope", "2 Day Normalized Momentum", "5 Day Normalized Momentum", "2D Discrete Moementum", "5D Discrete Moementum", "Standard Dev Normalized", "Profit Speed"]
        stockData = database.getDataframe(ticker, dataFields= dataFields, dateRange=["2010-01-01", "2016-06-06"])
        stockData.dropna(inplace = True)  #Remove any rows with missing data

        #Create input output pairs based on amount of days to include
        chunks = []
        for i in range(0, len(stockData)-daysToPass, 1):
            chunkFrame = stockData.iloc[i:i+daysToPass]  #chunk is the dataframe containing all the days to include in this datapoint
            chunk = (chunkFrame[dataFields[0:-1]].values.flatten() , float(chunkFrame.iloc[0]["Profit Speed"]))  #extract input data and output profitspeed
            chunks.append(chunk)
            

        #Seperate dataframe into Positive profit speeds and negative profit speeds
        positiveProfitSpeedList = [i for i in chunks if (i[1] > 0)]
        negativeProfitSpeedList = [i for i in chunks if (i[1] <= 0)]
        
        #Make sure datapoints are equally distributed between positive and negative profit speeds
        numberOfPositives = len(positiveProfitSpeedList)
        numberOfNegatives = len(negativeProfitSpeedList)

        if (numberOfPositives > numberOfNegatives):
            positiveProfitSpeedList = positiveProfitSpeedList[0:numberOfNegatives]
        elif (numberOfNegatives > numberOfPositives):
            negativeProfitSpeedList = negativeProfitSpeedList[0:numberOfPositives]
        
        DataPoints += positiveProfitSpeedList
        DataPoints += negativeProfitSpeedList
        
        return DataPoints

    except Exception as e:
        #print(e)
        return False


if __name__ == '__main__':
    #Populate datapoints list
    numberOfStocks = 600
    tickerList = database.getTickerList(randomize=True)[0:numberOfStocks]

    print("Number of stocks for training: " + str(numberOfStocks))
    print("Getting datapoints for training...")
    processCount = multiprocessing.cpu_count() - 1
    processPool = Pool(processCount)

    results = list(processPool.map(addDatapointsFromStock, tickerList))
    processPool.close()
    processPool.join()

    allDataPoints = []
    for dataPoints in results:
        if (dataPoints != False):
            allDataPoints += dataPoints


    print("Number of datapoints: " + str(len(allDataPoints)))

    #=======================================================
    #Train NN to classify between pos and neg Profit speed
    #=======================================================
    
    shuffle(allDataPoints)
    shuffle(allDataPoints)

    X = [i[0] for i in allDataPoints]
    Y = [int(i[1] > 0) for i in allDataPoints]

    
    # Evaluate model using standardized dataset. 
    # https://www.kaggle.com/parthsuresh/binary-classifier-using-keras-97-98-accuracy

    epochs = 100

    print("\n===================================")
    print("Evaluating network...")

    avgTrainingTimePerDatapoint = 0.0012*daysToPass + 0.034
    eta = int((len(allDataPoints) * epochs * avgTrainingTimePerDatapoint)/1000) + 30
    etaString = time.strftime('%H:%M:%S', time.gmtime(eta))
    print("ETA: " + etaString + "\n")

    startTime = time.time()
    estimators = []
    estimators.append(('standardize', StandardScaler()))
    estimators.append(('mlp', KerasClassifier(build_fn=create_baseline, epochs=epochs, batch_size=2000, verbose=0)))
    pipeline = Pipeline(estimators)
    kfold = StratifiedKFold(n_splits=10, shuffle=True)
    results = cross_val_score(pipeline, X, Y, cv=kfold)
    endTime = time.time()

    NNModel.save("Selectors\\Models\\TestModel.h5")

    print("\nResults: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))

    trainingTimePerDatapoint = (1000*(endTime - startTime - 30)) / (len(allDataPoints)*epochs)
    print ("Total training time: " + time.strftime('%H:%M:%S', time.gmtime(endTime - startTime)))
    print("Training time per datapoint (per epoch): " + str(trainingTimePerDatapoint) + " ms")
    
    
    






    