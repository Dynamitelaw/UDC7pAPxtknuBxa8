import yahoo_finance
from yahoo_finance import Share
import io
from pprint import pprint

tickerFile = open('Data/ListOfTickerSymbols.csv','r')

for line in tickerFile:
	print(line)
	stock = Share(line)
	stockFile = open('Data/StockData/'+line, 'w')
	stockFile.write(str(stock.get_historical('2000-01-01','2016-10-11')))
	stockFile.close()
