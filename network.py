'''
ilPesce
Trains Level 1 Neural Network that 
outputs buy certainty and sell certainty
'''



import tensorflow as tf
import numpy as np
import os
import GenerateTrainingData as gtd


'''
from create_sentiment_featuresets import create_feature_sets_and_labels
train_x,train_y,test_x,test_y = create_feature_sets_and_labels('Data/PcsData/A\n.csv')
'''

'''
#helper method for extracting relevant data
def extractRelevantData(data):
	inputs = []
	outputs = []	
	for i in range(len(data)):
		inputs += data[i][2]      #<- this syntax makes no sense. What were you trying to do?
		output += data[i][3]
	output = [inputs, outputs]
	return output

 
#import data from processed data files
data = gtd.RetrieveTrainData(0.1,['Open','2 Day Slope','5 Day Slope'],['2010-01-01','2010-01-01'])
print(len(data[0]))
train = extractRelevantData(data[0])
test = extractRelevantData(data[1])

train_x = train[0]
print(len(train_x))
train_y = train[1]
test_x = test[0]
test_y = test[1]
'''

#Number of neurons from each hidden layer
n_nodes_hl1 = 1500
n_nodes_hl2 = 1500
n_nodes_hl3 = 1500

#training parameters
n_classes = 2
#batch_size = 50
hm_epochs = 200

#Tensorflow placeholders for input and output data
x = tf.placeholder('float')		
y = tf.placeholder('float')


#sets up hidden layers with weigth and bias matricies
hidden_1_layer = {'f_fum':n_nodes_hl1,
                  'weight':tf.Variable(tf.random_normal([len(train_x[0]), n_nodes_hl1])),
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

'''
def train_neural_network(x):
	prediction = neural_network_model(x)
	cost = tf.reduce_mean( tf.nn.softmax_cross_entropy_with_logits(prediction,y) )
	optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(cost) #standard stochastic descent model for deep NN

	with tf.Session() as sess:
		sess.run(tf.initialize_all_variables())
	    
		for epoch in range(hm_epochs):
			epoch_loss = 0
			i=0
			while i < len(train_x):
				start = i
				end = i+batch_size
				batch_x = np.array(train_x[start:end])
				batch_y = np.array(train_y[start:end])

				_, c = sess.run([optimizer, cost], feed_dict={x: batch_x,y: batch_y})
				epoch_loss += c
				i+=batch_size
				
			print('Epoch', epoch+1, 'completed out of',hm_epochs,'loss:',epoch_loss)
		correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
		accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
		print('Accuracy:',accuracy.eval({x:test_x, y:test_y}))
'''


def train_neural_network(x, fields = None, daterange = None):
	prediction = neural_network_model(x)
	cost = tf.reduce_mean( tf.nn.softmax_cross_entropy_with_logits(prediction,y) )
	optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(cost) #standard stochastic descent model for deep NN
 

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
     

	with tf.Session() as sess:     #starts tensor flow session
		sess.run(tf.initialize_all_variables())
	    
		for epoch in range(hm_epochs):
			epoch_loss = 0
			for ticker in tickertrain:       #each batch is the IO for one of the training tickers
				stocktrain = gtd.GenerateIO(ticker, fields, daterange)
				batch_x = np.array(stocktrain[0])
				batch_y = np.array(stocktrain[1])

				_, c = sess.run([optimizer, cost], feed_dict={x: batch_x,y: batch_y})
				epoch_loss += c
				
				
			print('Epoch', epoch+1, 'completed out of',hm_epochs,'loss:',epoch_loss)
		correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
  
		accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
		AccuracySum = 0  
		for ticker in tickertest:     #finds the accuracy for each stock of the testing ticker list
			stocktest = gtd.GenerateIO(ticker, fields, daterange)
			StockAccuracy = accuracy.eval({x:stocktest[0], y:stocktest[1]})
			AccuracySum += StockAccuracy   
   
		print('Accuracy:',AccuracySum/(len(tickertest)))      #prints average accuracy



	    
train_neural_network(x)
