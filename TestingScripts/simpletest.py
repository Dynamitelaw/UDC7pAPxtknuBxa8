import pandas as pd
import numpy as np
import os
from sklearn import svm, preprocessing
import random
from matplotlib import pyplot as plt
from scipy import stats

def createDataFrame(dataDir="Data/StockData"):
    for root,dir,file in os.walk(dataDir):
        for f in file:
            try:
                ticker = f.rstrip(".csv")
                df = pd.DataFrame.from_csv("Data/StockData/"+f)
                Dates = df.index.tolist()
                addData = []
                for j in range (1,5):
                    addData.append([])
                    for k in range(0,j):
                        addData[j-1].append(None)
                    for k in range (j,len(df.index)):
                        val2 = df.at[Dates[k-j],"Close"]
                        val1 = df.at[Dates[k-1],"Open"]
                        addData[j-1].append((val2-val1)/val1)
                    df["PercentChange"+str(j)+"Day"] = addData[j-1]
                df.to_csv("Data/AdjData/"+f)
            except:
                pass
    
def convertBinary(dataDir="Data/AdjData"):
        for root,dir,file in os.walk(dataDir):
            for f in file:
                try:
                    ticker = f.rstrip(".csv")
                    filestring = "Data/AdjData/"+f
                    df = pd.DataFrame.from_csv(filestring)
                    Dates = df.index.tolist()
                    for j in range (1,5):
                        for k in range(0,len(Dates)):
                            percentVal = float(df.at[Dates[k],"PercentChange"+str(j)+"Day"])
                            if percentVal>.01:
                                df.at[Dates[k],"PercentChange"+str(j)+"Day"] = 1
                            else:
                                df.at[Dates[k],"PercentChange"+str(j)+"Day"] = 0
                    df.drop(Dates[0:6])
                    df.to_csv("Data/BinData/"+f)
                except Exception as e:
                    print(e)
                    pass

def Build_Data_Set():
    tickers = []
    for root,dir,file in os.walk("Data/BinData"):
            for f in file:
                tickers.append(f)
    randTickers = np.random.shuffle(tickers)
    data_df = pd.DataFrame.from_csv("Data/BinData/"+tickers[0])
    for ticker in tickers[1:100]:
        try:
            temp_df = pd.DataFrame.from_csv("Data/BinData/"+ticker)
            data_df.append(temp_df)
        except:
            pass

    population = data_df["PercentChange1Day"]
    sum = np.sum(population)
    total = len(population)



    #data_df = data_df[:100]
    data_df = data_df.reindex(np.random.permutation(data_df.index))
    X = np.array(data_df[["Open","High","Low","Close","Volume","Adj Close"]].values)#.tolist())

    y = (data_df["PercentChange1Day"]
         .values)

    X = preprocessing.scale(X)

    return X,y,sum/total

def Analysis():

   
    X, y, popStat = Build_Data_Set()
    #print(len(X))
    test_size = int(len(X)*.3)
    
    clf = svm.SVC(kernel="linear", C=1.0)
    clf.fit(X[:-test_size],y[:-test_size])
    correct_count = 0

    results = clf.predict(X[(-test_size-1):])

    for x in range(0, test_size):
        if results[0] == y[-x]:
            correct_count += 1

    #print("Accuracy:", (correct_count/test_size) * 100.00)
    return (correct_count/test_size) * 100.00, popStat, clf

def getStats():
    results = np.array([])
    popStats = np.array([])

    for x in range(1,100):
        r1,r2,model = Analysis()
        results = np.append(results,[r1])
        popStats = np.append(popStats,[r2])



    print("Stats")
    print("Mean",np.mean(results))
    print("ST Dev",np.std(results))

    print("pStats")
    print("pMean",np.mean(popStats))
    print("pST Dev",np.std(popStats))

def testModel():
    tickerList = []
    totalDays = 0
    for root,dirs,files in os.walk("Data/AdjData"):
        for f in files:
            tickerList.append(f)
    random.shuffle(tickerList)
    stat,popStat,model = Analysis()
    while stat<.6:
        stat,popStat,model = Analysis()

    balance = 10000.0
    k = 1
    for f in tickerList[0:1]:
        df = pd.DataFrame.from_csv("Data/AdjData/"+f)
        X = np.array(df[["Open","High","Low","Close","Volume","Adj Close"]].values)#.tolist())
        X = preprocessing.scale(X)
        y = (df["PercentChange1Day"].values)
        for i in range(1,len(X)):
            result = model.predict([X[i]])
            totalDays+=1
            if int(result[0]) == 1:
                #print(1+y[i])
                try:
                    balance *= (1+y[i])
                    k *= (1+y[i])
                except:
                    pass
    return balance,k,totalDays
    
def getModelStats(sample_size=200):
    balanceArray = np.array([])
    kArray = np.array([])
    totalDaysArray = np.array([])

    for i in range(0,sample_size):
        try:
            b,k,t = testModel()
        except:
            pass
        balanceArray = np.append(balanceArray,b)
        kArray = np.append(kArray,k)
        totalDaysArray = np.append(totalDaysArray,t)
    balanceArray.tofile("BalanceArray")
    
    print("Stats")
    print("Balance Mean: ",np.mean(balanceArray))
    print("Balane Mode: ",stats.mode(balanceArray))
    print("Balance Median",np.median(balanceArray))
    print("Balance Std: ",np.std(balanceArray))
    print("k Mean: ",np.mean(kArray))
    print("k Median: ",np.median(kArray))
    print("k Mode: ",stats.mode(kArray))
    print("k Std: ",np.std(kArray))
    print("Total Days Avg: ",np.mean(totalDaysArray))

    plt.hist(kArray,bins=list(range(0,100,1)))
    plt.show()


if __name__ == "__main__":
    getModelStats()

    
