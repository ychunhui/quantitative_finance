# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# Import libraries
import os
import pandas_datareader as pdr
import pandas as pd
import matplotlib.pyplot as plt
 
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

def calculate_investment(symbol):
    
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
                                'shares': quant,
                                'num_trades': trades,
                                'total': amount + (quant * price),
                                'ticker': symbol}, ignore_index = True)

    return ledger

# List targets of interest
tickers = ['BABA', 'CSTL', 'HLT', 'IEC', 'PYPL', 'PINS', 'UPLD', 'W', 'MSFT', 'SYK', 'AAPL', 'GOOGL', 'FCAU', 'IBM', 'USD', 'GLD', 'TMUS', 'T', 'S', 'CHTR', 'CBRE', 'CHCLY', 'SBUX']

data = pd.DataFrame()

for ticker in tickers:
    
    try:
        
        ledger = calculate_investment(ticker)
        ledger['ticker'] = ticker
        data = data.append(ledger)  
        
    except:
        
        pass
    
# Inspect
print(f"Data retrieved for {len(data['ticker'].unique())} tickers..")  

for nm, grp in data.groupby('ticker'):
    
    print(f'Analysis for {nm}..')
    print(grp.iloc[-1])
    
# Plot
totals = data.groupby('dt').agg({'total': 'sum'})

fig, ax = plt.subplots(figsize = (10, 6))
totals.plot(ax = ax, lw = 1)
plt.xlabel('Date') 
plt.ylabel('Returns ($ Millions)')
plt.title('Cumulative Returns for Portfolio')   
    
total = 0

print(f'\nOverall Analysis: {totals.index[0]} - {totals.index[-1]}\n')

for nm, grp in data.groupby('ticker'):
    
    total += grp['total'].iloc[-1]
    
    print(f"Final Total {nm}- ${grp['total'].iloc[-1]}")
    
print('\nTotal Investment $21,000')
print(f'Final Total-     ${round(total, 2)}')





