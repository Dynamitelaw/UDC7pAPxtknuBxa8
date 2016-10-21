
import numpy as np
import random
import pickle




def sample_handling(file_path):

	featureset = []


	data = np.genfromtxt(file_path,delimiter=',')
	data = np.delete(data,[0,10,13], axis=1)
	data = np.delete(data,[0], axis=0)

	i = data.shape
	k=0
	feature_set = []
	while k<i[0]:
		#print(data[k])
		day = data[k]
		feat = np.delete(day,[9,10],axis=0)
		classf = np.delete(day,[0,1,2,3,4,5,6,7,8],axis=0)
		res = [feat,classf]
		feature_set.append(res)
		#print(feature_set)
		k+=1
	print(len(feature_set))
	return feature_set



def create_feature_sets_and_labels(file_path,test_size = 0.1):
		
	features = sample_handling(file_path)
	random.shuffle(features)
	features = np.array(features)

	testing_size = int(test_size*len(features))
	train_x = list(features[:0][:-testing_size])
	train_y = list(features[:,1][:-testing_size])
	test_x = list(features[:,0][-testing_size:])
	test_y = list(features[:,1][-testing_size:])

	return train_x,train_y,test_x,test_y


"""if __name__ == '__main__':
	train_x,train_y,test_x,test_y = create_feature_sets_and_labels('/path/to/pos.txt','/path/to/neg.txt')
	# if you want to pickle this data:
	with open('/path/to/sentiment_set.pickle','wb') as f:
		pickle.dump([train_x,train_y,test_x,test_y],f)"""
