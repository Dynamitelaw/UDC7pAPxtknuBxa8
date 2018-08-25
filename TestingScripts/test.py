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


# baseline model
def create_baseline():
    # create model
    model = Sequential()
    model.add(Dense(7, input_dim=7, kernel_initializer='normal', activation='relu'))
    model.add(Dense(30, kernel_initializer='normal', activation='relu'))
    model.add(Dense(20, kernel_initializer='normal', activation='relu'))
    model.add(Dense(10, kernel_initializer='normal', activation='relu'))
    model.add(Dense(1, kernel_initializer='normal', activation='sigmoid'))
    # Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


def addDatapointsFromStock(ticker):
    DataPoints = []

    try:
        stockData = database.getDataframe(ticker, dataFields=["2 Day Normalized Slope", "5 Day Normalized Slope", "2 Day Normalized Momentum", "5 Day Normalized Momentum", "2D Discrete Moementum", "5D Discrete Moementum", "Standard Dev Normalized", "Profit Speed"], dateRange=["2010-01-01", "2016-06-06"])
        stockData.dropna(inplace = True)  #Remove any rows with missing data

        #Seperate dataframe into Positive profit speeds and negative profit speeds
        positiveProfitSpeedDframe = stockData[stockData.apply(lambda row: row["Profit Speed"] > 0, axis=1)]
        negativeProfitSpeedDframe = stockData[stockData.apply(lambda row: row["Profit Speed"] <= 0, axis=1)]
        
        #Make sure datapoints are equally distributed between positive and negative profit speeds
        numberOfPositives = len(positiveProfitSpeedDframe)
        numberOfNegatives = len(negativeProfitSpeedDframe)

        if (numberOfPositives > numberOfNegatives):
            positiveProfitSpeedDframe = positiveProfitSpeedDframe.iloc[0:numberOfNegatives]
        elif (numberOfNegatives > numberOfPositives):
            negativeProfitSpeedDframe = negativeProfitSpeedDframe.iloc[0:numberOfPositives]

        positiveDataList = list(positiveProfitSpeedDframe.values)
        negativeDataList = list(negativeProfitSpeedDframe.values)
        
        DataPoints += positiveDataList
        DataPoints += negativeDataList
        
        return DataPoints

    except Exception as e:
        #print(e)
        return False


if __name__ == '__main__':
    #Populate datapoints list
    numberOfStocks = 10
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

    X = [i[0:7] for i in allDataPoints]
    Y = [int(i[7] > 0) for i in allDataPoints]

    
    # Evaluate model using standardized dataset. 
    # https://www.kaggle.com/parthsuresh/binary-classifier-using-keras-97-98-accuracy

    epochs = 25

    print("\n===================================")
    print("Evaluating network...")

    avgTrainingTimePerDatapoint = 0.374
    eta = int((len(allDataPoints) * epochs * avgTrainingTimePerDatapoint)/1000)
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

    print("Results: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))

    trainingTimePerDatapoint = (1000*(endTime - startTime)) / (len(allDataPoints)*epochs)
    print ("Total training time: " + time.strftime('%H:%M:%S', time.gmtime(endTime - startTime)))
    print("Training time per datapoint (per epoch): " + str(trainingTimePerDatapoint) + " ms")
    
    






    