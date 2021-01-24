#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tues Jan 22 08:24:58 2022

@author: operator
"""

# Import libraries
import os
os.chdir('/Users/operator/Documents/code/')
from qc3 import *
from xgboost import XGBClassifier
import time
import datetime
from sklearn import metrics
import time
from datetime import date

# Function to build signal
def retrieve_signal(col):
    
    return gaussian_filter1d(col, 5)

# Function to compute trading positions
def computation_algorithm(data):
    
    data.dropna(inplace = True)

    x = data.index

    sells, props = find_peaks(data['signal'], prominence = 1, wlen = 10)
    buys, props = find_peaks(-data['signal'], prominence = 1, wlen = 10) 
    
    positions = []

    # Compute baseline trade actions based on signal
    for idx, row in data.reset_index().iterrows():
  
        if idx in sells:
    
            positions.append(-1)
  
        elif idx in buys:
    
            positions.append(1)
    
        else:
    
            positions.append(0)
    
    positions[0] = 1
    positions[-1] = -1

    # Compute
    data['position'] = positions
        
    return data

# Function to perform analysismo
def build_positions(x):
    
    if x >= .03:
        
        return -1
    
    elif x <= -.03:
        
        return 1
    
    else:
        
        return 0

# Function to plot actions
def plot_actions():
    
    fig, ax = plt.subplots(figsize = (30, 15))
    data['price'].plot(ax = ax, lw = 1, label = 'price')
    data['signal'].plot(ax = ax, lw = 1, label = 'signal')
    ax.scatter(data.loc[data['position'] == 1].index, data.loc[data['position'] == 1]['price'], marker = '^', s = 100, color = 'red', label = 'buy')
    ax.scatter(data.loc[data['position'] == -1].index, data.loc[data['position'] == -1]['price'], marker = 'v', s = 100, color = 'green', label = 'sell')
    plt.title('Plot of Price and Signal w/ Market Actions')
    fig.legend(loc = 'upper right')
    fig.tight_layout();
        
# Function to plot returns
def plot_cumulative_returns():
    
    fig, ax = plt.subplots(figsize = (30, 15))
    ledger['total'].plot(ax = ax, lw = 1, label = 'Cumulative Total')
    ax.scatter(ledger.loc[ledger['pos'] == 1].index, ledger.loc[ledger['pos'] == 1]['total'], marker = '^', s = 100, color = 'red', label = 'buy')
    ax.scatter(ledger.loc[ledger['pos'] == -1].index, ledger.loc[ledger['pos'] == -1]['total'], marker = 'v', s = 100, color = 'green', label = 'sell')
    plt.title('Plot of Cumulative Returns')
    fig.legend(loc = 'upper right')
    fig.tight_layout();
        
# List targets of interest
tickers = ['BABA', 'CSTL', 'HLT', 'IEC', 'PYPL', 'PINS', 'UPLD', 'W', 'MSFT', 'SYK', 'AAPL', 'GOOGL', 'FCAU', 'IBM', 'USD', 'GLD', 'TMUS', 'T', 'S', 'CHTR', 'CBRE', 'CHCLY']

# Initialize
raw = pd.DataFrame()

# Iterate
for symbol in tickers:
    
    # Handle exceptions
    try:
        
        # Retrieve data
        df = pdr.get_data_yahoo(symbol, '2000-01-01', '2020-12-31').rename({'Adj Close': 'price'}, axis = 1)
        df = df.drop(['High', 'Low', 'Open', 'Close', 'Volume'], axis = 1)
    
    
        # Update
        df['ticker'] = symbol
        raw = raw.append(df)
        
    except:
        
        pass
        print('Mayday!! SNAFU DETECTED!!')
    
# Iterate for signalgen
r1 = pd.DataFrame()

for nm, grp in raw.groupby('ticker'):
    
    grp['signal'] = retrieve_signal(grp['price'])
    
    r1 = r1.append(grp)

# Apply function to erect trades
r2 = pd.DataFrame()

for nm, grp in r1.groupby('ticker'):
    
    grp1 = computation_algorithm(grp)
    
    r2 = r2.append(grp1)

# Initialize ledger
trades = 0
quant = 0
ledger = pd.DataFrame()

# Calculate trade activity
for nm, grp in r2.groupby('ticker'):

    date, price = grp.loc[grp['price'] != np.nan].index, grp.loc[grp['price'] != np.nan]['price']
    
    # Buy
    amount =  10000
    units = amount // grp['price'].loc[grp['price'] != np.nan]        
    
    for idx, row in grp.iterrows():
        
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
                
