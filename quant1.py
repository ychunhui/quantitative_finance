#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tues Jan 22 08:24:58 2022

@author: operator
"""

# Import libraries
import os
os.chdir('/Users/operator/Documents/code/')
from quantfuncs import *
import pandas as pd
import pandas_datareader as pdr
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import numpy as np

# List targets of interest
tickers = ['BABA', 'CSTL', 'HLT', 'IEC', 'PYPL', 'PINS', 'UPLD', 'W', 'MSFT', 'SYK', 'AAPL', 'GOOGL', 'FCAU', 'IBM', 'USD', 'GLD', 'TMUS', 'T', 'S', 'CHTR', 'CBRE', 'CHCLY', 'SBUX']

data = pd.DataFrame()

# Iterate
for s in tickers:
    
    # Handle exceptions
    try:
        
        # Retrieve data
        df = pdr.get_data_yahoo(s, '2000-01-01', '2020-12-31').rename({'Adj Close': 'price'}, axis = 1)
        df = df.drop(['High', 'Low', 'Open', 'Close', 'Volume'], axis = 1)
    
        # Update
        df['ticker'] = s
                
        data = data.append(df)
        
    except:
        
        pass

'''
    SMA strategy
'''

sma = pd.DataFrame()

for nm, grp in data.groupby('ticker'):
    
    grp['short'] = grp['price'].rolling(window = 7).mean()
    grp['long'] = grp['price'].rolling(window = 21).mean()
    
    # Initialize the `signals` DataFrame with the `signal` column
    signs = pd.DataFrame(index = grp.index)
    signs['signal'] = 0.0

    # Create signals
    signs['signal'][7:] = np.where(grp['short'][7:] > grp['long'][7:], 1.0, 0.0)   

    # Generate trading orders
    grp['position'] = signs['signal'].diff()
    
    sma = sma.append(grp)
    
    # Visualize
    fig, ax = plt.subplots(figsize = (10, 6))
    plt.xlabel('year')
    plt.ylabel('$')
    ax.plot(grp['price'], lw = 1, color = 'dodgerblue')
    
    #ax.plot(signs['signal'], lw = 1, color = 'red')
    
    ax.scatter(grp.loc[grp['position'] == -1].index, grp.loc[grp['position'] == -1]['price'], marker = 'v', label = 'buy', color = 'red')
    ax.scatter(grp.loc[grp['position'] == 1].index, grp.loc[grp['position'] == 1]['price'], marker = '^', label ='sell', color = 'green')
        
'''
    Calculate ledger
'''

ledger = pd.DataFrame()

# Calculate trade activity
for nm, grp in sma.groupby('ticker'):
    
    grp.dropna(inplace = True)
    grp.reset_index(inplace = True)
    
    # Initialize ledger
    trades = 0
    amount =  10000
    quant = 0
            
    for idx, row in grp.iterrows():
    
        date, price, units = row['Date'], row['price'], amount // row['price']
    
        if row['position'] == 1:
      
            amount -= (units * price) 
            quant += units
            trades += 1
        
        # Hold
        elif row['position'] == 0:
        
            pass
      
        # Sell
        elif row['position'] == -1:
      
            amount += (units * price)
            quant -= units
            trades += 1

        ledger = ledger.append({'dt': date,
                                'price': price,
                                'pos': row['position'],
                                'shares': quant,
                                'num_trades': trades,
                                'total': amount + (quant * price),
                                'ticker': nm}, ignore_index = True)

