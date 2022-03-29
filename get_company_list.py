# -*- coding: utf-8 -*-
"""
Created on Thu May 27 20:12:53 2021

@author:  Coen (Chin Hooi) Yap
"""

import requests
import pandas as pd 
import time
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta 
import shutil
import urllib.request as request
from contextlib import closing
from yahoo_fin import stock_info as si
from yahoo_fin import *
import yfinance as yf



# Download Nasdaq and S&P listed stocks 
with closing(request.urlopen('ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt')) as r:
    with open('file', 'wb') as f:
        shutil.copyfileobj(r, f)

import os
thisFile = "file"
base = os.path.splitext(thisFile)[0]
os.remove("file.txt")
os.rename(thisFile, base + ".txt")

with closing(request.urlopen('ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt')) as r:
    with open('file', 'wb') as f:
        shutil.copyfileobj(r, f)

thisFile = "file"
base = os.path.splitext(thisFile)[0]
os.remove("file2.txt")
os.rename(thisFile, base + "2.txt")


# Load them into data frame. Repeat process for both files
x=pd.read_csv('file.txt',sep="|")


# Clean the stock list and remove tickers that we are not interested.
x['Security Name']=x['Security Name'].str.lower()
x['Security Name']=x['Security Name'].astype(str)

#filter test stocks, next shares, etf, financial status
x=x[(x['Test Issue']=='N')&(x['Financial Status']=='N')&
    (x['ETF']=='N')&(x['NextShares']=='N')&
    (~x['Security Name'].str.contains('warrant'))&
    (~x['Security Name'].str.contains('- unit'))&
    (~x['Security Name'].str.contains('- right'))&
    (~((x['Security Name'].str.contains('preferred'))&(x['Symbol']!='PFBC')))&
    (~x['Security Name'].str.contains('representing'))&
    (~x['Security Name'].str.contains('%'))&
    (~x['Security Name'].str.contains('nonvoting'))&
    (~x['Security Name'].str.contains('due 2'))&
    (~((x['Security Name'].str.contains('end fund'))|(x['Security Name'].str.contains('return fund'))|(x['Security Name'].str.contains('income fund'))))
    ]


all_nas=x['Symbol'].tolist()

y=pd.read_csv('file2.txt',sep="|")
y['Security Name']=y['Security Name'].str.lower()
y['Security Name']=y['Security Name'].astype(str)

#filter test stocks, next shares, etf, financial status
y=y[(y['Test Issue']=='N')&#(y['Financial Status']=='N')&
    (y['ETF']=='N')&#(y['NextShares']=='N')&
    (~y['Security Name'].str.contains('warrant'))&
    (~y['Security Name'].str.contains('- unit'))&
    (~y['Security Name'].str.contains('- right'))&
    (~((y['Security Name'].str.contains('preferred'))&(y['NASDAQ Symbol']!='PFBC')))&
    (~y['Security Name'].str.contains('representing'))&
    (~y['Security Name'].str.contains('%'))&
    (~y['Security Name'].str.contains('nonvoting'))&
    (~y['Security Name'].str.contains('due 2'))&
    (~((y['Security Name'].str.contains('end fund'))|(y['Security Name'].str.contains('return fund'))|(y['Security Name'].str.contains('income fund'))))
    ]


all_nas=x['Symbol'].tolist()

all_other = y['NASDAQ Symbol'].tolist()



# Also download file from wikipedia on the latest tickers from all 3 different indices (S&P, Nasdaw, Dow Jones)
def get_sp500():
	sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
	sp500_tickers = sp500_tickers[0]

	tickers = sp500_tickers['Symbol'].values.tolist()
	return tickers

def get_nas100():
	nas100_tickers = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100#Components')
	nas100_tickers = nas100_tickers[3]

	tickers = nas100_tickers['Ticker'].values.tolist()
	return tickers

def get_dj30():
	dj30_tickers = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')
	dj30_tickers = dj30_tickers[1]

	tickers = dj30_tickers['Symbol'].values.tolist()
	return tickers

companies_nas=get_nas100()
companies_dj=get_dj30()
companies = get_sp500()



#join all companies list together, remove duplicates, replace "." with "-" for BRK.B and BF.B
companies.extend(companies_nas)
companies.extend(companies_dj)
companies.extend(all_nas)
# companies.extend(all_other)
companies = [sub.replace('.', '-') for sub in companies]
companies = list(set(companies))
companies_left=[]


# =============================================================================
# get live price to filter away penny stocks
# =============================================================================

from yahoo_fin import stock_info as si
from yahoo_fin import *


dict_comp={}
count=0
companies_left=[]
today_date= date.today()


for company in companies:
    count=count+1
    # time.sleep(3)
    print(count, " ", company)
    try:
        price_DF = yf.download(company, start="2022-01-01", end=today_date)
        price = price_DF['Close'][-1]
        dict_comp[company] = price
    except:
        companies_left.append(company)
        print("failed ", company)
        pass

 
price_check=pd.DataFrame.from_dict(dict_comp,orient='index',columns=['price'])
all_stocks=price_check.reset_index()  

test=all_stocks[all_stocks['price']>=10]

today_date= date.today()
filename='price_check_'+today_date.strftime("%d%m%y")+'.csv'
test.to_csv(filename)

companies=test['index'].tolist()
