#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 06:33:33 2021

@author: operator
"""

# Import libraries
import os
import pandas_datareader as pdr
import pandas as pd
import matplotlib.pyplot as plt

# Class for investment trading
class stock:
    
    def __init__(self, symbol, start, end):
        
        self.symbol = symbol
        self.start = start
        self.end = end
        self.data = self.calculate_investment() 
        
    # Function to get trades
    def get_trade_actions(self, x):
    
        # Buy
        if x <= -.025:
        
            return -1
    
        # Sell
        elif x >= .025:
        
            return 1
    
        # Hold
        else:
    
            return 0
    
    # Function to compute trades
    def calculate_investment(self):
    
        df = pdr.get_data_yahoo(self.symbol, self.start, self.end).rename({'Adj Close': 'price'}, axis = 1)

        # Calculate % change
        df['pct_change'] = df['price'].pct_change()
    
        # Apply function
        df.dropna(inplace = True)
        df.reset_index(inplace = True)
            
        df['trades'] = df['pct_change'].apply(self.get_trade_actions)
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
                                    'ticker': self.symbol}, ignore_index = True)

        return ledger