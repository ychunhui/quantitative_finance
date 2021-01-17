#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 12:00:00 2022

@author: operator
"""

# Import libraries
from qc1 import *
from xgboost import XGBClassifier
import time
import datetime
from sklearn import metrics

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
    
    cum_return += grp['total'].iloc[-1]
    
# Plot cumulative returns for portfolio
returns1 = p.optimized_ledger.groupby(p.optimized_ledger.dt).agg({'total': 'sum'}) #.reset_index(drop = True)

fig, ax = plt.subplots(figsize = (10, 6))
plt.title('Cumulative Returns for Optimized Portfolio')
plt.xlabel('Year')
plt.ylabel('$ (Millions)')
ax.plot(returns, lw = 1, color = 'green', label = 'Unweighted')
ax.plot(returns1, lw = 1, label = 'Efficient Frontier', color = 'red')
plt.legend()

'''
    Machine Learning
'''

out1['dt'] = [pd.to_datetime(i, unit = 'ms', origin = 'unix') for i in out1.index] 
out1['dt'] = out1.dt.apply(lambda x: time.mktime(x.timetuple()))    

for nm, grp in out1.groupby('ticker'):
    
    try:
        
        xtrain = grp['2018':][['dt', 'price']]
        ytrain = grp['2018':]['pos']
    
        xval = grp[:'2018'][['dt', 'price']]
        yval = grp[:'2018']['pos']
    
        m = XGBClassifier(random_state = 100)
        m.fit(xtrain, ytrain)
    
        preds = m.predict(xval)
    
        score = metrics.accuracy_score(preds, yval)
    
        print(f'Model Evaluation for {nm}- {round(score, 2) * 100}%')
        print('AUC for Model-')
        print(metrics.classification_report(preds, yval))
        
    except:
        
        print('Catastrophic Failure Detected! Run!!!')
    
