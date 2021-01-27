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
from xgboost import XGBClassifier, XGBRegressor
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

def predcomps(data):
    
    data.dropna(inplace = True)

    x = data.index

    sells, props = find_peaks(data['pred_signal'], prominence = 1, wlen = 10)
    buys, props = find_peaks(-data['pred_signal'], prominence = 1, wlen = 10) 
    
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
    data['pred_position'] = positions
        
    return data

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

r3 = pd.DataFrame()

for nm, grp in r2.groupby('ticker'):
    
    grp.reset_index(inplace = True)
    grp['dt'] = grp['Date'].apply(lambda x: (x - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'))
    
    r = XGBRegressor(random_state = 100)
    r.fit(grp[['dt', 'price']], grp['signal'])
    
    grp['pred_signal'] = r.predict(grp[['dt', 'price']])
    
    r3 = r3.append(predcomps(grp))
    
r4 = predcomps(r3)

#r4.loc[r4['position'] != r4['pred_position']][['price', 'position', 'pred_position']]

ledger = pd.DataFrame()

# Calculate trade activity
for nm, grp in r4.groupby('ticker'):
    
    # Initialize ledger
    trades = 0
    amount =  10000
    quant = 0
        
    ptrades = 0
    pamount = 10000
    pquant = 0
        
    # Buy
    units = int(amount / price)
            
    for idx, row in grp.iterrows():
    
        date, price = row['Date'], row['price']
    
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

        if row['pred_position'] == 1:
      
            pamount -= (units * price) 
            pquant += units
            ptrades += 1
        
        # Hold
        elif row['pred_position'] == 0:
        
            pass
      
        # Sell
        elif row['pred_position'] == -1:
      
            pamount += (units * price)
            pquant -= units
            ptrades += 1
        
        ledger = ledger.append({'dt': date,
                                'price': price,
                                'pos': row['position'],
                                'shares': quant,
                                'num_trades': trades,
                                'total': amount + (quant * price),
                                'pred_pos': row['pred_position'],
                                'pred_trades': ptrades,
                                'pred_total': pamount + (pquant * price),
                                'ticker': nm}, ignore_index = True)
        
total = 0
ptotal = 0

for nm, grp in ledger.groupby('ticker'):
    
    total += grp['total'].iloc[-1]
    ptotal += grp['pred_total'].iloc[-1]
    
