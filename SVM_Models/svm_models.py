'''
IlPesce
Contains methods for training SVM models and gathering stats
on their accuracy.
'''

import pandas as pd
import math
import numpy as np
import sklearn
from sklearn import svm,preprocessing
from sklearn.svm import SVC
from matplotlib import pyplot as plt
import os
from utils import emitAsciiBell
import random
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import GridSearchCV
from datetime import date

def createSVMmodel(dir="Data/SVM/1PercentGrowth3DaysAway/",training_percent=.3,c=1,kernel="rbf",gamma=.1,date_range=None):
    '''Creates and trains a SVM model from data in the dir directory. Takes training_percent
    as an argument denoting how much of the data is to be used for training the model. 
    training_percent should be a float less than 1 i.e. for 30% training_percent=.3.
    Returns model,accuracy
    '''

    data_df = getTrainingDataFrame(dir,date_range=None)
        
    df = sklearn.utils.shuffle(data_df)

    X = np.array(df.drop(columns=["Result","Percent Results"]).values)
    X = preprocessing.scale(X)
    y = df["Result"].values
    p_res = df["Percent Results"].values
    
    train_index = int(len(df.index.tolist())*training_percent)
    trainingDataX = X[0:train_index]
    testingDataX = X[train_index:]
    trainingDataY = y[0:train_index]
    testingDataY = y[train_index:]
    testing_p_res = p_res[train_index:]

    clf = svm.SVC(kernel=kernel, C=c,gamma=gamma)
    clf.fit(trainingDataX,trainingDataY)
    correct_count = 0

    results = clf.predict(testingDataX)
    buy_count = 0
    corr_buy = 0
    k = 1.0
    for x in range(0, len(results)):
        if results[x] == 1:
            buy_count+= 1
            k *= (1+testing_p_res[x])
            if testingDataY[x]==1:
                corr_buy+=1
        if results[x] == testingDataY[x]:
            correct_count += 1
    return clf , correct_count/len(results),corr_buy,k,len(results),np.array(df.drop(columns=["Result","Percent Results"]).values)

def getTrainingDataFrame(dir,date_range=None):
        #Ensuring that the data path exists
    if not os.path.isdir(dir):
        print("Invalid data directory")
        return
    tickers = []
    for root,dirs,files in os.walk(dir):
            for f in files[0:100]:
                tickers.append(f)
    path = os.path.join(dir,tickers[0])
    data_df = pd.DataFrame.from_csv(path)
    #data_df.index.name = 'date'
    #data_df['date'] = pd.to_datetime(data_df['date'])
    if date_range!=None and len(date_range)==2:
        mask = (data_df['date'] > date_range[0]) & (data_df['date'] <= date_range[1])
        data_df = data_df.loc[mask] 
    for ticker in tickers:
        try:
            temp_df = pd.DataFrame.from_csv(os.path.join(dir,ticker))
            data_df.append(temp_df)
        except:
            pass
    return data_df

def logSearchParams(dir="Data/SVM/1PercentGrowth1DaysAway/",training_percent=.3):
    data_df = getTrainingDataFrame(dir)
    df = sklearn.utils.shuffle(data_df)

    X = np.array(df.drop(columns=["Result","Percent Results"]).values)
    X = preprocessing.scale(X)
    y = df["Result"].values
    C_range = np.logspace(-2, 10, 5)
    gamma_range = np.logspace(-9, 3, 5)
    param_grid = dict(gamma=gamma_range, C=C_range)
    cv = StratifiedShuffleSplit(n_splits=5, test_size=0.2, random_state=42)
    grid = GridSearchCV(SVC(), param_grid=param_grid, cv=cv)
    grid.fit(X, y)
    
    print("The best parameters are %s with a score of %0.2f"
      % (grid.best_params_, grid.best_score_))

    f = open("bestGridParams.txt",w)
    f.write("The best parameters are %s with a score of %0.2f"
      % (grid.best_params_, grid.best_score_))
    f.close()
    return grid.best_params_

#c=1000000000.0,gamma=1e-07
def testParams(dir,c,gamma,sample_size=10,training_percent=.3,date_range=None):
    
    accArray = []
    corr_buy_array = []
    k_arr = []
    day_arr = []

    for i in range(sample_size):
        model,accuracy,corr_buy,k,days,a = createSVMmodel(dir,c=c,gamma=gamma,training_percent=training_percent,date_range=date_range)
        accArray.append(accuracy)
        corr_buy_array.append(corr_buy)
        k_arr.append(k)
        day_arr.append(days)
    
    interest = lambda d: math.pow(float(np.mean(k_arr)),(1/(float(np.mean(day_arr))/d)))

    print("Mean Accuracy: {}".format(np.mean(accArray)))
    print("Standard Dev Acc: {}".format(np.std(accArray)))
    print("Mean CorrectBuys: {}".format(np.mean(corr_buy_array)))
    print("Standard Dev CorrectBuys: {}".format(np.std(corr_buy_array)))
    print("Mean K: {}".format(np.mean(k_arr)))
    print("Standard Dev K: {}".format(np.std(k_arr)))
    print("Mean Days: {}".format(np.mean(day_arr)))
    print("Standard Dev Days: {}".format(np.std(day_arr)))
    print("Equ. annual interest: {}".format(interest(250)))
    print("Equ. monthly interest: {}".format(interest(7)))
    print("Equ. daily interest {}".format(interest(1)))

    plt.hist(k_arr)
    plt.show()



if __name__=="__main__":
    dir="Data/SVM/1PercentGrowth3DaysAway/"
    logSearchParams(dir="Data/SVM/1PercentGrowth3DaysAway/",training_percent=.3)
    emitAsciiBell()
    #testParams(dir=dir,c=100,gamma=.1,sample_size=100,training_percent=.3,date_range=[date(2013,1,1),date(2016,1,1)])

    
    
