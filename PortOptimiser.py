# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 20:58:41 2023

@author: JHL
"""
import numpy as np
import pandas as pd
import portfolioTheory as pt
import yftickers as ticks
import datetime as dt
from dateutil.relativedelta import relativedelta

def optimisePortfolio(tickers, start, end, optimiseBy= 'MaxSharpe', riskFreeRate=0, contraintSet=(0,1), logReturns = True, threshold=0.8, drop_extremes=True, excess=5, dateRange=None):
    portfolio = pt.Portfolio(tickers, start, end)
    portfolio.getData()
    portfolio.cleanData(threshold=threshold, drop_extremes=drop_extremes, excess=excess, dateRange=dateRange)
    portfolio.calculate_stats(logReturns=logReturns)
    if logReturns:
        meanReturns = portfolio.logReturns.mean()
    else:
        meanReturns = portfolio.returns.mean()
    covMatrix = portfolio.covMatrix
    if optimiseBy=='MaxSharpe':
        def optimiser(meanReturns,covMatrix, riskFreeRate=riskFreeRate, contraintSet=contraintSet):
            pt.maxSharpeRatio(meanReturns,covMatrix, riskFreeRate=riskFreeRate, contraintSet=contraintSet)
    if optimiseBy=='MinVariance':
        def optimiser(meanReturns, covMatrix, constraintSet=contraintSet):
            pt.minimizeVariance(meanReturns, covMatrix, constraintSet=contraintSet)
        

tickers = ticks.ftse100
start=dt.datetime(2000,1,1)
end=dt.datetime(2023,1,1)
threshold=0.9

port = optimisePortfolio(tickers, start, end, logReturns=True)