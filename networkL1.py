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
import pyttsx


hm_epochs = 3
batchSize = 100
tfields = ['2 Day Slope', '5 Day Slope', '2 Day Momentum', '5 Day Momentum']
tratio = 0.1		#ratio of testing to training
inputDayLength = 5

# Neural Network Model Setup (regression)
inlayer = tflearn.layers.core.input_data(shape=[inputDayLength,len(tfields)])
layer1 = tflearn.layers.core.fully_connected(inlayer,((inputDayLength % 2) + 1)*len(tfields), activation = 'linear')
layer2 = tflearn.layers.core.fully_connected(layer1,((inputDayLength % 4) + 1)*len(tfields), activation = 'linear')
layer3 = tflearn.layers.core.fully_connected(layer2,((inputDayLength % 16) + 1)*len(tfields), activation = 'linear')
#layer4 = tflearn.layers.core.fully_connected(layer2,10, activation = 'linear')
layer5 = tflearn.layers.core.fully_connected(layer3,1, activation = 'linear')		#final layer needs to be only one neuron wide for regression to work
linear = tflearn.single_unit(layer5)
nOptimizer = tflearn.optimizers.Momentum(learning_rate = 0.003, decay_step = 1000)
regression = tflearn.layers.estimator.regression(linear, optimizer=nOptimizer, loss='mean_square')
m = tflearn.DNN(regression)

'''
# Neural Network Model Setup (categorical)
net = tflearn.layers.core.input_data(shape=[90,len(tfields)])
net = tflearn.layers.core.fully_connected(net,45*len(tfields), activation = 'relu')
net = tflearn.layers.core.fully_connected(net,5*len(tfields), activation = 'relu')
#net = tflearn.layers.core.fully_connected(net,500, activation = 'relu')
#net = tflearn.layers.core.fully_connected(net,50, activation = 'relu')
net = tflearn.layers.core.dropout(net,0.8)
net = tflearn.layers.core.fully_connected(net,5, activation = 'softmax')		
#net = tflearn.single_unit(net)
net = tflearn.layers.estimator.regression(net, optimizer='adam', loss='categorical_crossentropy', learning_rate=0.01)
m = tflearn.DNN(net)
'''

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

tickertrain = tickertrain[0:200]
count = 0
breaks = 0 
for indx in range(0,len(tickertrain),batchSize):       #each batch is the IO for one of the training tickers
	X = []
	Y = []
	for b in range(0,batchSize):
		count += 1
		if ((indx + b < len(tickertrain))):
			try:
				stocktrain = GenerateIO(tickertrain[indx + b], 'ps', normalize = True, categorical = False, fields = tfields, daterange = None, OutputMultiple = 1000, ZeroPruneRatio = False, HistoricalDayLength = inputDayLength)
				if (stocktrain != 0): #if GenerateIO does not throw an error
					for xt in stocktrain[0]:
						X.append(xt)
					for yt in stocktrain[1]:
						Y.append(yt)
					#X.append(stocktrain[0])
					#Y.append(stocktrain[1])
					#m.fit(X, Y, n_epoch=hm_epochs, show_metric=True, run_id = 'linear test', snapshot_epoch=False)		#TFLearn training function
				print("Count:" + str(count) + " out of " + str(len(tickertrain)))
			except Exception as e:
				print(e)
				print ('Stock Number: ' + str(count))
				#print (ticker)
				breaks += 1
				pass
	m.fit(X, Y, n_epoch=hm_epochs, show_metric=True, run_id = 'linear test', snapshot_epoch=False)		#TFLearn training function


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
'''
#Outputing Test Validation Data
m.load('networkL1B.tflearn')

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

'''
categoricaltrain = False

stocktrain = GenerateIO(tickertest[0], 'ps', normalize = True, categorical = False, fields = tfields, daterange = None, OutputMultiple = 1000, ZeroPruneRatio = False, HistoricalDayLength = inputDayLength)
X = stocktrain[0]
Y = stocktrain[1]

predictions = m.predict(X)

savepath = 'netL1OutSample.csv'
fout = open(savepath,'w')
if categoricaltrain:
	for i in range(0,len(predictions)):
		netout = predictions[i]
		outmax = np.amax(netout)

		'''
		if (netout[0] == outmax):
			outprint = 0
		if (netout[1] == outmax):
			outprint = 1
		if (netout[2] == outmax):
			outprint = 5
		if (netout[3] == outmax):
			outprint = 8
		if (netout[4] == outmax):
			outprint = 10
		'''
		outprint = (netout[1] * 1) + (netout[2]*5) + (netout[3]*8) + (netout[4]*10)
		fout.write(str(outprint) + "," + str(Y[i]) + "\n")
else:
	for i in range(0,len(predictions)):
		fout.write(str(predictions[i]) + "," + str(Y[i]) + "\n")

fout.close()

Phil = pyttsx.init()
Phil.say('Processing, complete')
Phil.runAndWait()
