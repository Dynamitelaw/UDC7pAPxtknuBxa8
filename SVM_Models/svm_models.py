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
import random
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import GridSearchCV
from datetime import date

def createSVMmodel(date_range,dir="Data/SVM/1PercentGrowth3DaysAway/",customTickers=None,c=1,kernel="rbf",gamma=.1):
    '''Creates and trains a SVM model from data in the dir directory. Takes training_percent
    as an argument denoting how much of the data is to be used for training the model. 
    training_percent should be a float less than 1 i.e. for 30% training_percent=.3.
    Returns model,accuracy
    '''

    training_data_df = getTrainingDataFrame(dir,date_range=[date(2013,9,2),date_range[0]],customTickers=customTickers)
    testing_data_df  = getTrainingDataFrame(dir,date_range=[date_range[0],date_range[1]],customTickers=customTickers) 

    X = np.array(training_data_df.drop(columns=["Result","Percent Results"]).values)
    X = preprocessing.scale(X)
    y = training_data_df["Result"].values
    
    X_test = np.array(testing_data_df.drop(columns=["Result","Percent Results"]).values)
    X_test = preprocessing.scale(X_test)
    y_test = testing_data_df["Result"].values
    
    p_res_test = testing_data_df["Percent Results"].values
    
    
    trainingDataX = X[:]
    testingDataX = X_test[:]
    trainingDataY = y[:]
    testingDataY = y_test[:]
    testing_p_res = p_res_test[:]

    clf = svm.SVC(kernel=kernel, C=c,gamma=gamma)
    clf.fit(trainingDataX,trainingDataY)
    correct_count = 0

    results = clf.predict(testingDataX)
    buy_count = 0
    corr_buy = 0
    k = 1.0
    for x in range(len(results)):
        if results[x] == 1:
            buy_count+= 1
            k *= (1+testing_p_res[x])
            if testingDataY[x]==1:
                corr_buy+=1
        if results[x] == testingDataY[x]:
            correct_count += 1
    return clf , correct_count/len(results),corr_buy,k,len(results),np.array(training_data_df.drop(columns=["Result","Percent Results"]).values)

def getTrainingDataFrame(dir,date_range=None,customTickers=None):
        #Ensuring that the data path exists
    if not os.path.isdir(dir):
        print("Invalid data directory")
        return
    
    if customTickers == None:
        tickers = []
        for root,dirs,files in os.walk(dir):
                for f in files[0:100]:
                    tickers.append(f)
    else:
        tickers = customTickers[:]
        for i in range(len(tickers)):
            tickers[i] = tickers[i]+".csv"
    path = os.path.join(dir,tickers[0])
    data_df = pd.DataFrame.from_csv(path)
    # data_df.index.name = 'date'
    # data_df['date'] = pd.to_datetime(data_df['date'])
    if date_range!=None and len(date_range)==2:
        data_df = data_df.loc[date_range[0]:date_range[1]] 
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
    C_range = np.logspace(-2, 10, 13)
    gamma_range = np.logspace(-9, 3, 13)
    param_grid = dict(gamma=gamma_range, C=C_range)
    cv = StratifiedShuffleSplit(n_splits=5, test_size=0.2, random_state=42)
    grid = GridSearchCV(SVC(), param_grid=param_grid, cv=cv)
    grid.fit(X, y)
    
    print("The best parameters are %s with a score of %0.2f"
      % (grid.best_params_, grid.best_score_))

    f = open("bestGridParams.txt",'w')
    f.write("The best parameters are %s with a score of %0.2f"
      % (grid.best_params_, grid.best_score_))
    f.close()
    return grid.best_params_

#c=1000000000.0,gamma=1e-07
def testParams(dir,c,gamma,sample_size=10,date_range=None,customTickers=None):
    
    accArray = []
    corr_buy_array = []
    k_arr = []
    day_arr = []

    for i in range(sample_size):
        model,accuracy,corr_buy,k,days,a = createSVMmodel(dir=dir,c=c,gamma=gamma,date_range=date_range,customTickers=customTickers)
        accArray.append(accuracy)
        corr_buy_array.append(corr_buy)
        k_arr.append(k)
        day_arr.append(days)
    
    interest = lambda d: math.pow(float(np.mean(k_arr)),(1/(float(np.mean(day_arr))/d)))

    # print("Mean Accuracy: {}".format(np.mean(accArray)))
    # print("Standard Dev Acc: {}".format(np.std(accArray)))
    # print("Mean CorrectBuys: {}".format(np.mean(corr_buy_array)))
    # print("Standard Dev CorrectBuys: {}".format(np.std(corr_buy_array)))
    # print("Mean K: {}".format(np.mean(k_arr)))
    # print("Standard Dev K: {}".format(np.std(k_arr)))
    # print("Mean Days: {}".format(np.mean(day_arr)))
    # print("Standard Dev Days: {}".format(np.std(day_arr)))
    # print("Equ. annual interest: {}".format(interest(250)))
    # print("Equ. monthly interest: {}".format(interest(7)))
    # print("Equ. daily interest {}".format(interest(1)))


    return interest(250)
    # plt.hist(k_arr)
    # plt.show()


def createSlopesSVMmodel(dir="Data/SVM/5day_vs_2day_vs_Profit Speed/",c=1,kernel="rbf",gamma=.1):
    '''
    Creates an SVM model for finding surface for profitable region of the heatmap in meh_selector
    Takes path to training data as input. Test output in the "Result" Column
    '''

    if not os.path.isdir(dir):
        print("Invalid data directory")
        return

    #Collects all data into memory
    df = pd.DataFrame()
    for root, dirs,files in os.walk(dir):
        for f in files:
            stock_df = pd.DataFrame.from_csv(os.path.join(dir,f))
            df = df.append(stock_df)

    df = sklearn.utils.shuffle(df)
    
    X = np.array(df.drop(columns=["Result"]).values)
    y = np.array(df["Result"].values)


    #Separates the data into training and testing data
    training_index = int(len(X)*.7)

    trainingDataX = X[0:training_index]
    trainingDataY = y[0:training_index]
    testingDataX = X[training_index:]
    testingDataY = y[training_index:]

    #Creates and trains model
    clf = svm.SVC(kernel=kernel, C=c,gamma=gamma)
    clf.fit(trainingDataX,trainingDataY)

    #Gets prediction results
    results = clf.predict(testingDataX)

    correct_count = 0

    #Gets accuracy
    for i in range(len(results)):
        if results[i] == testingDataY[i]:
            correct_count+=1
    
    print(correct_count/len(results))

    return clf, correct_count/len(results)









if __name__=="__main__":
    
    createSlopesSVMmodel()
    
    
    
    
    # dir="Data/SVM/1PercentGrowth3DaysAway/"
    # k_max=0
    # c_max=0
    # gamma_max=0
    # #logSearchParams(dir="Data/SVM/1PercentGrowth3DaysAway/",training_percent=.3)
    # for i in range(-10,11):
    #     for j in range(-10,11):
    #         k = testParams(dir=dir,c=10**j,gamma=10**i,sample_size=1,date_range=[date(2015,1,1),date(2016,1,1)],customTickers=['AAPL'])
    #         if k>k_max:
    #             k_max = k
    #             c_max = 10**j
    #             gamma_max = 10**i
    
    # print("Best K={} at c={},gamma={}".format(k_max,c_max,gamma_max))
    
    
