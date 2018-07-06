'''
IlPesce
Contains methods for training SVM models and gathering stats
on their accuracy.
'''

import pandas as pd
import numpy as np
import sklearn
from sklearn import svm,preprocessing
from sklearn.svm import SVC
from matplotlib import pyplot as plt
import os
import random
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import GridSearchCV

def createSVMmodel(dir="Data/SVM/1PercentGrowth1DaysAway/",training_percent=.3,c=1,kernel="rbf",gamma=.1):
    '''Creates and trains a SVM model from data in the dir directory. Takes training_percent
    as an argument denoting how much of the data is to be used for training the model. 
    training_percent should be a float less than 1 i.e. for 30% training_percent=.3.
    Returns model,accuracy
    '''

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
    for ticker in tickers:
        try:
            temp_df = pd.DataFrame.from_csv(os.path.join(dir,ticker))
            data_df.append(temp_df)
        except:
            pass
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
    return clf , correct_count/len(results),X,y


if __name__=="__main__":
    model,accuracy,X,y = createSVMmodel(c=60,gamma=.16)
    
    C_range = np.logspace(-2, 10, 13)
    gamma_range = np.logspace(-9, 3, 13)
    param_grid = dict(gamma=gamma_range, C=C_range)
    cv = StratifiedShuffleSplit(n_splits=5, test_size=0.2, random_state=42)
    grid = GridSearchCV(SVC(), param_grid=param_grid, cv=cv)
    grid.fit(X, y)
    
    print("The best parameters are %s with a score of %0.2f"
      % (grid.best_params_, grid.best_score_))
    
    print(accuracy)