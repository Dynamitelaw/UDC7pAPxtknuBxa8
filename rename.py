'''
Dynamitelaw
For some reason, the downloaded stock files have an extra character at the end of the name,
so this removes them.
'''

import os

os.chdir('/home/dynamitelaw/Documents/dw/UDC7pAPxtknuBxa8-firstTfModel/Data')

k = os.listdir('StockData')
os.chdir('/home/dynamitelaw/Documents/dw/UDC7pAPxtknuBxa8-firstTfModel/Data/StockData')

for file in k:
	os.rename(file,file[0:-5]+file[-4:])

