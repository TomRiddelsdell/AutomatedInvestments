# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 19:33:51 2017

@author: Tom
"""
import pandas as pd
#import quandl
from pandas_datareader.data import DataReader

#Auth = "d85AxYgsEaWPyhx_k2ZL"

def yahoo_prices(symbols, start_date, verbose = True):
    ticker_df_list = []
    start_dates = {};
    for index, row in symbols.iterrows(): 
        try:
            data = DataReader(row.Ticker, 'yahoo', start_date)
            data['Ref'] = row.Ticker 
            data = data.loc[:, ['Ref', 'Adj Close']]
            data.rename(columns={'Adj Close': 'Price'}, inplace=True)
            if verbose:
                print("{}: Historical Perf: {}".format(row.Ticker, data.tail(1).iloc[0]['Price']/data.head(1).iloc[0]['Price']-1))            
            ticker_df_list.append(data)
            start_dates[row.Ticker] = data.head(1).index[0]
        except Exception as e:
            if verbose:
                print("No data for ticker %s\n%s" % (row.Ticker, str(e)))    
    df = pd.concat(ticker_df_list)   
    cell= df[['Ref','Price']] 
    return cell.pivot(columns='Ref'), start_dates

"""    
def get_pricing(symbols, start_date, verbose = True):
    ticker_df_list = []
    for index, row in symbols.iterrows(): 
        try:
            r = quandl.get(row.Quandl.format(row.Ticker), start_date=start_date, authtoken=auth)
            r['Ref'] = row.Ticker 
            r = r.loc[:, ['Ref', row.PriceColumn]]
            r.rename(columns={row.PriceColumn: 'Price'}, inplace=True)
            ticker_df_list.append(r)
            if verbose:
                print("Obtained data for ticker %s" % row.Ticker)
        except Exception as e:
            if verbose:
                print("No data for ticker %s\n%s" % (row.Ticker, str(e)))    
    df = pd.concat(ticker_df_list)   
    cell= df[['Ref','Price']]     
    #cell.reset_index().sort(['Ref', 'Date'], ascending=[1,0]).set_index('Ref')
    return cell.pivot(columns='Ref')['Price']
"""