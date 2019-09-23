#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015, 2016, 2017 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import backtrader as bt
import backtrader.indicators as btind
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import pandas as pd


# Create a Stratey

lpt = 0.1
lsl = 0.03
ltt = 0.05
lttex = 0.03

spt = 0.1
ssl = 0.03
stt = 0.05
sttex = 0.03

maxmacdhist = 0
minmacdhist = 0
ltrail_flag = 0
ltrail_price = 0
strail_flag = 0
strail_price = 0
period_sma5 = 5
period_sma25 = 20
period_he = 20
    


strategyname = 'SG_FCPO_D_000002'
   
class CUSTOM_STRAT_FIFTEEN_VO_SRT(bt.Strategy):

    params = dict(
        lprofit_target=lpt,
        lstop_loss=lsl,
        ltrail_target = ltt,
        ltrail_target_exit = lttex,
        sprofit_target=spt,
        sstop_loss=ssl,
        strail_target = stt,
        strail_target_exit = sttex,
        period_sma5 = period_sma5,
        period_sma25 = period_sma25,
        period_he = period_he
    )

    def printdatacsv(self):
        dd = pd.read_csv(os.path.join(path,tradefilename))
        print(dd)        

    def printdata(self,data):
        print(data)        
    
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))  
        #print(txt)
        
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries\
        print("-------------------------------------------------------")
        print(self.params.period_sma5, self.params.period_sma25, self.params.period_he)
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close
        self.sma5 = bt.indicators.SMA(self.dataclose, period=self.params.period_sma5, plotname='mysma')
        self.sma25 = bt.indicators.SMA(self.dataclose, period=self.params.period_sma25, plotname='mysma')
        self.smaco = btind.CrossOver(self.sma5,self.sma25)
        self.he = bt.indicators.HurstExponent(self.dataclose,period=self.params.period_he)

        # To keep track of pending orders
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        global histtrades
        global maxhe
        global minhe
        global lentryprice
        global sentryprice
        global ltrail_flag
        global ltrail_price
        global strail_flag
        global strail_price
        global longpentry
        global shortpentry
        global longptexit
        global shortptexit
        global longslexit
        global shortslexit
        global longtrailexit
        global shorttrailexit
         
        
        #print(self.datas[0].datetime.date(0))
        print(self.position.size)

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            if self.he[0] > 0.5 and self.sma5[0] > self.sma25[0]:
                        lentryprice = self.dataclose[0]  
                        maxhe = self.he[0]
                        longpentry = self.buy(price = lentryprice,exectype=bt.Order.Market)
                        longtrailexit = self.sell(exectype=bt.Order.StopTrail, trailpercent=self.p.ltrail_target_exit)
                        longpentry.addinfo(name=strategyname+'_LE')
                        print('long entry')
                        print(lentryprice)
            if self.he[0] > 0.4 and self.dataclose[0] < self.dataopen[0] :
                        sentryprice = self.dataclose[0]
                        minhe = self.he[0]
                        shortpentry = self.sell(price=sentryprice,exectype=bt.Order.Market)
                        shorttrailexit = self.buy(exectype=bt.Order.StopTrail, trailpercent=self.p.strail_target_exit)
                        shortpentry.addinfo(name=strategyname+'_SE')
                        
                        print('short entry')
                        print(sentryprice)
        else:
            # Pattern Long exit
            if self.position.size > 0:
                if(self.he[0] > maxhe):
                    maxhe = self.he[0]
                if(self.he[0] < self.he[-1] and self.he[-1] < maxhe) and self.dataclose[0] > self.dataopen[0]:
                    print("LongPExit")
                    longpexit = self.sell(exectype=bt.Order.Market) 
                    cancellongtrailexit = self.broker.cancel(longtrailexit)
                    lentryprice = 0
                
                # Long profit target exit    
                if(self.datalow[0] <= lentryprice*(1+self.p.lprofit_target) and self.datahigh[0] >= lentryprice*(1+self.p.lprofit_target)):
                    print('LPT')
                    longptexit = self.sell(exectype=bt.Order.Limit, price=lentryprice*(1+self.p.lprofit_target))
                    cancellongtrailexit = self.broker.cancel(longtrailexit)
                    lentryprice = 0
                # Long stop loss exit    
                if(self.datalow[0] <= lentryprice*(1-self.p.lstop_loss) and self.datahigh[0] >= lentryprice*(1-self.p.lstop_loss)):
                    print("LSL")
                    longslexit = self.sell(exectype=bt.Order.Market)
                    cancellongtrailexit = self.broker.cancel(longtrailexit)
                    lentryprice = 0
                '''
                # Long Trailing flag trigger
                if(ltrail_flag == 0 and self.datahigh[0] >= lentryprice*(1+self.p.ltrail_target)):
                    ltrail_flag = 1
                    ltrail_price = self.datahigh[0]
                    
                if(ltrail_flag ==1 and (self.datahigh[0] - self.dataopen[0]) < (self.dataopen[0] - self.datalow[0])):
                    if(self.datahigh[0] >= ltrail_price):
                        ltrail_price = self.datahigh[0]
                    if(self.datalow[0] < ltrail_price*(1-self.p.ltrail_target_exit)):
                        self.order = self.sell(exectype=bt.Order.Stop, price=ltrail_price*(1-self.p.ltrail_target_exit))
                        lentryprice = 0
                        ltrail_flag = 0
                elif (ltrail_flag == 1 and (self.datahigh[0] - self.dataopen[0]) > (self.dataopen[0] - self.datalow[0])):        
                    if(self.datalow[0] < ltrail_price*(1-self.p.ltrail_target_exit)):
                        self.order = self.sell(exectype=bt.Order.Stop, price=ltrail_price*(1-self.p.ltrail_target_exit))
                        lentryprice = 0
                        ltrail_flag = 0
            '''         
            # pattern Short Exit        
            if self.position.size < 0:
                if(self.he[0] < minhe):
                    minhe = self.he[0]
                if(self.he[0] > self.he[-1] and self.he[-1] > minhe and self.dataclose[0] < self.dataopen[0]):
                    print("ShortPExit")
                    shortpexit = self.buy(exectype=bt.Order.Market)  
                    cancelshorttrailexit = self.broker.cancel(shorttrailexit)
                    sentryprice = 0          
                
                # Short profit target exit    
                if(self.datalow[0] <= sentryprice*(1 - self.p.sprofit_target) and self.datahigh[0] >= sentryprice*(1-self.p.sprofit_target)):
                    print('SPT')
                    shortptexit = self.buy(exectype=bt.Order.Limit, price=sentryprice*(1-self.p.sprofit_target))
                    cancelshorttrailexit = self.broker.cancel(shorttrailexit)
                    sentryprice = 0
                # Short stop loss exit    
                if(self.datalow[0] <= sentryprice*(1+self.p.sstop_loss) and self.datahigh[0] >= sentryprice*(1+self.p.sstop_loss)):
                    print('SSL')
                    shortslexit = self.buy(exectype=bt.Order.Stop, price=sentryprice*(1+self.p.sstop_loss))
                    cancelshorttrailexit = self.broker.cancel(shorttrailexit)
                    sentryprice = 0
                '''
                # Short Trailing flag trigger
                if(strail_flag == 0 and self.datalow[0] <= sentryprice*(1-self.p.strail_target)):
                    strail_flag = 1
                    strail_price = self.datalow[0]
                if(strail_flag == 1 and (self.datahigh[0] - self.dataopen[0]) > (self.dataopen[0] - self.datalow[0])):
                    if(self.datalow[0] <= strail_price):
                        strail_price = self.datalow[0]
                    if(self.datalow[0] > strail_price*(1+self.p.strail_target_exit)):
                        self.order = self.buy(exectype=bt.Order.Stop, price=strail_price*(1-self.p.strail_target_exit))
                        sentryprice = 0
                        strail_flag = 0
                elif (strail_flag == 1 and (self.datahigh[0] - self.dataopen[0]) > (self.dataopen[0] - self.datalow[0])):        
                    if(self.datalow[0] < strail_price*(1-self.p.strail_target_exit)):
                        self.order = self.buy(exectype=bt.Order.Stop, price=strail_price*(1-self.p.strail_target_exit))
                        sentryprice = 0
                        strail_flag = 0
               '''

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pyfolio as pf
import numpy as np
import sg_fcpo_d_000001_v1_Single

path = 'D:/indicatorOptimization/result'
reportPath = 'D:/indicatorOptimization/result/reports/'
filename = 'FCPO3-OHLCV.csv'
instrument = "FCPO"

noosstrategies = 1
strategy = "GL"
if strategy=='GL':# and reporttype== 'consolidated':
    lotsize = 25 
    investment = 20000
    tinvestment = 20000 * noosstrategies
    commission = 5 
else:
    lotsize = 25 * noosstrategies
    investment = 20000 * noosstrategies
    tinvestment = 20000 * noosstrategies
    commission = 5 * noosstrategies
    
strategy_variable = {
        'GL': {
                'lotsize': 25 ,
                'investment': 20000,
                'tinvestment': 20000 * noosstrategies,
                'commission': 5 
            },
        'SG': {
                'lotsize': 25 * noosstrategies,
                'investment': 20000 * noosstrategies,
                'tinvestment': 20000 * noosstrategies,
                'commission': 5 * noosstrategies
                }
        }
    
leverage = 10
riskpercentage = 0.25
futures_like = True


fromdate = datetime.datetime(2000, 1, 1)
last_row = pd.read_csv(path+"/"+filename)
# todate = datetime.datetime.strptime(last_row.iloc[len(last_row)-1]['Date'], '%Y-%d-%m')
todate = datetime.datetime(2015, 12, 31)

import_Data = True


# Create a Stratey

lpt = 0.1
lsl = 0.03
ltt = 0.05
lttex = 0.03

spt = 0.1
ssl = 0.03
stt = 0.05
sttex = 0.03

maxmacdhist = 0
minmacdhist = 0
ltrail_flag = 0
ltrail_price = 0
strail_flag = 0
strail_price = 0

strategyname = 'SG_FCPO_D_000002'
   

def run_strategy(strategy, variables,
                 period_sma5=None, 
                 period_sma25=None,
                 period_he=None,
                 issg=False):
    print("run strategy")
    print(period_sma5, period_sma25, period_he)
    cerebro = bt.Cerebro()
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath,path,filename)

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
       dataname=datapath,
       # Do not pass values before this date
       fromdate=fromdate,
       todate=todate,
       dtformat=('%Y-%m-%d'),
       nullvalue=0.0,
       datetime=0,
       open=1,
       high=2,
       low=3,
       close=4,
       volume=5,
       openinterest=-1
       )

    cerebro.addanalyzer(bt.analyzers.PyFolio)
    cerebro.adddata(data)
    if issg == False:
        cerebro.addstrategy(strategy, 
            period_sma5=period_sma5,
            period_sma25=period_sma25,
            period_he=period_he)
    else:
        cerebro.addstrategy(strategy)

    # Set our desired cash start
    cerebro.broker.setcash(variables['investment'])
    cerebro.broker.setcommission(commission=variables['commission'], margin=variables['investment']*(1-riskpercentage), mult=variables['lotsize'],leverage=leverage)

    # Run over everything{}
    result = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    return result



result_sg = run_strategy(sg_fcpo_d_000001_v1_Single.SG_FCPO_Single_v1, strategy_variable['SG'], issg=True)
pyfolio = result_sg[0].analyzers.getbyname('pyfolio')
returns, positions, transactions, gross_lev = pyfolio.get_pf_items()
returns.to_csv("BenchMark.csv")


# Reading Benchmark Data from CSV file for Singapore Strategy

retdata = pd.read_csv('BenchMark.csv',header=None)
retdata.columns = ['Date', 'Return']
pd.to_datetime(retdata['Date'], errors='coerce')
retdata = retdata.set_index('Date')
retdata.index.names = [None] 
benchmark = retdata.ix[:,0].rename("BenchMark")
benchmark.index = pd.to_datetime(benchmark.index, errors='coerce')
benchmark = benchmark.tz_localize('UTC')



final_results_list= []

time_a = datetime.datetime.now()
lpt = 0.08 #np.arange(0.08, 0.2, 0.02)
spt = 0.08 #np.arange(0.08, 0.2, 0.02)
i = 0

for period_sma5 in np.arange(5, 20, 2):  # 6
    for period_sma25 in np.arange(period_sma5+3, 22, 2):  # 6
        for period_he in np.arange(6, 22, 2):  # 6
            i = i+1
            res = run_strategy(CUSTOM_STRAT_FIFTEEN_VO_SRT, strategy_variable['GL'], 
                               period_sma5, 
                               period_sma25, 
                               period_he,
                               issg=False)                        
            pyfolio = res[0].analyzers.getbyname('pyfolio')
            returns, positions, transactions, gross_lev = pyfolio.get_pf_items()
    #                round_trip_data, drawdown_df = gen_report(returns, positions, transactions, gross_lev, benchmark, strategy_variable['SG'])
            returns.to_csv("returnsnew_"+str(i)+".csv")
            round_trip_data = pf.create_round_trip_tear_sheet_data(
                returns=returns,
                positions=positions,
                transactions=transactions,
                sector_mappings=None,
                return_fig=True,
                shares_held=strategy_variable['GL']['lotsize'],
                slippage=0)
            drawdown_df = pf.create_returns_tear_drawdown_data(
                returns,
                live_start_date=None,
                cone_std=(1.0, 1.5, 2.0),
                benchmark_rets=benchmark,
                bootstrap=False,
                set_context=True,
                investment=tinvestment,
                shares_held=lotsize)
            df_per = drawdown_df['percentage']
            df_abs = drawdown_df['absolute']
            rd_ret = round_trip_data['returns']
            ret = ( rd_ret[rd_ret.columns[0]].iloc[0]/strategy_variable['GL']['investment'] ) * 100
            final_results_list.append([period_sma5, period_sma25, period_he, ret,round_trip_data['pnl'][round_trip_data['pnl'].columns[0]].iloc[0].round(2), df_per[df_per.columns[0]].iloc[0], df_abs[df_abs.columns[0]].iloc[0] ])
            print("Number of iteration: ")
            print(i)

time_b = datetime.datetime.now()
print(time_b-time_a)
list = pd.DataFrame(final_results_list, columns = ["period_sma5", "period_sma25", "period_he", 'return', 'pnl', 'drawdown (%)', 'drawdown (abs)'])
list.to_csv("gl_fcpo_d_000015_v0_Multiple.csv")

print("printing i value: ")
print(i)

