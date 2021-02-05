# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# Import libraries
import pandas_datareader as pdr
import pandas as pd
import matplotlib.pyplot as plt
from xgboost import XGBClassifier, XGBRegressor
from sklearn import metrics
import numpy as np
from operator import itemgetter

# Get data
df = pdr.get_data_yahoo('SBUX', '2010-01-01', '2021-02-03').rename({'Adj Close': 'price'}, axis = 1)

# Calculate % change
df['pct_change'] = df['price'].pct_change()
df.dropna(inplace = True)

# Function to get trades
def optimal_trading(x, n):
    
    # Buy
    if x <= -n:
        
        return -1
    
    # Sell
    elif x >= n:
        
        return 1
    
    # Hold
    else:
    
        return 0
    
# Iterate to find optimal magnitude
df.reset_index(inplace = True)
scores = []

for n in np.arange(.05, .5, .05):

    df['trades'] = df['pct_change'].apply(lambda x: optimal_trading(x, n))
    df['trades'].iloc[0] = -1
    df['trades'].iloc[-1] = 1

    ledger = pd.DataFrame()
    
    # Initialize ledger
    trades = 0
    amount =  10000
    quant = 0
    
    # Calculate trade activity
    for idx, row in df.iterrows():

        date, price, units = row['Date'], row['price'], amount // row['price']
    
        if row['trades'] == -1:
        
            amount -= (units * price) 
            quant += units
            trades += 1
        
        # Hold
        elif row['trades'] == 0:
        
            pass
      
        # Sell
        elif row['trades'] == -1:
      
            amount += (units * price)
            quant -= units
            trades += 1

        ledger = ledger.append({'dt': date,
                                'price': price,
                                'trades': row['trades'],
                                'shares': quant,
                                'num_trades': trades,
                                'total': amount + (quant * price)}, ignore_index = True)
        
    scores.append((n, ledger['total'].iloc[-1]))

best = max(scores, key = itemgetter(1))