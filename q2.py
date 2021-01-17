#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 07:55:27 2021

@author: operator
"""

# Import libraries
from qc1 import *

# List targets of interest
tickers = ['BABA', 'CSTL', 'HLT', 'IEC', 'PYPL', 'PINS', 'UPLD', 'W', 'MSFT', 'SYK', 'AAPL', 'GOOGL', 'FCAU', 'IBM', 'USD', 'GLD', 'TMUS', 'T', 'S']

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
        
        raw = raw.append(t.data)
        out = out.append(t.ledger)
        
    except:
        
        pass
    
out1 = out.set_index('dt')

# Plot cumulative returns for portfolio
returns = out1.groupby(out1.index).agg({'total': 'sum'})

fig, ax = plt.subplots(figsize = (10, 6))
plt.title('Cumulative Returns for Portfolio')
plt.xlabel('Year')
plt.ylabel('$ (Millions)')
ax.plot(returns, lw = 1, color = 'green')

'''
    Portfolio Optimization
'''

p = portfolio(raw, out1)
p.plot_portfolio_stats()
p.plot_efficient_frontier()

cum_return = 0

for nm, grp in p.optimized_ledger.groupby('ticker'):
    
    