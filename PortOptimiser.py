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

class optPort:
    def __init__(self, tickers, start, end, optimiseBy= 'maxSharpe', riskFreeRate=0, constraintSet=(0,1), logReturns=True, threshold=0.8, drop_extremes=True, excess=5, dateRange=None):
        self.portfolio = pt.Portfolio(tickers, start, end)
        self.portfolio.getData()
        self.portfolio.cleanData(threshold=threshold, drop_extremes=drop_extremes, excess=excess, dateRange=dateRange)
        self.portfolio.calculate_stats(logReturns=logReturns)
        self.portfolio.calculate_PortPerformance(pt.equallyWeighted(self.portfolio.logReturns.mean(),self.portfolio.logReturns.cov())[1][1])
        self.optimiseBy = optimiseBy
    def testConstraints(self,riskFreeRate=0,constraintSet=(0,1)):
        def optimiser(meanReturns,covMatrix, riskFreeRate=riskFreeRate, constraintSet=constraintSet):
            if self.optimiseBy=='maxSR':
                return pt.maxSharpeRatio(meanReturns,covMatrix, riskFreeRate=riskFreeRate, constraintSet=constraintSet)
            elif self.optimiseBy=='minVol':
                return pt.minimizeVariance(meanReturns,covMatrix, constraintSet=constraintSet)
        meanReturns = self.portfolio.logReturns.mean()
        covMatrix = self.portfolio.covMatrix
        w0001 = optimiser(meanReturns,covMatrix,constraintSet=(0.0001, 1))
        w001 = optimiser(meanReturns,covMatrix,constraintSet=(0.001, 1))
        w01 = optimiser(meanReturns,covMatrix,constraintSet=(0.01, 1))
        w = optimiser(meanReturns,covMatrix)
        fig, axs = plt.subplots(2,2,figsize=(10,4), layout='constrained', sharey=True, sharex=True)
        fig.suptitle('Distribution of weights with various contraints', fontsize=15)
        fig.supylabel('Weight')
        fig.supxlabel('Asset index')
        axs[0][0].bar(np.arange(1,len(w0001[1][1])+1),height=w0001[1][1])
        axs[0][0].set_title('contraintSet=(0.0001, 1)')
        axs[0][1].bar(np.arange(1,len(w001[1][1])+1),height=w001[1][1])
        axs[0][1].set_title('contraintSet=(0.001, 1)')
        axs[1][0].bar(np.arange(1,len(w01[1][1])+1),height=w01[1][1])
        axs[1][0].set_title('contraintSet=(0.01, 1)')
        axs[1][1].bar(np.arange(1,len(w[1][1])+1),height=w[1][1])
        axs[1][1].set_title('contraintSet=(0, 1)')
        for i in axs.flatten():
            i.grid(visible=True,which='both',linewidth=0.3)
            i.margins(x=0)
        plt.show()
        df = pd.concat([pd.DataFrame(w0001[1]).T.set_index(0),
                 pd.DataFrame(w001[1]).T.set_index(0), 
                 pd.DataFrame(w01[1]).T.set_index(0), 
                 pd.DataFrame(w[1]).T.set_index(0)], axis=1)
        df.columns = ['(0.0001, 1)','(0.001, 1)','(0.01, 1)','(0, 1)']
        df.index.name = 'ConstraintSet'
        df = (df*100).astype(float).round(2)
        return df.T.astype(str) + '%'
    
    def testResetMovingWindow(self,riskFreeRate=0,constraintSet=(0,1)):
        def optimiser(meanReturns,covMatrix, riskFreeRate=riskFreeRate, constraintSet=constraintSet):
            if self.optimiseBy=='maxSR':
                return pt.maxSharpeRatio(meanReturns,covMatrix, riskFreeRate=riskFreeRate, constraintSet=constraintSet)
            elif self.optimiseBy=='minVol':
                return pt.minimizeVariance(meanReturns,covMatrix, constraintSet=constraintSet)
        # Forward FAnnual
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
        plt.title('Comparing the frequency of resetting the weights from backwards looking window')        
        return df
    
    def testResetCumulativeSample(self,riskFreeRate=0,constraintSet=(0,1)):
        def optimiser(meanReturns,covMatrix, riskFreeRate=riskFreeRate, constraintSet=constraintSet):
            if self.optimiseBy=='maxSR':
                return pt.maxSharpeRatio(meanReturns,covMatrix, riskFreeRate=riskFreeRate, constraintSet=constraintSet)
            elif self.optimiseBy=='minVol':
                return pt.minimizeVariance(meanReturns,covMatrix, constraintSet=constraintSet)
        # Forward cumulative Annual
        CannualReset = pd.DataFrame(np.full(len(self.portfolio.logReturns),fill_value=np.nan),index=self.portfolio.logReturns.index)
        CannualReset.rename(columns={0:'ret'}, inplace=True)
        for i,x in self.portfolio.logReturns.resample('1Y',label='right',closed='left'):
            meanReturns = self.portfolio.logReturns[:i].mean()
            covMatrix = self.portfolio.logReturns[:i].cov()
            CannualReset['ret'][i:i+relativedelta(years=1)]= self.portfolio.logReturns[i:i+relativedelta(years=1)] @ (optimiser(meanReturns,covMatrix)[1][1]).T
        # Forward cumulative BiAnnual    
        CBiAnnualReset = pd.DataFrame(np.full(len(self.portfolio.logReturns),fill_value=np.nan),index=self.portfolio.logReturns.index)
        CBiAnnualReset.rename(columns={0:'ret'}, inplace=True)
        for i,x in self.portfolio.logReturns.resample('6m',label='right',closed='left'):
            meanReturns = self.portfolio.logReturns[:i].mean()
            covMatrix = self.portfolio.logReturns[:i].cov()
            CBiAnnualReset['ret'][i:i+relativedelta(months=+6)]= self.portfolio.logReturns[i:i+relativedelta(months=+6)] @ (optimiser(meanReturns,covMatrix)[1][1]).T
        # Forward cumulative quarterly
        CQuarterlyReset = pd.DataFrame(np.full(len(self.portfolio.logReturns),fill_value=np.nan),index=self.portfolio.logReturns.index)
        CQuarterlyReset.rename(columns={0:'ret'}, inplace=True)
        for i,x in self.portfolio.logReturns.resample('3m',label='right',closed='left'):
            meanReturns = self.portfolio.logReturns[:i].mean()
            covMatrix = self.portfolio.logReturns[:i].cov()
            CQuarterlyReset['ret'][i:i+relativedelta(months=+3)]= self.portfolio.logReturns[i:i+relativedelta(months=+3)] @ (optimiser(meanReturns,covMatrix)[1][1]).T
        df = pd.concat([CannualReset,CBiAnnualReset,CQuarterlyReset], axis=1)
        df.columns = ['Annual Reset','Bi-annual Reset','Quarterly Reset']
        df.cumsum().plot(figsize=(12,4)); plt.legend();plt.margins(x=0), plt.grid()
        plt.title('Comparing the frequency of resetting the weights with cumulative sample')        
        return df      
    
tickers = ticks.simple
start=dt.datetime(2000,1,1)
end=dt.datetime(2023,1,1)
threshold=0.9

port = optPort(tickers, start, end, logReturns=True, optimiseBy='minVol', threshold=0.5)
constraints = port.testConstraints()
cumulativeWindow = port.testResetCumulativeSample()

