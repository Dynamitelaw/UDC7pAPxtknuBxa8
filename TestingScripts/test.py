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
	model.add(Dense(60, input_dim=3, kernel_initializer='normal', activation='relu'))
	model.add(Dense(1, kernel_initializer='normal', activation='sigmoid'))
	# Compile model
	model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
	return model


if __name__ == '__main__':
    #=================================================
    #Generate two random groups for NN validation
    #=================================================
    #3D Sphereical group definitions
    AClusterCenter = [0,0,0]
    AClusterRadius = 57

    BClusterCenter = [28,28,28]
    BClusterRadius = 57

    #Generate Random datapoints that belong to each group
    datapointsPerCluster =300

    #A Cluster
    datapointsInA = 0
    Acluster = []
    while True:
        #Create random coordinate
        x = uniform(AClusterCenter[0]-AClusterRadius, AClusterCenter[0]+AClusterRadius)
        y = uniform(AClusterCenter[1]-AClusterRadius, AClusterCenter[1]+AClusterRadius)
        z = uniform(AClusterCenter[2]-AClusterRadius, AClusterCenter[2]+AClusterRadius)

        #Check to make sure coordinate is inside defined cluster
        xDistance = x - AClusterCenter[0]
        yDistance = y - AClusterCenter[1]
        zDistance = z - AClusterCenter[2]

        distanceFromCenterSquared = zDistance**2 + yDistance**2 + xDistance**2
        if (distanceFromCenterSquared <= (AClusterRadius**2)):
            #If inside cluster boundary, add point to cluster
            Acluster.append((x,y,z,1))
            datapointsInA += 1
            if (datapointsInA == datapointsPerCluster):
                #Break if enough datapoints have been collected
                break

    #B Cluster
    datapointsInB = 0
    Bcluster = []
    while True:
        #Create random coordinate
        x = uniform(BClusterCenter[0]-BClusterRadius, BClusterCenter[0]+BClusterRadius)
        y = uniform(BClusterCenter[1]-BClusterRadius, BClusterCenter[1]+BClusterRadius)
        z = uniform(BClusterCenter[2]-BClusterRadius, BClusterCenter[2]+BClusterRadius)

        #Check to make sure coordinate is inside defined cluster
        xDistance = x - BClusterCenter[0]
        yDistance = y - BClusterCenter[1]
        zDistance = z - BClusterCenter[2]

        distanceFromCenterSquared = zDistance**2 + yDistance**2 + xDistance**2
        if (distanceFromCenterSquared <= (BClusterRadius**2)):
            #If inside cluster boundary, add point to cluster
            Bcluster.append((x,y,z,0))
            datapointsInB += 1
            if (datapointsInB == datapointsPerCluster):
                #Break if enough datapoints have been collected
                break


    #Plot clusters to check if we did everything right
    fig = pyplot.figure()
    ax = Axes3D(fig)

    A_x_vals = [i[0] for i in Acluster]
    A_y_vals = [i[1] for i in Acluster]
    A_z_vals = [i[2] for i in Acluster]
    ax.scatter(A_x_vals, A_y_vals, A_z_vals, c = "orange")

    B_x_vals = [i[0] for i in Bcluster]
    B_y_vals = [i[1] for i in Bcluster]
    B_z_vals = [i[2] for i in Bcluster]
    ax.scatter(B_x_vals, B_y_vals, B_z_vals, c = "blue")

    pyplot.show()

    #=================================================
    #Train NN to classify between the two clusters
    #=================================================

    #Prepare data
    allDataPoints = []
    allDataPoints += Acluster
    allDataPoints += Bcluster

    shuffle(allDataPoints)

    X = [list(i[0:3]) for i in allDataPoints]
    Y = [i[3] for i in allDataPoints]
    
    #Create and train NN model
    # seed = 7
    # kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)

    # Evaluate model using standardized dataset. 
    # https://www.kaggle.com/parthsuresh/binary-classifier-using-keras-97-98-accuracy
    estimators = []
    estimators.append(('standardize', StandardScaler()))
    estimators.append(('mlp', KerasClassifier(build_fn=create_baseline, epochs=25, batch_size=5, verbose=0)))
    pipeline = Pipeline(estimators)
    kfold = StratifiedKFold(n_splits=10, shuffle=True)
    results = cross_val_score(pipeline, X, Y, cv=kfold)
    print("Results: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))






    