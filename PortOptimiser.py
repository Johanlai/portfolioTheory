# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 20:58:41 2023

@author: JHL
"""

import portfolioTheory as pt
import yftickers as ticks
import datetime as dt

def optimisePortfolio(tickers, start, end, OptBy= 'MaxSharpe', logReturns = True, threshold=0.8, drop_extremes=True, excess=5, dateRange=None):
    portfolio = pt.Portfolio(tickers, start, end)
    portfolio.getData()
    portfolio.cleanData(threshold=threshold, drop_extremes=drop_extremes, excess=excess, dateRange=dateRange)
    portfolio.calculate_stats(logReturns=logReturns)

tickers = ticks.ftse100
start=dt.datetime(2000,1,1)
end=dt.datetime(2023,1,1)
threshold=0.9

optimisePortfolio(tickers, start, end, logReturns=False)