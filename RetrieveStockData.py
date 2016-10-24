'''
ilPesce
Requests all stock data from Yahoo Finance
API and stores them as CSV's
'''

import urllib
import io

###########################support methods############################
base_url = "http://ichart.finance.yahoo.com/table.csv?s="
def make_url(ticker_symbol):  #creates url for downloading from yahoo
    return base_url + ticker_symbol

output_path = "Data/StockData" #directory containing stock data
def make_filename(ticker_symbol):
    return output_path + "/" + ticker_symbol + ".csv"

def pull_historical_data(ticker_symbol):    #downloads the stock data
    try:
        urllib.urlretrieve(make_url(ticker_symbol), make_filename(ticker_symbol))
    except urllib.ContentTooShortError as e:
        outfile = open(make_filename(ticker_symbol, directory), "w")
        outfile.write(e.content)
        outfile.close()
#######################################################################

tickerFile = open('Data/ListOfTickerSymbols.csv','r') #opens ticker file

for line in tickerFile:		#iterates through file and downloads data
	pull_historical_data(line)
	print(make_url(line))
