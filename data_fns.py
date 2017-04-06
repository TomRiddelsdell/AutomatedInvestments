# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 19:33:51 2017

@author: Tom
"""
import pandas as pd
from yahoo_finance import Share
#import quandl
from pandas_datareader.data import DataReader

#Auth = "d85AxYgsEaWPyhx_k2ZL"

def yahoo_prices(symbols, start_date, verbose = True):
    fixings = {}
    info = {}
    for index, row in symbols.iterrows(): 
        try:
            data = DataReader(row.Ticker, 'yahoo', start_date).loc[:, 'Adj Close'].rename(row.Ticker)
            if verbose:
                print("{}: Historical Perf: {}".format(row.Ticker, data[0]/data[-1]))
            fixings[row.Ticker] = data

            share_info = Share(row.Ticker)
            info[row.Ticker] = {'start_date':data.head(1).index[0], 'currency':share_info.get_currency()}
        except Exception as e:
            if verbose:
                print("No data for ticker %s\n%s" % (row.Ticker, str(e)))    
    df = pd.DataFrame(fixings).reset_index()
    df.index = df['Date']
    del df['Date']
    return df, info

