# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# Import libraries
import os
os.chdir('/Users/operator/Documents/')
from qf import *
import matplotlib.pyplot as plt

# List targets of interest
tickers = ['AG', 'BABA', 'CSTL', 'HLT', 'IEC', 'PYPL', 'PINS', 'UPLD', 'W', 'MSFT', 'SYK', 'SCCO', 'AAPL', 'GOOGL', 'FCAU', 'IBM', 'USD', 'GLD', 'TMUS', 'T', 'S', 'CHTR', 'CBRE', 'CHCLY', 'SBUX']
portfolio = {}

for ticker in tickers:
    
    s = stock(ticker, '2000-01-01', '2021-02-01')
    portfolio[ticker] = s.data
    
# Analyze
total = 0

print(f"\nOverall Analysis: {data.iloc[0]['dt']} - {data.iloc[-1]['dt']}\n")

for k, v in portfolio.items():
        
    total += v['total'].iloc[-1]
    
    print(f"Final Total {k}- ${round(v['total'].iloc[-1], 2)}")
    
print('\nTotal Investment $23,000')
print(f'Final Total-     ${round(total, 2)}')

df = pd.DataFrame()

for k, v in portfolio.items():

    df = df.append(v)  

# Plot
totals = df.groupby('dt').agg({'total': 'sum'})

fig, ax = plt.subplots(figsize = (10, 6))
totals.plot(ax = ax, lw = 1)
plt.xlabel('Date') 
plt.ylabel('Returns ($ Millions)')
plt.title('Cumulative Returns for Portfolio') 