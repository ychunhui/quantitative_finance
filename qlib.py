#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 07:54:43 2021

@author: operator
"""

# Import libraries
import pandas_datareader.data as pdr
import pandas as pd
import numpy as np
from pylab import mpl, plt
mpl.rcParams['savefig.dpi'] = 500
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['figure.figsize'] = [10, 6]
import warnings
warnings.filterwarnings('ignore')
plt.style.use('fivethirtyeight')
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
from sklearn.model_selection import train_test_split
from sklearn.metrics import *

try:
    
    from xgboost import XGBClassifier

except:
    
    print('XGB unavailable..')
    
try:
    
    from fbprophet import Prophet
    
except:
    
    print('Prophet forecasting unavailable..')

class ticker:
    
    def __init__(self, ticker, start, end, capital = 10000):

        self.ticker = ticker
        self.start = start
        self.end = end
        self.data = self.retrieve_prices()
        self.retrieve_signal()
        self.positions = self.compute_trades()
        self.ledger = self.build_ledger()

    # Function to get data
    def retrieve_prices(self):
        
        df = pdr.get_data_yahoo(self.ticker, self.start, self.end).rename({'Adj Close': 'price'}, axis = 1)

        return df

    # Function to build signal
    def retrieve_signal(self):

        self.data['signal'] = gaussian_filter1d(self.data['price'], 5)

    # Function to compute trading positions
    def compute_trades(self):
        
        self.data.dropna(inplace = True)

        x = self.data.index

        sells, props = find_peaks(self.data['signal'], prominence = 1, wlen = 250)
        buys, props = find_peaks(-self.data['signal'], prominence = 1, wlen = 250) 
    
        positions = []

        # Compute baseline trade actions based on signal
        for idx, row in self.data.reset_index().iterrows():
  
            if idx in sells:
    
                positions.append(-1)
  
            elif idx in buys:
    
                positions.append(1)
    
            else:
    
                positions.append(0)
    
        positions[0] = 1
        positions[-1] = -1

        # Compute
        self.data['position'] = positions
        self.data['pct_change'] = self.data['price'].pct_change()
        self.data['delta'] = self.data['signal'].pct_change()
        
        return positions

    # Function to calculate balances
    def build_ledger(self):

        ledger = pd.DataFrame()

        # Calculate trade activity
        for idx, row in self.data.reset_index().iterrows():
    
            date, price = row['Date'], row['price']
    
            if idx == 0:
        
                # Initialize ledger
                trades = 0
                amount =  10000
                quant = 0
    
                # Buy
                units = int(amount / price)
    
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
                                    'total': amount + (quant * price)}, ignore_index = True)
            
        return ledger

    # Function to plot actions
    def plot_actions(self):

        fig, ax = plt.subplots(figsize = (30, 15))
        self.data['price'].plot(ax = ax, lw = 1, label = 'price')
        self.data['signal'].plot(ax = ax, lw = 1, label = 'signal')
        ax.scatter(self.data.loc[self.data['position'] == 1].index, self.data.loc[self.data['position'] == 1]['price'], marker = '^', s = 100, color = 'red', label = 'buy')
        ax.scatter(self.data.loc[self.data['position'] == -1].index, self.data.loc[self.data['position'] == -1]['price'], marker = 'v', s = 100, color = 'green', label = 'sell')
        plt.title('Plot of Price and Signal w/ Market Actions')
        fig.legend(loc = 'upper right')
        fig.tight_layout();
        
    # Function to plot returns
    def plot_cumulative_returns(self):

        fig, ax = plt.subplots(figsize = (30, 15))
        self.ledger['total'].plot(ax = ax, lw = 1, label = 'Cumulative Total')
        ax.scatter(self.ledger.loc[self.ledger['pos'] == 1].index, self.ledger.loc[self.ledger['pos'] == 1]['total'], marker = '^', s = 100, color = 'red', label = 'buy')
        ax.scatter(self.ledger.loc[self.ledger['pos'] == -1].index, self.ledger.loc[self.ledger['pos'] == -1]['total'], marker = 'v', s = 100, color = 'green', label = 'sell')
        plt.title('Plot of Cumulative Returns')
        fig.legend(loc = 'upper right')
        fig.tight_layout();

'''
    Portfolio Optimization
'''

# Class to manage portfolio as a whole    
class portfolio:
    
    def __init__(self, data):
        
        self.portfolio = pd.DataFrame()
        self.p_ret = [] 
        self.p_vol = [] 
        self.p_weights = [] 

        self.data = data
        
        for nm, grp in self.data.groupby('ticker'):
    
            self.portfolio[nm] = grp['price']
    
        self.cov_mat = self.portfolio.pct_change().apply(lambda x: np.log(1 + x)).cov()
        self.corr_mat = self.portfolio.pct_change().apply(lambda x: np.log(1 + x)).corr()
        
        self.rf = 0.01 

        # Equally weighted portfolio variance
        self.w = 1/len(self.portfolio.columns)

        self.port_var = self.cov_mat.mul(self.w, axis = 0).mul(self.w, axis = 1).sum().sum()

        # Yearly returns for individual companies
        self.ind_er = self.portfolio.resample('Y').last().pct_change().mean()

        # Volatility - annual standard deviation. We multiply by 250 because there are 250 trading days/year.
        self.ann_sd = self.portfolio.pct_change().apply(lambda x: np.log(1 + x)).std().apply(lambda x: x * np.sqrt(250))

        # Creating a table for visualising returns and volatility of assets
        self.assets = pd.concat([self.ind_er, self.ann_sd], axis = 1) 
        self.assets.columns = ['return', 'volatility']
        
        self.num_assets = len(self.portfolio.columns)
        self.num_portfolios = 10000

    # Function to plot
    def plot_portfolio_stats(self):
            
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize = (10, 6))
        plt.title('Asset Volatility')
        plt.xlabel('Ticker')
        plt.ylabel('Volatility')
        ax.bar(self.assets.index, self.assets['volatility'])
        plt.xticks(rotation = 90)
        fig.tight_layout();

        fig1, ax = plt.subplots(figsize = (10, 6))
        plt.title('Yearly Average Returns')
        plt.xlabel('Ticker')
        plt.ylabel('Volatility')
        ax.bar(self.assets.index, self.assets['return'], color = 'orange')
        plt.xticks(rotation = 90)
        fig.tight_layout();

    # Function to find optima
    def get_optimal_weights(self):

        for p in range(self.num_portfolios):
    
            weights = np.random.random(self.portfolio.shape[1])
            weights = weights/np.sum(weights)
            self.p_weights.append(weights)
            returns = np.dot(weights, self.ind_er) 
            self.p_ret.append(returns)
            var = self.cov_mat.mul(weights, axis = 0).mul(weights, axis = 1).sum().sum()
            sd = np.sqrt(var) 
            ann_sd = sd * np.sqrt(250) 
            self.p_vol.append(ann_sd)

            self.d = {'return': self.p_ret, 'volatility': self.p_vol}

        for counter, symbol in enumerate(self.portfolio.columns.tolist()):
    
            #print(counter, symbol)
            self.d[symbol] = [w[counter] for w in self.p_weights]
    
        self.toomany = pd.DataFrame(self.d)

        self.min_vol_port = self.toomany.iloc[self.toomany['volatility'].idxmin()]

        self.optimal_risky_port = self.toomany.iloc[((self.toomany['return'] - self.rf) / self.toomany['volatility']).idxmax()]

    def plot_efficient_frontier(self):
        
        self.toomany.plot.scatter(x = 'volatility', y = 'return', marker = 'o', s = 10, alpha = 0.3, grid = True, figsize = [10, 6])
        plt.scatter(self.min_vol_port[1], self.min_vol_port[0], color = 'r', marker = '*', s = 500)
        plt.scatter(self.optimal_risky_port[1], self.optimal_risky_port[0], color = 'g', marker = '*', s = 500)
        plt.title('Graphing Portfolio Efficient Frontier')
    