'''
Dynamitelaw

Imports all required system paths
'''

import sys


systemPathList = []

#Populate system path list
systemPathList.append("SVM_Models/")
systemPathList.append("Selectors/")
systemPathList.append("TestingScripts/")
systemPathList.append("Tensorflow/")
systemPathList.append("utils/")

#Insert all paths in systemPathList
insertionIndex = 0
for path in systemPathList:
    sys.path.insert(insertionIndex, path)
    insertionIndex += 1
