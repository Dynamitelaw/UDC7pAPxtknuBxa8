'''
Dynamitelaw
The first level nueral network model. The first level is split into 2 networks, one for buy values, and one for sell values.
Script [will] include the model layout, training functions, testing functions, and running functions.
Uses TFLearn as tensorflow API
'''


import tflearn
import numpy as np
from GenerateTrainingData import GenerateIO 
import os
import time


hm_epochs = 1
tfields = ['Open', 'Volume', '2 Day Slope', '5 Day Slope']
tratio = 0.1		#ratio of testing to training

'''
# Neural Network Model Setup (regression)
inlayer = tflearn.layers.core.input_data(shape=[90,len(fields)])
layer1 = tflearn.layers.core.fully_connected(inlayer,1500)
layer2 = tflearn.layers.core.fully_connected(layer1,750)
layer3 = tflearn.layers.core.fully_connected(layer2,50)
layer4 = tflearn.layers.core.fully_connected(layer3,10)
layer5 = tflearn.layers.core.fully_connected(layer4,1)		#final layer needs to be only one neuron wide for regression to work
linear = tflearn.single_unit(layer5)
regression = tflearn.layers.estimator.regression(linear, optimizer='adam', loss='mean_square', learning_rate=0.003)
m = tflearn.DNN(regression)
'''

# Neural Network Model Setup (categorical)
net = tflearn.layers.core.input_data(shape=[90,len(tfields)])
net = tflearn.layers.core.fully_connected(net,1500, activation = 'relu')
net = tflearn.layers.core.fully_connected(net,1500, activation = 'relu')
net = tflearn.layers.core.fully_connected(net,500, activation = 'relu')
net = tflearn.layers.core.fully_connected(net,50, activation = 'relu')
net = tflearn.layers.core.dropout(net,0.8)
net = tflearn.layers.core.fully_connected(net,5, activation = 'softmax')		
#net = tflearn.single_unit(net)
net = tflearn.layers.estimator.regression(net, optimizer='adam', loss='categorical_crossentropy', learning_rate=0.003)
m = tflearn.DNN(net)


#Training the Model 
startTime = time.time()
tickerlist = os.listdir('Data/PcsData/')       #obtains list of all processed stock files
k = len(tickerlist)
rand = np.random.random((k))
tickertrain = []       #list of training tickers
tickertest = []        #list of testing tickers

indx = 0
for r in rand:      #randomly splits tickers into training and testing lists
	if r < tratio:
		tickertest.append(tickerlist[indx])
	else:
		tickertrain.append(tickerlist[indx])
	indx += 1

tickertrain = tickertrain[0:100]
count = 0
breaks = 0 
for ticker in tickertrain:       #each batch is the IO for one of the training tickers
	count += 1
	try:
		stocktrain = GenerateIO(ticker, 'b', normalize = True, categorical = True, fields = tfields, daterange = None)
		X = stocktrain[0]
		Y = stocktrain[1]
		m.fit(X, Y, n_epoch=hm_epochs, show_metric=True, run_id = 'linear test', snapshot_epoch=False)		#TFLearn training function
	except Exception as e:
		print(e)
		print ('Stock Number: ' + str(count))
		print (ticker)
		breaks += 1
		pass


m.save('networkL1B.tflearn')		#saves the model weights

print ('__________________________________')
runtime = time.time() - startTime
if runtime < 60:
	print ('Runtime -> Seconds: ' + str(runtime))
if runtime >= 60 and runtime <3600:
	print ('Runtime -> Minutes: ' + str(runtime/60))
if runtime >= 3600:
	print ('Runtime -> Hours: ' + str(runtime/3600))

print ('')
print (str(count) + ' stocks tried')
print (str(breaks) + 'stocks failed')
print ('__________________________________')

#-----------------------------------------------------------------------------------------------
