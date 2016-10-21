import numpy as np
from pprint import pprint
file_path = 'Data/PcsData/A\n.csv'
data = np.genfromtxt(file_path,delimiter=',')
data = np.delete(data,[0,10,13], axis=1)
data = np.delete(data,[0], axis=0)

i = data.shape
k=0
features_set = []
while k<i[0]:
	#print(data[k])
	day = data[k]
	feat = np.delete(day,[9,10],axis=0)
	classf = np.delete(day,[0,1,2,3,4,5,6,7,8],axis=0)
	res = [feat,classf]
	features_set.append(res)
	k+=1
print(len(features_set))
print(features_set[0:])

