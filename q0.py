# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# Import libraries
import pandas_datareader as pdr
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pdr.get_data_yahoo('SBUX', '2010-01-01', '2021-02-03').rename({'Adj Close': 'price'}, axis = 1)

# Calculate % change
df['pct_change'] = df['price'].pct_change()

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
                            'total': amount + (quant * price)}, ignore_index = True)
    
# Plot
fig, ax = plt.subplots(figsize = (10, 6))
ax.plot(df['price'], lw = 1)
plt.title('Price for Starbucks Stock: 2010-2021')
plt.xlabel('Year')
plt.ylabel('Price ($)')

fig, ax = plt.subplots(figsize = (10, 6))
ax.plot(df['price'], lw = 1)
ax.scatter(df.loc[df['trades'] == -1].index, df.loc[df['trades'] == -1]['price'], marker = '^', color = 'red', label = 'buy')
ax.scatter(df.loc[df['trades'] == 1].index, df.loc[df['trades'] == 1]['price'], marker = 'v', color = 'green', label = 'sell')
plt.title('Price for Starbucks Stock: 2010-2021')
plt.xlabel('Year')
plt.ylabel('Price ($)')
plt.legend()

fig, ax = plt.subplots(figsize = (10, 6))
ax.plot(ledger['dt'], ledger['total'], lw = 1, color = 'green')
plt.title('Cumulative Return for Trading Starbucks Stock: 2010-2021')
plt.xlabel('Year')
plt.ylabel('Price ($)')
plt.legend()
