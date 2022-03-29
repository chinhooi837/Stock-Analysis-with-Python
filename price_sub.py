# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 16:45:36 2021

@author: Coen (Chin Hooi) Yap
"""


# 7.30PM
import gc
gc.collect()

import yfinance as yf
import requests
import pandas as pd 
import time
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta 
import shutil
import urllib.request as request
from contextlib import closing
from datetime import datetime

from yahoo_fin import stock_info as si
from yahoo_fin import *

start = datetime.now()
print(start)

#read config file for api_key fron finance model prep
import yaml

with open("config.yaml", "r") as ymlfile:
    cfg = yaml.load(ymlfile)

for section in cfg:
    print(section)
api_key=cfg["apikey"]


#read the loaded price_check file from 
price_full = pd.read_csv('price_check_280322.csv')
test=price_full[price_full['price']>=10]
companies=test['index'].tolist()
companies.insert(0,'^GSPC')


# Initiate variables
price = {}
companies_left=[]
metrics = {}
RS = pd.DataFrame()

#running for first round to initiate data for index level
company=companies[0] #GSIC S&P 500 Index

prices_retrieval = requests.get(f'https://financialmodelingprep.com/api/v3/historical-price-full/{company}?timeseries=500&apikey={api_key}').json()
prices_retrieval = prices_retrieval['historical']
price = {}
price[company] = {}
metrics[company] = {}
for item in prices_retrieval:
	price_date = item['date']
	price[company][price_date] = item['close']
price_DF_idx = pd.DataFrame.from_dict(price)
price_DF_idx=price_DF_idx.sort_index(ascending=True)
price_DF_idx['200_MA'] = price_DF_idx[company].rolling(window=200,min_periods=1).mean()
price_DF_idx['150_MA'] = price_DF_idx[company].rolling(window=150,min_periods=1).mean()
price_DF_idx['50_MA'] = price_DF_idx[company].rolling(window=50,min_periods=1).mean()

price_DF_idx['price_before60'] = price_DF_idx[company].shift(60)
price_DF_idx['price_before125'] = price_DF_idx[company].shift(125)
price_DF_idx['price_before250'] = price_DF_idx[company].shift(250)

price_DF_idx['RS_3months'] = (price_DF_idx[company]/price_DF_idx['^GSPC'] )/ (price_DF_idx['price_before60'] /price_DF_idx['price_before60'] ) *100
price_DF_idx['RS_halfYear'] = (price_DF_idx[company]/price_DF_idx['^GSPC'] )/ (price_DF_idx['price_before125'] /price_DF_idx['price_before125'] ) *100
price_DF_idx['RS'] = (price_DF_idx[company]/price_DF_idx['^GSPC'] )/ (price_DF_idx['price_before250'] /price_DF_idx['price_before250'] ) *100

	
metrics[company]['200 MA'] = price_DF_idx['200_MA'][-1]
metrics[company]['150 MA'] = price_DF_idx['150_MA'][-1]
metrics[company]['50 MA'] = price_DF_idx['50_MA'][-1]
metrics[company]['200 MA_1mago'] = price_DF_idx['200_MA'][-30]
metrics[company]['150 MA_1mago'] = price_DF_idx['150_MA'][-30]
metrics[company]['200 MA_2mago'] = price_DF_idx['200_MA'][-60]
metrics[company]['150 MA_2mago'] = price_DF_idx['150_MA'][-60]
metrics[company]['52W_Low'] = price_DF_idx[company][-252:].min()
metrics[company]['52W_High'] = price_DF_idx[company][-252:].max()
metrics[company]['price'] = price_DF_idx[company][-1]
metrics[company]['Relative Strength'] = price_DF_idx['RS'][-1]
metrics[company]['Above_30%_low'] = metrics[company]['52W_Low'] *1.3
metrics[company]['Within_25%_high'] = metrics[company]['52W_High'] * 0.75



RS=RS.merge(price_DF_idx,left_index=True, right_index=True,how='right')
RS=RS.drop([company, '200_MA', '150_MA', '50_MA','price_before60', 'price_before125',
       'price_before250', 'RS_3months','RS_halfYear'],axis=1)
RS.rename(columns={"RS": company},inplace = True)

RS_3 = RS.copy()
RS_6 = RS.copy()



price = {}
metrics = {}
count = 0
companies_left=[]
companies_left2=[]


for company in companies:
	count = count + 1
	print('count ' ,count, " ", company)
	try:
		 prices_retrieval = requests.get(f'https://financialmodelingprep.com/api/v3/historical-price-full/{company}?timeseries=500&apikey={api_key}').json()
		 if type(prices_retrieval)==dict:
		  for key in prices_retrieval.keys():
      			if key == 'Error Message': print(company,'not done')
      			if key == 'Error Message': companies_left.append(company)  
		 prices_retrieval = prices_retrieval['historical']
		 price = {}
		 price[company] = {}
		 metrics[company] = {}
		 for item in prices_retrieval:
 	 		price_date = item['date']
 	 		price[company][price_date] = item['close']
 			
		 price_DF = pd.DataFrame.from_dict(price)
		 price_DF = price_DF.sort_index(ascending=True)

		 price_DF['200_MA'] = price_DF[company].rolling(window=200,min_periods=1).mean()
		 price_DF['150_MA'] = price_DF[company].rolling(window=150,min_periods=1).mean()
		 price_DF['50_MA'] = price_DF[company].rolling(window=50,min_periods=1).mean()

		 price_DF['price_before60'] = price_DF[company].shift(60)
		 price_DF['price_before125'] = price_DF[company].shift(125)
		 price_DF['price_before250'] = price_DF[company].shift(250)
         
		 price_DF['RS_3months'] = (price_DF[company]/price_DF_idx['^GSPC'] )/ (price_DF['price_before60'] /price_DF_idx['price_before60'] ) *100        
		 price_DF['RS_halfYear'] = (price_DF[company]/price_DF_idx['^GSPC'] )/ (price_DF['price_before125'] /price_DF_idx['price_before125'] ) *100
		 price_DF['RS'] = (price_DF[company]/price_DF_idx['^GSPC'] )/ (price_DF['price_before250'] /price_DF_idx['price_before250'] ) *100	

		 price_DF_3 = price_DF[['RS_3months']]
		 price_DF_6= price_DF[['RS_halfYear']]
		 price_DF1=price_DF[['RS']]

		 price_DF1.rename(columns={"RS": company},inplace = True)
		 price_DF_3.rename(columns={"RS_3months": company},inplace = True)
		 price_DF_6.rename(columns={"RS_halfYear": company},inplace = True)
         
		 RS=RS.merge(price_DF1,left_index=True, right_index=True,how='outer')
		 RS_3=RS_3.merge(price_DF_3,left_index=True, right_index=True,how='outer')
		 RS_6=RS_6.merge(price_DF_6,left_index=True, right_index=True,how='outer')
		 
		 metrics[company]['200 MA'] = price_DF['200_MA'][-1]
		 metrics[company]['150 MA'] = price_DF['150_MA'][-1]
		 metrics[company]['50 MA'] = price_DF['50_MA'][-1]
		 metrics[company]['200 MA_1mago'] = price_DF['200_MA'][-30]
		 metrics[company]['150 MA_1mago'] = price_DF['150_MA'][-30]
		 metrics[company]['200 MA_2mago'] = price_DF['200_MA'][-60]
		 metrics[company]['150 MA_2mago'] = price_DF['150_MA'][-60]
		 metrics[company]['52W_Low'] = price_DF[company][-252:].min()
		 metrics[company]['52W_High'] = price_DF[company][-252:].max()
		 metrics[company]['price'] = price_DF[company][-1]
		 metrics[company]['Relative Strength'] = price_DF['RS'][-1]
		 #Current Price is at least 30% above 52 week low (1.3*low_of_52week)
		 metrics[company]['Above_30%_low'] = metrics[company]['52W_Low'] *1.3
		 # Condition 7: Current Price is within 25% of 52 week high   (.75*high_of_52week)
		 metrics[company]['Within_25%_high'] = metrics[company]['52W_High'] * 0.75
	except:
		print("failed "+company)
		companies_left.append(company)  
    
count = 0

#rerun for any tickers that failed the first round, to ensure that the failure is not due to internet connection issue 
for company in companies_left:
	count = count + 1
	print('count ' ,count, " ", company)
	try:
		 prices_retrieval = requests.get(f'https://financialmodelingprep.com/api/v3/historical-price-full/{company}?timeseries=500&apikey={api_key}').json()
		 if type(prices_retrieval)==dict:
		  for key in prices_retrieval.keys():
      			if key == 'Error Message': print(company,'not done')
      			if key == 'Error Message': companies_left2.append(company)  
		 prices_retrieval = prices_retrieval['historical']
		 price = {}
		 price[company] = {}
		 metrics[company] = {}
		 for item in prices_retrieval:
 	 		price_date = item['date']
 	 		price[company][price_date] = item['close']
 			
		 price_DF = pd.DataFrame.from_dict(price)
		 price_DF = price_DF.sort_index(ascending=True)

		 price_DF['200_MA'] = price_DF[company].rolling(window=200,min_periods=1).mean()
		 price_DF['150_MA'] = price_DF[company].rolling(window=150,min_periods=1).mean()
		 price_DF['50_MA'] = price_DF[company].rolling(window=50,min_periods=1).mean()

		 price_DF['price_before60'] = price_DF[company].shift(60)
		 price_DF['price_before125'] = price_DF[company].shift(125)
		 price_DF['price_before250'] = price_DF[company].shift(250)
         
		 price_DF['RS_3months'] = (price_DF[company]/price_DF_idx['^GSPC'] )/ (price_DF['price_before60'] /price_DF_idx['price_before60'] ) *100        
		 price_DF['RS_halfYear'] = (price_DF[company]/price_DF_idx['^GSPC'] )/ (price_DF['price_before125'] /price_DF_idx['price_before125'] ) *100
		 price_DF['RS'] = (price_DF[company]/price_DF_idx['^GSPC'] )/ (price_DF['price_before250'] /price_DF_idx['price_before250'] ) *100	

		 price_DF_3 = price_DF[['RS_3months']]
		 price_DF_6= price_DF[['RS_halfYear']]
		 price_DF1=price_DF[['RS']]

		 price_DF1.rename(columns={"RS": company},inplace = True)
		 price_DF_3.rename(columns={"RS_3months": company},inplace = True)
		 price_DF_6.rename(columns={"RS_halfYear": company},inplace = True)
         
		 RS=RS.merge(price_DF1,left_index=True, right_index=True,how='outer')
		 RS_3=RS_3.merge(price_DF_3,left_index=True, right_index=True,how='outer')
		 RS_6=RS_6.merge(price_DF_6,left_index=True, right_index=True,how='outer')
		 	
		 metrics[company]['200 MA'] = price_DF['200_MA'][-1]
		 metrics[company]['150 MA'] = price_DF['150_MA'][-1]
		 metrics[company]['50 MA'] = price_DF['50_MA'][-1]
		 metrics[company]['200 MA_1mago'] = price_DF['200_MA'][-30]
		 metrics[company]['150 MA_1mago'] = price_DF['150_MA'][-30]
		 metrics[company]['200 MA_2mago'] = price_DF['200_MA'][-60]
		 metrics[company]['150 MA_2mago'] = price_DF['150_MA'][-60]
		 metrics[company]['52W_Low'] = price_DF[company][-252:].min()
		 metrics[company]['52W_High'] = price_DF[company][-252:].max()
		 metrics[company]['price'] = price_DF[company][-1]
		 metrics[company]['Relative Strength'] = price_DF['RS'][-1]
		 #Current Price is at least 30% above 52 week low (1.3*low_of_52week)
		 metrics[company]['Above_30%_low'] = metrics[company]['52W_Low'] *1.3
		 # Condition 7: Current Price is within 25% of 52 week high   (.75*high_of_52week)
		 metrics[company]['Within_25%_high'] = metrics[company]['52W_High'] * 0.75
	except:
		print("failed "+company)
		companies_left2.append(company)  

today_date= date.today()

# Play a notification sound when the loop run is done
import winsound
duration = 1000  # milliseconds
freq = 440  # Hz
winsound.Beep(freq, duration)
winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)


def find_RS (RS):
    
    RS_T = RS.T     
    columns = list(RS_T.columns.values.tolist())
    
    for col in columns:
        RS_T[col + '_RS'] = RS_T[col].rank(pct=True)
    
    RS_T=RS_T.loc[:,RS_T.columns.str.endswith('RS')]
    RS_T.columns = RS_T.columns.str.replace(r'_RS', '')
    RS_TT = RS_T.T
    RS_TT=RS_TT.dropna(thresh=10) 
    return RS_TT


RS_year = find_RS(RS)
RS_halfYear = find_RS(RS_6)
RS_3months = find_RS(RS_3)

#Export the file with all relative strength 
RS_year.to_csv('RS_year.csv')
RS_halfYear.to_csv('RS_halfyear.csv')
RS_3months.to_csv('RS_3months.csv')


metrics_DF = pd.DataFrame.from_dict(metrics)
metrics_DF = metrics_DF.T 
#to determine the rank percentil and see which are the 80% top performers
metrics_DF['pct_rank'] = metrics_DF['Relative Strength'].rank(pct=True)
metrics_DF = metrics_DF.T

today_date= date.today()
filename_allstocks='all_stocks_SP500_'+today_date.strftime("%d%m%y")+'.csv'

metrics_DF.to_csv(filename_allstocks)
print(metrics_DF)


filename_prices_SP500='prices_SP500_'+today_date.strftime("%d%m%y")+'.csv'


#Calculate the 8 conditions for ranking system, using Mark Minervini Trend Template
stocks = pd.read_csv(filename_allstocks)
stocks = stocks.T
stocks.columns = stocks.iloc[0]
stocks = stocks[1:]
stocks['condition1'] = np.where((stocks['price'] > stocks['200 MA']) & (stocks['price'] > stocks['150 MA']),1,0)

stocks['condition2'] = np.where(stocks['150 MA'] > stocks['200 MA'],1,0)
#3 The 200-day moving average line is trending up for 1 month 
stocks['condition3'] = np.where(stocks['200 MA'] > stocks['200 MA_1mago'],1,0)
stocks['condition4'] = np.where((stocks['50 MA'] > stocks['200 MA']) & (stocks['50 MA'] > stocks['150 MA']),1,0)
stocks['condition5'] = np.where(stocks['price'] > stocks['50 MA'],1,0)
#6 The current stock price is at least 30 percent above its 52-week low
stocks['condition6'] = np.where(stocks['price'] > stocks['Above_30%_low'],1,0)
#7 The current stock price is within at least 25 percent of its 52-week high.
stocks['condition7'] = np.where(stocks['price'] > stocks['Within_25%_high'],1,0)
#8 The relative strength ranking is above 80
stocks['condition8'] = np.where(stocks['pct_rank'] > 0.8,1,0)

stocks['score']=stocks['condition1']+stocks['condition2']+stocks['condition3']+stocks['condition4']+ \
    stocks['condition5']+stocks['condition6']+stocks['condition7']+stocks['condition8']

today_date= date.today()
filename='stocks_metrics_'+today_date.strftime("%d%m%y")+'.csv'

stocks = stocks.reset_index()
stocks.to_csv(filename,index=False)

#Export Stocks that meet all 8 conditions
selection = stocks[(stocks['condition1'] == True) & (stocks['condition2'] == True) & (stocks['condition3'] == True) & (stocks['condition4'] == True)
		& (stocks['condition5'] == True) & (stocks['condition6'] == True) & (stocks['condition7'] == True) & (stocks['condition8'] == True)]

filename_selection='selection_'+today_date.strftime("%d%m%y")+'.csv'
# selection.to_csv(filename_selection)

print(selection)
watchlist=selection.sort_values('pct_rank',ascending=False)['index'].tolist()
with open('watchlist.txt', 'w') as f:
    for item in watchlist:
        f.write("%s\n" % item)

# To print the start and end time so that we can find out how long did the program run
end = datetime.now()
print(start)
print(end)