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
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn import metrics
 
# Function to get trades
def get_trade_actions(x):
    
    # Buy
    if x <= -.05:
        
        return -1
    
    # Sell
    elif x >= .05:
        
        return 1
    
    # Hold
    else:
    
        return 0
    
# List targets of interest
tickers = ['BABA', 'CSTL', 'HLT', 'IEC', 'PYPL', 'PINS', 'UPLD', 'W', 'MSFT', 'SYK', 'AAPL', 'GOOGL', 'FCAU', 'IBM', 'USD', 'GLD', 'TMUS', 'T', 'S', 'CHTR', 'CBRE', 'CHCLY', 'SBUX']
data = pd.DataFrame()

# Load data
for symbol in tickers:
    
    try:
        
        df = pdr.get_data_yahoo(symbol, '2010-01-01', '2021-02-03').rename({'Adj Close': 'price'}, axis = 1)

        # Calculate % change
        df['pct_change'] = df['price'].pct_change()
    
        # Apply function
        df.dropna(inplace = True)
        df.reset_index(inplace = True)

        df['trades'] = df['pct_change'].apply(get_trade_actions)
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
                                    'total': amount + (quant * price),
                                    'ticker': symbol}, ignore_index = True)

        data = data.append(ledger)
        
    except:
        
        pass

# Sum up totals
stocks = data.groupby('dt').agg({'total': 'sum'})

fig, ax = plt.subplots(figsize = (10, 6))
ax.plot(ledger['dt'], ledger['total'], lw = .5, color = 'green')
plt.title('Cumulative Return for Portfolio: 2010-2021')
plt.xlabel('Year')
plt.ylabel('Price ($)')

'''
    Machine Learning
'''

pledger = pd.DataFrame()

# Load data
for symbol in tickers:
    
    try:
        
        df = pdr.get_data_yahoo(symbol, '2010-01-01', '2021-02-03').rename({'Adj Close': 'price'}, axis = 1)
        df.reset_index()
        
        df['Date'] = df.index
        df['Date'] = df['Date'].apply(lambda x: (x - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'))
        
        # Calculate % change
        df['pct_change'] = df['price'].pct_change()
        
        df.dropna(inplace = True)
        
        m = XGBRegressor(random_state = 100)
        m.fit(df[['Date']], df[['price']])
        
        df['predicted_price'] = m.predict(df[['Date']])
        df['predicted_change'] = df['predicted_price'].pct_change()
        df['predicted_trades'] = df['predicted_change'].apply(get_trade_actions)
        
        df['predicted_trades'].iloc[0] = -1
        df['predicted_trades'].iloc[-1] = 1
    
        # Initialize ledger
        trades = 0
        amount =  10000
        quant = 0
    
        # Calculate trade activity
        for idx, row in df.iterrows():

            date, price, units = row['Date'], row['price'], amount // row['price']
    
            if row['predicted_trades'] == -1:
        
                amount -= (units * price) 
                quant += units
                trades += 1
        
            # Hold
            elif row['predicted_trades'] == 0:
        
                pass
      
            # Sell
            elif row['predicted_trades'] == -1:
      
                amount += (units * price)
                quant -= units
                trades += 1

            pledger = pledger.append({'dt': date,
                                      'price': price,
                                      'predicted_trades': row['predicted_trades'],
                                      'shares': quant,
                                      'num_trades': trades,
                                      'total': amount + (quant * price),
                                      'ticker': symbol}, ignore_index = True)
    except:
        
        pass
    