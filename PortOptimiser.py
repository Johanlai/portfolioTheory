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
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt

class optPort:
    def __init__(self, tickers, start, end, optimiseBy= 'maxSharpe', riskFreeRate=0, constraintSet=(0,1), logReturns=True, threshold=0.8, drop_extremes=True, excess=5, dateRange=None):
        self.portfolio = pt.Portfolio(tickers, start, end)
        self.portfolio.getData()
        self.portfolio.cleanData(threshold=threshold, drop_extremes=drop_extremes, excess=excess, dateRange=dateRange)
        self.portfolio.calculate_stats(logReturns=logReturns)
        self.portfolio.calculate_PortPerformance(pt.equallyWeighted(self.portfolio.logReturns.mean(),self.portfolio.logReturns.cov())[1][1])
        self.optimiseBy = optimiseBy

    def window_test(self,riskFreeRate=0,constraintSet=(0,1)):
        def optimiser(meanReturns,covMatrix, riskFreeRate=riskFreeRate, constraintSet=constraintSet):
            if self.optimiseBy=='maxSR':
                return pt.maxSharpeRatio(meanReturns,covMatrix, riskFreeRate=riskFreeRate, constraintSet=constraintSet)
            elif self.optimiseBy=='minVol':
                return pt.minimizeVariance(meanReturns,covMatrix, constraintSet=constraintSet)
        shiftedRet = self.portfolio.logReturns.shift(-(len(self.portfolio.logReturns[self.portfolio.logReturns.index.year==self.portfolio.logReturns.index.year[0]])))
        FannualReset = pd.DataFrame(np.full(len(self.portfolio.logReturns),fill_value=0.0),index=self.portfolio.logReturns.index)
        FannualReset.rename(columns={0:'ret'}, inplace=True)
        for i,x in self.portfolio.logReturns.groupby(self.portfolio.logReturns.index.year):
            meanReturns = x.mean()
            covMatrix = x.cov()
            FannualReset['ret'][x.index]= shiftedRet.loc[x.index] @ (optimiser(meanReturns,covMatrix)[1][1]).T
        FannualReset = FannualReset.shift(len(self.portfolio.logReturns[self.portfolio.logReturns.index.year==self.portfolio.logReturns.index[0].year])).dropna()
        # Forward FBiAnnual
        shiftedRetBannual = self.portfolio.logReturns.shift(-int(len(self.portfolio.logReturns[self.portfolio.logReturns.index.year==self.portfolio.logReturns.index.year[0]])/2))
        FBiAnnualReset = pd.DataFrame(np.full(len(self.portfolio.logReturns),fill_value=0.0),index=self.portfolio.logReturns.index)
        FBiAnnualReset.rename(columns={0:'ret'}, inplace=True)
        for i,x in self.portfolio.logReturns.resample('6M',label='right',closed='left'):
            meanReturns = x.mean()
            covMatrix = x.cov()
            FBiAnnualReset['ret'][x.index] = shiftedRetBannual.loc[x.index] @ (optimiser(meanReturns,covMatrix)[1][1]).T
        FBiAnnualReset = FBiAnnualReset.shift(int(len(self.portfolio.logReturns[self.portfolio.logReturns.index.year==self.portfolio.logReturns.index.year[0]])/2))
        # Forward Quarterly
        shiftedRetQuarterly = self.portfolio.logReturns.shift(-int(len(self.portfolio.logReturns[self.portfolio.logReturns.index.year==self.portfolio.logReturns.index.year[0]])/2))
        FQuarterlyReset = pd.DataFrame(np.full(len(self.portfolio.logReturns),fill_value=0.0),index=self.portfolio.logReturns.index)
        FQuarterlyReset.rename(columns={0:'ret'}, inplace=True)
        for i,x in self.portfolio.logReturns.resample('Q',label='right',closed='left'):
            meanReturns = x.mean()
            covMatrix = x.cov()
            FQuarterlyReset['ret'][x.index] = shiftedRetQuarterly.loc[x.index] @ (optimiser(meanReturns,covMatrix)[1][1]).T
        FQuarterlyReset = FQuarterlyReset.shift(int(len(self.portfolio.logReturns[self.portfolio.logReturns.index.year==self.portfolio.logReturns.index.year[0]])/4))
        df = pd.concat([FannualReset,FBiAnnualReset,FQuarterlyReset], axis=1)
        df.columns = ['Annual Reset','Bi-annual Reset','Quarterly Reset']
        df.cumsum().plot(figsize=(12,4)); plt.legend();plt.margins(x=0), plt.grid()
        plt.title('Comparing the frequency of resetting the weights')        
        return df             

tickers = ticks.ftse100
start=dt.datetime(2000,1,1)
end=dt.datetime(2023,1,1)
threshold=0.9

port = optPortfolio(tickers, start, end, logReturns=True)
port.test()

