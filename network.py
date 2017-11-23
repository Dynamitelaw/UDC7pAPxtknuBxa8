'''
ilPesce
Trains Level 1 Neural Network that 
outputs buy certainty and sell certainty
'''

##############################################
#	1) This shit don't work
#	2) Moving network to networkL1.py
##############################################

import tensorflow as tf
import numpy as np
import os
import GenerateTrainingData as gtd
import time


#Number of neurons from each hidden layer
n_nodes_hl1 = 1500
n_nodes_hl2 = 1500
n_nodes_hl3 = 1500

#training parameters
n_classes = 2
#batch_size = 50
hm_epochs = 2

#Tensorflow placeholders for input and output data
x = tf.placeholder('float',)		
y = tf.placeholder('float')


#sets up hidden layers with weigth and bias matricies
hidden_1_layer = {'f_fum':n_nodes_hl1,
                  'weight':tf.Variable(tf.random_normal([810, n_nodes_hl1])),
                  'bias':tf.Variable(tf.random_normal([n_nodes_hl1]))}

hidden_2_layer = {'f_fum':n_nodes_hl2,
                  'weight':tf.Variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
                  'bias':tf.Variable(tf.random_normal([n_nodes_hl2]))}

hidden_3_layer = {'f_fum':n_nodes_hl3,
                  'weight':tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_hl3])),
                  'bias':tf.Variable(tf.random_normal([n_nodes_hl3]))}

output_layer = {'f_fum':None,
                'weight':tf.Variable(tf.random_normal([n_nodes_hl3, n_classes])),
                'bias':tf.Variable(tf.random_normal([n_classes])),}


#creates nerual network model by setting activation functions and layer
#relationships
def neural_network_model(data):
    l1 = tf.add(tf.matmul(data,hidden_1_layer['weight']), hidden_1_layer['bias'])
    l1 = tf.nn.relu(l1)

    l2 = tf.add(tf.matmul(l1,hidden_2_layer['weight']), hidden_2_layer['bias'])
    l2 = tf.nn.relu(l2)

    l3 = tf.add(tf.matmul(l2,hidden_3_layer['weight']), hidden_3_layer['bias'])
    l3 = tf.nn.relu(l3)

    output = tf.matmul(l3,output_layer['weight']) + output_layer['bias']

    return output


def train_neural_network(x, fields = None, daterange = None):
	'''
	Trains the nerual network (Level 1), then saves the network to a .ckpt file
	'''

	saver = tf.train.Saver()		#creates saver object to later save the trained network

	prediction = neural_network_model(x)
	cost = tf.reduce_mean( tf.nn.softmax_cross_entropy_with_logits(prediction,y) )
	optimizer = tf.train.AdamOptimizer(learning_rate=0.0003).minimize(cost) #standard stochastic descent model for deep NN
 

	tickerlist = os.listdir('Data/PcsData/')       #obtains list of all processed stock files
	k = len(tickerlist)
	rand = np.random.random((k))
	tickertrain = []       #list of training tickers
	tickertest = []        #list of testing tickers

	indx = 0
	for r in rand:      #randomly splits tickers into training and testing lists
		if r < 0.915:
			tickertest.append(tickerlist[indx])
		else:
			tickertrain.append(tickerlist[indx])
		indx += 1
	

	tickertrain = tickertrain[0:100]
	tickertest = tickertest[0:200]
	with tf.Session() as sess:     #starts tensor flow session
		sess.run(tf.initialize_all_variables())
	    
		for epoch in range(hm_epochs):
			epoch_loss = 0
			startime=time.time()
			for ticker in tickertrain:       #each batch is the IO for one of the training tickers
				try:					
					stocktrain = gtd.GenerateIO(ticker, fields, daterange)
					#print(ticker)
					batch_x = stocktrain[0]
					#print(len(batch_x[0]))
					batch_y = stocktrain[1]
					_, c = sess.run([optimizer, cost], feed_dict={x: batch_x,y: batch_y})
					epoch_loss += c
				except Exception as e:
					print(e)
					pass
				
			print('Epoch', epoch+1, 'completed out of',hm_epochs,'loss:',epoch_loss)
			print('Hours: '+str((time.time()-startime)/3600))
		correct = tf.equal(prediction,y)
  
		accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
		AccuracySum = 0  
		g = len(tickertest)
		k=0

		for ticker in tickertest:     #finds the accuracy for each stock of the testing ticker list
			try:				
				stocktest = gtd.GenerateIO(ticker, fields, daterange)
				StockAccuracy = accuracy.eval({x:stocktest[0], y:stocktest[1]})
				AccuracySum += StockAccuracy
				print(sess.run(prediction.eval(feed_dict={x:stocktest[0][0:2]})))
				k +=1   
   			except Exception as e:
				g -=1
		print(g)		
		print('Accuracy:',AccuracySum/k)      #prints average accuracy

		savepath = saver.save(sess,'NetworkLevel1.ckpt')		#saves the neural network



	    
train_neural_network(x)

def testnetwork():
	saver = tf.train.Saver()
	tickerlist = os.listdir('Data/PcsData/')       #obtains list of all processed stock files
	k = len(tickerlist)
	rand = np.random.random((k))
	tickertrain = []       #list of training tickers
	tickertest = []        #list of testing tickers

	indx = 0
	for r in rand:      #randomly splits tickers into training and testing lists
		if r < 0.1:
			tickertest.append(tickerlist[indx])
		else:
			tickertrain.append(tickerlist[indx])
		indx += 1

	tickertest = tickertest[0:10]
	
	with tf.Session() as sess:
		saver.restore(sess,'NetworkLevel1.ckpt')
		prediction = neural_network_model(x)

		correct = tf.equal(prediction,y)
		accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
		AccuracySum = 0  
		g = len(tickertest)
		k=0

		for ticker in tickertest:     #finds the accuracy for each stock of the testing ticker list
			try:				
				stocktest = gtd.GenerateIO(ticker)
				StockAccuracy = accuracy.eval({x:stocktest[0], y:stocktest[1]})
				AccuracySum += StockAccuracy
				print(sess.run(prediction.eval(feed_dict={x:stocktest[0][0:2]})))
				k +=1   
   			except Exception as e:
   				print(e)
				g -=1
		print(g)		
		print('Accuracy:',AccuracySum/k)


#testnetwork()
