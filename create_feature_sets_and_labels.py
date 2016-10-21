import nltk
from nltk.tokenize import word_tokenize
import numpy as np
import random
import pickle
from collections import Counter
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
hm_lines = 100000

def create_lexicon(pos,neg):

	lexicon = []
	with open(pos,'r') as f:
		contents = f.readlines()
		for l in contents[:hm_lines]:
			all_words = word_tokenize(l)
			lexicon += list(all_words)

	with open(neg,'r') as f:
		contents = f.readlines()
		for l in contents[:hm_lines]:
			all_words = word_tokenize(l)
			lexicon += list(all_words)

	lexicon = [lemmatizer.lemmatize(i) for i in lexicon]
	w_counts = Counter(lexicon)
	l2 = []
	for w in w_counts:
		#print(w_counts[w])
		if 1000 > w_counts[w] > 50:
			l2.append(w)
	print(len(l2))
	return l2





def sample_handling(data_file):

	featureset = []

			########################
			########################
                        ##put inputs in features
			#put output in classification
			#########################
			featureset.append([features,classification])

	return featureset



def create_feature_sets_and_labels(file_path,test_size = 0.1):
	try:
	    data_file = open(file_path, 'r')	
	except Exception as e:
	    print(e)	
	features = []
	features += sample_handling(data_file)
	random.shuffle(features)
	features = np.array(features)

	testing_size = int(test_size*len(features))

	train_x = list(features[:,0][:-testing_size])
	train_y = list(features[:,1][:-testing_size])
	test_x = list(features[:,0][-testing_size:])
	test_y = list(features[:,1][-testing_size:])

	return train_x,train_y,test_x,test_y


"""if __name__ == '__main__':
	train_x,train_y,test_x,test_y = create_feature_sets_and_labels('/path/to/pos.txt','/path/to/neg.txt')
	# if you want to pickle this data:
	with open('/path/to/sentiment_set.pickle','wb') as f:
		pickle.dump([train_x,train_y,test_x,test_y],f)"""
