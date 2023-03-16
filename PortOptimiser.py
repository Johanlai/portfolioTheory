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
"""
        def optimiser(self, meanReturns,covMatrix, riskFreeRate=riskFreeRate, contraintSet=contraintSet):
            if optimiseBy=='MaxSharpe':
                return pt.maxSharpeRatio(meanReturns,covMatrix, riskFreeRate=riskFreeRate, contraintSet=contraintSet)
            if optimiseBy=='MinVariance':
                return pt.minimizeVariance(meanReturns, covMatrix, constraintSet=contraintSet)
            
        if optimiseBy=='MaxSharpe':
            def optimiser(self, meanReturns,covMatrix, riskFreeRate=riskFreeRate, contraintSet=contraintSet):
                return pt.maxSharpeRatio(meanReturns,covMatrix, riskFreeRate=riskFreeRate, contraintSet=contraintSet)
        if optimiseBy=='MinVariance':
            def optimiser(self, meanReturns, covMatrix, riskFreeRate=riskFreeRate, constraintSet=contraintSet):
                return pt.minimizeVariance(meanReturns, covMatrix, constraintSet=contraintSet)

    def maxSR(self):
        return pt.maxSharpeRatio(self.meanReturns,self.covMatrix, self.riskFreeRate, self.contraintSet)
    def minVar(self):
        return pt.minimizeVariance(self.meanReturns, self.covMatrix, self.contraintSet)
            
        
"""    
class optPortfolio:
    def __init__(self, tickers, start, end, optimiseBy= 'maxSharpe', riskFreeRate=0, constraintSet=(0,1), logReturns = True, threshold=0.8, drop_extremes=True, excess=5, dateRange=None):
        self.portfolio = pt.Portfolio(tickers, start, end)
        self.portfolio.getData()
        self.portfolio.cleanData(threshold=threshold, drop_extremes=drop_extremes, excess=excess, dateRange=dateRange)
        self.portfolio.calculate_stats(logReturns=logReturns)
        self.start = start
        self.end = end
        self.optimiseBy = optimiseBy
        self.riskFreeRate = riskFreeRate
        self.constraintSet = constraintSet
        if logReturns:
            self.meanReturns = self.portfolio.logReturns.mean()
        else:
            self.meanReturns = self.portfolio.returns.mean()
        self.covMatrix = self.portfolio.covMatrix
        if (self.optimiseBy == 'maxSharpe'):
            self.optimiser = self.maxSR()
        elif self.optimiseBy == 'minVol':
            self.optimiser = self.minVar()
    def optimiser(self):
        if self.optimiseBy=='maxSharpe':
            return 'yes'
        else:
            return 'no'

    def test(self):
        return self.optimiser(self)
    def window_test(self):
                # Forward Annual
        shiftedRet = self.portfolio.logReturns.shift(-(len(self.portfolio.logReturns[self.portfolio.logReturns.index.year==self.portfolio.logReturns.index.year[0]])))
        FannualReset = pd.DataFrame(np.full(len(self.portfolio.logReturns),fill_value=0.0),index=self.portfolio.logReturns.index)
        FannualReset.rename(columns={0:'ret'}, inplace=True)
        for i,x in self.portfolio.logReturns.groupby(self.portfolio.logReturns.index.year):
            meanReturns = x.mean()
            covMatrix = x.cov()
            FannualReset['ret'][x.index]= shiftedRet.loc[x.index] @ (self.optimiser(meanReturns, covMatrix, riskFreeRate=self.riskFreeRate, constraintSet=self.contraintSet)[1][1]).T
        FannualReset = FannualReset.shift(len(self.portfolio.logReturns[self.portfolio.logReturns.index.year==self.portfolio.logReturns.index[0].year])).dropna()
        # Forward FBiAnnual
        shiftedRetBannual = self.portfolio.logReturns.shift(-int(len(self.portfolio.logReturns[self.portfolio.logReturns.index.year==self.portfolio.logReturns.index.year[0]])/2))
        FBiAnnualReset = pd.DataFrame(np.full(len(self.portfolio.logReturns),fill_value=0.0),index=self.portfolio.logReturns.index)
        FBiAnnualReset.rename(columns={0:'ret'}, inplace=True)
        for i,x in self.portfolio.logReturns.resample('6M',label='right',closed='left'):
            meanReturns = x.mean()
            covMatrix = x.cov()
            FBiAnnualReset['ret'][x.index] = shiftedRetBannual.loc[x.index] @ (self.optimiser(meanReturns, covMatrix, riskFreeRate=self.riskFreeRate, constraintSet=self.contraintSet)[1][1]).T
        FBiAnnualReset = FBiAnnualReset.shift(int(len(self.portfolio.logReturns[self.portfolio.logReturns.index.year==self.portfolio.logReturns.index.year[0]])/2))
        # Forward Quarterly
        shiftedRetQuarterly = self.portfolio.logReturns.shift(-int(len(self.portfolio.logReturns[self.portfolio.logReturns.index.year==self.portfolio.logReturns.index.year[0]])/2))
        FQuarterlyReset = pd.DataFrame(np.full(len(self.portfolio.logReturns),fill_value=0.0),index=self.portfolio.logReturns.index)
        FQuarterlyReset.rename(columns={0:'ret'}, inplace=True)
        for i,x in self.portfolio.logReturns.resample('Q',label='right',closed='left'):
            meanReturns = x.mean()
            covMatrix = x.cov()
            FQuarterlyReset['ret'][x.index] = shiftedRetQuarterly.loc[x.index] @ (self.optimiser(meanReturns, covMatrix, riskFreeRate=self.riskFreeRate, constraintSet=self.contraintSet)[1][1]).T
        FQuarterlyReset = FQuarterlyReset.shift(int(len(self.portfolio.logReturns[self.portfolio.logReturns.index.year==self.portfolio.logReturns.index.year[0]])/4))
        plt.figure(figsize=(10,4))
        plt.title('Log returns')
        plt.margins(x=0)
        #plt.plot(np.cumsum(annualReset), label='Annual reset', ls=':')
        plt.plot(np.cumsum(FannualReset.dropna()), label='FAnnual reset')
        plt.plot(np.cumsum(FBiAnnualReset.dropna()), label='FBiAnnual reset')
        plt.plot(np.cumsum(FQuarterlyReset.dropna()), label='FQuarterly reset')
        plt.plot(np.cumsum(portfolio.portlogReturns), label='Equally weighted', ls='--')
        plt.plot(np.cumsum(ftseLogReturn), label='ftse', ls='--')
        plt.title('Out of sample - forward static window')
        plt.grid()
        plt.legend()
        plt.show()                

tickers = ticks.ftse100
start=dt.datetime(2000,1,1)
end=dt.datetime(2023,1,1)
threshold=0.9

port = optPortfolio(tickers, start, end, logReturns=True)
port.test()

