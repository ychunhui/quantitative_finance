#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 12:00:00 2020

@author: operator
"""

# Import libraries
from qc1 import *
from xgboost import XGBClassifier
import time
import datetime
from sklearn import metrics
import time
from datetime import date

# List targets of interest
tickers = ['BABA', 'CSTL', 'HLT', 'IEC', 'PYPL', 'PINS', 'UPLD', 'W', 'MSFT', 'SYK', 'AAPL', 'GOOGL', 'FCAU', 'IBM', 'USD', 'GLD', 'TMUS', 'T', 'S', 'CHTR']

'''
    Parameters-
    
        self.ticker = ticker
        self.start = start
        self.end = end
        self.data = self.retrieve_prices()
        
        self.retrieve_signal()
        self.positions = self.compute_trades()
        self.ledger = self.build_ledger()
        
    Functions-
    
        retrieve_prices()
        retrieve_signals()
        compute_trades()
        build_ledger()
        plot_actions()
        plot_cumulative_returns()
'''

# Employ class actions
t = ticker(tickers[1], '2010-01-01', '2021-01-15')

# Inspect
t.data
t.positions    
t.ledger.tail()

t.plot_actions()
t.plot_cumulative_returns()

# Build portfolio
raw = pd.DataFrame()
out = pd.DataFrame()
    
for symbol in tickers:
    
    try:
        
        t = ticker(symbol, '2010-01-01', '2021-01-01')
        
        t.data['ticker'] = symbol
        t.ledger['ticker'] = symbol
        t.ledger = t.ledger.set_index('dt')
        raw = raw.append(t.data)
        out = out.append(t.ledger)
        
    except:
        
        pass

'''
    Machine Learning
'''

predictions = pd.DataFrame()

def convert_date(x):
    
    return (x - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
    
for symbol in tickers:
    
    try:
        
        dat = out.loc[out['ticker'] == symbol]
        dat['dt'] = [convert_date(i) for i in dat.index]
        dat.reset_index(drop = True)
        
        train = dat[:'2018']
        
        m = XGBClassifier(random_state = 100)
        m.fit(train[['dt', 'price']], train['pos'])
        
        dat['pos_pred'] = m.predict(dat[['dt', 'price']])
  
        dat.iloc[0]['pos_pred'] = 1
        dat.iloc[-1]['pos_pred'] = -1
        
        predictions = predictions.append(dat)
        
    except:
        
        pass

preds = pd.DataFrame()
    
for nm, grp in predictions.groupby('ticker'):

    amount = 10000
    
    # Buy
    units = int(amount / grp.iloc[0]['price'])
    quant = 0
    trades = 0
    
    for idx, row in grp.iterrows():
        
        date, price = row['dt'], row['price']
        
        if row['pos'] == 1:
            
            amount -= (units * price) 
            quant += units
            trades += 1
    
        # Hold
        elif row['pos'] == 0:
        
            pass
      
        # Sell
        elif row['pos'] == -1:
      
            amount += (units * price)
            quant -= units
            trades += 1
      
        preds = preds.append({'price': price,
                              'pos': row['pos'],
                              'shares': quant,
                              'num_trades': trades,
                              'total': amount + (quant * price),
                              'ticker': nm}, ignore_index = True)

returns = 0
        
for nm, grp in preds.groupby('ticker'):
    
    total = grp.iloc[-1]['total']
    
    returns += total
