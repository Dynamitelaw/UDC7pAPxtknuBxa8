'''
Dynamitelaw
Function Graveyard: Code that is no longer in use, but may prove useful in the future.
Don't delete! Just dump it all here.
'''


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

       #[ [ [input], [output] ]

def create_feature_sets_and_labels(file_path,test_size = 0.1):
		
	features = sample_handling(file_path)
	random.shuffle(features)
	features = np.array(features)
	testing_size = int(test_size*len(features))
	print(testing_size)
	train_x = list(features[0:testing_size][:,0])
	train_y = list(features[0:testing_size][:,1])
	test_x = list(features[testing_size:][:,0])
	test_y = list(features[testing_size:][:,1])
	#print(train_x)
	return train_x,train_y,test_x,test_y
	
def GenTrainData(fields = None, daterange = None):
    '''
    Generates a pickle of training and testing data for the entire market.
    
    Fields is a list of strings specifying which data columns you want included. Defaults to all fields
    possible fields-> ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close', '2 Day Slope', '5 Day Slope', 'Standard Dev']
    
    Daterange is an optional 2 element list, containing the min and max dates desired for the created pickle.
    Dates must have following format:  'YYYY-MM-DD'
    Dates must be given in increasing order (ie. 2012 before 2015)
    '''
    error = False

    if fields:      #if specified fields are given
        fieldlist = []
        for f in fields:
            if f == 'Open':
                fieldlist.append(0)
            if f == 'High':
                fieldlist.append(1)
            if f == 'Low':
                fieldlist.append(2)
            if f == 'Close':
                fieldlist.append(3)
            if f == 'Volume':
                fieldlist.append(4)
            if f == 'Adj Close':
                fieldlist.append(5)
            if f == '2 Day Slope':
                fieldlist.append(6)
            if f == '5 Day Slope':
                fieldlist.append(7)
            if f == 'Standard Dev':
                fieldlist.append(8)
        
        fieldlist.sort()
        idx = 0
        for f in fieldlist:     #puts the field labels in order
            if f == 0:
                fieldlist[idx] = 'Open'
            if f == 1:
                fieldlist[idx] = 'High'
            if f == 2:
                fieldlist[idx] = 'Low'
            if f == 3:
                fieldlist[idx] = 'Close'
            if f == 4:
                fieldlist[idx] = 'Volume'
            if f == 5:
                fieldlist[idx] = 'Adj Close'
            if f == 6:
                fieldlist[idx] = '2 Day Slope'
            if f == 7:
                fieldlist[idx] = '5 Day Slope'
            if f == 8:
                fieldlist[idx] = 'Standard Dev'
            idx += 1
            
    else:
        fieldlist = False
        
        
    if daterange:       #if date range is specified
        if (len(daterange[0]) != 10) or (len(daterange[1]) != 10) or (len(daterange) != 2):     #if daterange is invalid
            print ('Error: Invalid Daterange')
            error = True
        else:
            dates = []      #list containing range of dates
            for d in daterange:
                date = []
                year = int(d[0:4])
                month = int(d[5:7])
                day = int(d[8:10])
                date.append(year)
                date.append(month)
                date.append(day)
                dates.append(date)
                
    if error == False:      #if all inputes are valid
        tickerFile = open('Data/ListOfTickerSymbols.csv','r') #opens ticker file
        row = 0
        data = []       #final data list to be saved to pickle
        
        for l in tickerFile:		#iterates through tickers and creates training data 
            if row == 0:        #skips first row of ticker file
                row = 1
            else:
                ticker = l.rstrip()
                try:                
                    if fieldlist == False:
                        sdata = GenerateIO(ticker)
                    else:
                        sdata = GenerateIO(ticker,fieldlist)        #generates IO for that stock

                    if daterange:       #truncates IO for that stock based on date range (if specified)
                        sidx = 0
                        delidx = []
                        for d in sdata:
                            delete = False
                            sdate = d[1][0][1:11]
                            syear = int(sdate[0:4])
                            smonth = int(sdate[5:7])
                            sday = int(sdate[8:10])
                            if (syear < dates[0][0]) or (syear > dates[1][0]):
                                delete = True
                            if (syear == dates[0][0] and smonth < dates[0][1]) or (syear == dates[1][0] and smonth > dates[1][1]):
                                delete = True
                            if (syear == dates[0][0] and smonth == dates[0][1] and sday < dates[0][2]) or (syear == dates[1][0] and smonth == dates[1][1] and sday > dates[1][2]):
                                delete = True
                            
                            if delete == True:
                                delidx.append(sidx)
                            
                            sidx += 1
        
                        delidx.sort(reverse = True)
                        for i in delidx:
                            del sdata[i]        #deletes unwanted dates

                    data.extend(sdata)      #adds stock's IO to master data list
           
                except Exception as e:
                    #print ('Error generation IO for ' + ticker)
                    #print(e)
                    pass

            
        tickerFile.close()
        
        savepath = 'Data/TrainData/Level1/data_'        #saves data to a pickle
        if fields:
            if daterange:
                savepath = savepath + '_' + str(fieldlist).strip('[],"') + '_' + str(daterange).strip('[],"')
            else:
                savepath = savepath + '_' + str(fieldlist).strip('[],"')
        if daterange:
            if fieldlist == False:
                savepath = savepath + '_' + str(daterange).strip('[],"')
                
        savepath = savepath + '.p'
        pickle.dump(data,open(savepath,'wb'))


def RetrieveTrainData(ratio, fields = None, daterange = None):
    '''
    Retrieves training data from pickle and outputs it as a list.
    If the pickle doesn't exist, it creates the pickle first, the returns the list.
    Output data is formated as -> [train, test]
    
    Ratio is the ratio of testing to training data size (0<ratio<1).
    
    Fields is a list of strings specifying which data columns you want included. Defaults to all fields
    possible fields-> ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close', '2 Day Slope', '5 Day Slope', 'Standard Dev']
    
    Daterange is an optional 2 element list, containing the min and max dates desired for the data.
    Dates must have following format:  'YYYY-MM-DD'
    Dates must be given in increasing order (ie. 2012 before 2015)
    '''
    
    if fields:      #if specified fields are given
        fieldlist = []
        for f in fields:
            if f == 'Open':
                fieldlist.append(0)
            if f == 'High':
                fieldlist.append(1)
            if f == 'Low':
                fieldlist.append(2)
            if f == 'Close':
                fieldlist.append(3)
            if f == 'Volume':
                fieldlist.append(4)
            if f == 'Adj Close':
                fieldlist.append(5)
            if f == '2 Day Slope':
                fieldlist.append(6)
            if f == '5 Day Slope':
                fieldlist.append(7)
            if f == 'Standard Dev':
                fieldlist.append(8)
        
        fieldlist.sort()
        idx = 0
        for f in fieldlist:     #puts the field labels in order
            if f == 0:
                fieldlist[idx] = 'Open'
            if f == 1:
                fieldlist[idx] = 'High'
            if f == 2:
                fieldlist[idx] = 'Low'
            if f == 3:
                fieldlist[idx] = 'Close'
            if f == 4:
                fieldlist[idx] = 'Volume'
            if f == 5:
                fieldlist[idx] = 'Adj Close'
            if f == 6:
                fieldlist[idx] = '2 Day Slope'
            if f == 7:
                fieldlist[idx] = '5 Day Slope'
            if f == 8:
                fieldlist[idx] = 'Standard Dev'
            idx += 1
            
    else:
        fieldlist = False
        
    
    filepath = 'Data/TrainData/Level1/data_'        
    if fields:
        if daterange:
            filepath = filepath + '_' + str(fieldlist).strip('[],"') + '_' + str(daterange).strip('[],"')
        else:
            filepath = filepath + '_' + str(fieldlist).strip('[],"')
    if daterange:
        if fields == None:
            filepath = filepath + '_' + str(daterange).strip('[],"')
            
    filepath = filepath + '.p'      #file path for pickle

    try:
        data = pickle.load(open(filepath,'rb'))
    except:
        print ('Pickle does not exist yet')     #if pickle doesn't exits yet...
        print ('Generating pickle now...')
        GenTrainData(fields, daterange)     #generates pickle
        print ('Here you go')
        data = pickle.load(open(filepath,'rb'))
        
    
    k = len(data)
    rand = np.random.random((k))
    train = []
    test = []

    indx = 0
    for r in rand:      #splits data into training and testing lists
        if r < ratio:
            test.append(data[indx])
        else:
            train.append(data[indx])
        indx += 1
            
    outdata = [train, test]
    return outdata
    
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


"""
Retrieved from https://github.com/himoacs/iex_data
Dynamitelaw: This is here in case the other API breaks or is no longer availible
Since its a python file rather than a library, it doesn't require a pip-install



This api will provide a python wrapper over IEX's native api for retrieving its data.

This api will allow you to:
- get latest quote and trade data
- get trade data only

"""

import pandas as pd
from urllib.request import Request, urlopen
import json
from pandas.io.json import json_normalize


class API(object):

    """
    This API class allows users to get different type of data from IEX via its methods.
    API class can be used for:
    - requesting valid securities
    - getting latest quote and trade data
    - getting latest trade data

    Examples:
        m = API()
        print(m.get_latest_trade_data(['AAPL', 'IBM']))
        print(m.get_latest_quote_and_trade_data(['AAPL', 'IBM']))
        print(m.return_valid_securities(['AAPL', 'IBM']))
    """

    def __init__(self):
        self._end_point_prefix = r'https://api.iextrading.com/1.0/'

    def return_valid_securities(self, securities):

        """
        Return a list of valid securities
        :param securities: list of securities
        :return: list of valid securities
        """

        suffix = r'ref-data/symbols'
        valid_securities = self._url_to_dataframe(self._end_point_prefix+suffix)['symbol']

        return [x for x in securities if x in set(valid_securities)]

    def _url_to_dataframe(self, url, nest=None):

        """
        Takes a url and returns the response in a pandas dataframe
        :param url: str url
        :param nest: column with nested data
        :return: pandas dataframe containing data from url
        """

        request = Request(url)
        response = urlopen(request)
        elevations = response.read()
        data = json.loads(elevations)

        if nest:
            data = json_normalize(data[nest])
        else:
            data = json_normalize(data)

        return pd.DataFrame(data)

    def get_latest_quote_and_trade(self, securities):

        """
        Gets latest quote and trade data
        :param securities: list of securities
        :return: pandas dataframe containing data for valid securities
        """

        securities = self.return_valid_securities(securities)

        if securities:
            suffix = r'tops?symbols='
            symbols = ','.join(securities)
            df = self._url_to_dataframe(self._end_point_prefix + suffix + symbols)
            df['lastSaleTime'] = pd.to_datetime(df['lastSaleTime'], unit='ms')
            df['lastUpdated'] = pd.to_datetime(df['lastUpdated'], unit='ms')
            df.set_index(['symbol'], inplace=True)
            return df
        else:
            print('These stock(s) are invalid!')

    def get_latest_trade(self, securities):

        """
        Gets latest trade data
        :param securities: list of securities
        :return: pandas dataframe containing data for valid securities
        """

        securities = self.return_valid_securities(securities)

        if securities:
            suffix = r'tops/last?symbols='
            symbols = ','.join(securities)
            df = self._url_to_dataframe(self._end_point_prefix + suffix + symbols)
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            df.set_index(['symbol'], inplace=True)
            return df
        else:
            print('These stock(s) are invalid!')

    def get_latest_news(self, securities, count=1):

        """
        Get latest news for securities. By default, gets one news item per security.

        :param securities: list of securities
        :param count: how many news items to return
        :return: dataframe
        """

        securities = self.return_valid_securities(securities)

        final_df = pd.DataFrame({})

        # Get news for each security and then append the results together
        if securities:
            for symbol in securities:
                suffix = r'stock/{symbol}/news/last/{count}'.format(symbol=symbol,
                                                                    count=count)
                df = self._url_to_dataframe(self._end_point_prefix + suffix)
                df['time'] = pd.to_datetime(df['datetime'])
                del df['datetime']
                df['symbol'] = symbol
                df = df[['symbol', 'time', 'headline', 'summary', 'source', 'url', 'related']]
                final_df = final_df.append(df, ignore_index=True)
            return final_df
        else:
            print('These stock(s) are invalid!')

    def get_financials(self, securities):

        """
        Get latest financials of securities. By default, gets one news item per security.
        :param securities: list of symbols
        :return: dataframe
        """

        securities = self.return_valid_securities(securities)

        final_df = pd.DataFrame({})

        # Get financials of each security and then append the results together
        if securities:
            for symbol in securities:
                suffix = r'stock/{symbol}/financials'.format(symbol=symbol)
                df = self._url_to_dataframe(self._end_point_prefix + suffix, 'financials')
                df['symbol'] = symbol
                final_df = final_df.append(df, ignore_index=True)
            return final_df
        else:
            print('These stock(s) are invalid!')

    def get_earnings(self, securities):

        """
        Get latest earnings for securities.
        :param securities: list of symbols
        :return: dataframe
        """

        securities = self.return_valid_securities(securities)

        final_df = pd.DataFrame({})

        # Get earnings data for each security and then append the results together
        if securities:
            for symbol in securities:
                suffix = r'stock/{symbol}/earnings'.format(symbol=symbol)
                df = self._url_to_dataframe(self._end_point_prefix + suffix, 'earnings')
                df['symbol'] = symbol
                final_df = final_df.append(df, ignore_index=True)
            return final_df
        else:
            print('These stock(s) are invalid!')

    def get_trade_bars_data(self, securities, bucket='1m'):

        """
        Get bucketed trade/volume data. Supported buckets are: 1m, 3m, 6m, 1y, ytd, 2y, 5y

        :param securities: list of securities
        :param bucket:
        :return: dataframe
        """

        securities = self.return_valid_securities(securities)

        final_df = pd.DataFrame({})

        # Get earnings data for each security and then append the results together
        if securities:
            for symbol in securities:
                suffix = r'stock/{symbol}/chart/{bucket}'.format(symbol=symbol,
                                                                   bucket=bucket)
                df = self._url_to_dataframe(self._end_point_prefix + suffix)
                df['symbol'] = symbol
                final_df = final_df.append(df, ignore_index=True)
            return final_df
        else:
            print('These stock(s) are invalid!')


def processListOfTickers(listOfTickers):
    '''
    Creates pandas dataframe CSVs for every ticker in listOfTickers
    '''
    lengthOfTickerList = len(listOfTickers)

    for i in range(0,lengthOfTickerList,1):
        ticker = listOfTickers[i]

        try:
            process(ticker)
        except Exception as e:
            #print(e)
            try:
                os.remove('Data/StockData/'+ticker+'.csv')			
            except Exception as e:
                pass

        #Approximate Progress bar
        percentComplete = int((i*100)/(lengthOfTickerList-1))
        sys.stdout.write("\r")
        if (percentComplete < 10):
            sys.stdout.write("~ 0{}% Complete".format(percentComplete))
        else:
            sys.stdout.write("~ {}% Complete".format(percentComplete))
        sys.stdout.write("\r")
        sys.stdout.flush()


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