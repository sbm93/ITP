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

lpt = 0.15
lsl = 0.05
ltt = 0.1
lttex = 0.05

spt = 0.1
ssl = 0.03
stt = 0.1
sttex = 0.05


maxhe = 0
minhe = 0
ltrail_flag = 0
ltrail_price = 0
strail_flag = 0
strail_price = 0



strategyname = 'SG_FCPO_D_000002'
   
class BRACKET_ORDER_STR(bt.Strategy):
    
    params = dict(
        lprofit_target=lpt,
        lstop_loss=lsl,
        ltrail_target = ltt,
        ltrail_target_exit = lttex,
        sprofit_target=spt,
        sstop_loss=ssl,
        strail_target = stt,
        strail_target_exit = sttex,
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
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close
        self.datavol = self.datas[0].volume
        self.sma5 = bt.indicators.SMA(self.dataclose, period=5, plotname='mysma')
        self.sma25 = bt.indicators.SMA(self.dataclose, period=20, plotname='mysma')
        self.smaco = btind.CrossOver(self.sma5,self.sma25)
        #self.dm = bt.indicators.DirectionalMovementIndex(self.data,period=14,plot=False)
        #self.dmco = btind.CrossOver(self.dm.DIplus,self.dm.DIminus)
        self.he = bt.indicators.HurstExponent(self.dataclose,period=25)
        self.macdhist = self.he #bt.indicators.MACDHisto()
        
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
        global cancellongptslexit
        global cancelshortptslexit
        #print(self.datas[0].datetime.date(0))
        
        #print(self.position.size)
    
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            if self.he > 0.4 and self.dataclose > self.dataopen:# and self.smaco > 0 :
                        lentryprice = self.dataclose[0]   # order.executed.price , check in notify_order method
                        maxhe = self.he[0]
                        #self.log('BUY CREATE, %.2f' % self.dataclose[0])
                        # Keep track of the created order to avoid a 2nd order
                        #longpentry = self.buy(exectype=bt.Order.Market)
                        longpentry = self.buy_bracket(price = lentryprice,size=1,exectype=bt.Order.Market,limitprice=lentryprice*(1+self.p.lprofit_target),limitexec=bt.Order.Limit,stopprice=lentryprice*(1-self.p.lstop_loss),stopexec=bt.Order.Stop )
                        #longpentry.addinfo(name=strategyname+'_LE')
                        print('long entry')
                        print(lentryprice)
                        
            if self.he > 0.4 and self.dataclose < self.dataopen:# and self.smaco < 0: 
                        sentryprice = self.dataclose[0]
                        minhe = self.he[0]
                        #self.log('SELL CREATE, %.2f' % self.dataclose[0])
                        
                        shortpentry = self.sell_bracket(price=sentryprice,size=1,exectype=bt.Order.Market,limitprice=sentryprice*(1-self.p.sprofit_target),limitexec=bt.Order.Limit,stopprice=sentryprice*(1+self.p.sstop_loss), stopexec=bt.Order.Stop)
                        print('short entry')
                        
        else:
            # Pattern Long exit
            if self.position.size > 0:
                
                if(self.he[0] > maxhe):
                    maxhe = self.he[0]
                
                if(self.smaco < 0):
                    print("LongPExit")
                    self.order = self.sell(exectype=bt.Order.Market) 
                    lentryprice = 0
                
                '''
                # Long profit target exit    
                if(self.datalow[0] <= lentryprice*(1+self.p.lprofit_target) and self.datahigh[0] >= lentryprice*(1+self.p.lprofit_target)):
                    self.order = self.sell(exectype=bt.Order.Limit, price=lentryprice*(1+self.p.lprofit_target))
                    currtrade = pd.DataFrame([[self.datas[0].datetime.date(0),instrument,"LongExit",lentryprice*(1+self.p.lprofit_target),strategyname,strategyname+'_LEXPT']], columns=cols)
                    histtrades = histtrades.append(currtrade, ignore_index=True)
                    histtrades.to_csv(os.path.join(path,tradefilename),index=False)    
                    lentryprice = 0
                # Long stop loss exit    
                if(self.datalow[0] <= lentryprice*(1-self.p.lstop_loss) and self.datahigh[0] >= lentryprice*(1-self.p.lstop_loss)):
                    print("LSL")
                    print(self.datalow[0] <= lentryprice*(1-self.p.lstop_loss) and self.datahigh[0] >= lentryprice*(1-self.p.lstop_loss))
                    print(lentryprice*(1-self.p.lstop_loss))
                    #self.order = self.sell(exectype=bt.Order.Stop, price=lentryprice*(1-self.p.lstop_loss))
                    self.order = self.sell()
                    currtrade = pd.DataFrame([[self.datas[0].datetime.date(0),instrument,"LongExit",lentryprice*(1-self.p.lstop_loss),strategyname,strategyname+'_LEXSL']], columns=cols)
                    histtrades = histtrades.append(currtrade, ignore_index=True)
                    histtrades.to_csv(os.path.join(path,tradefilename),index=False)        
                    lentryprice = 0
               
                # Long Trailing flag trigger
                if(ltrail_flag == 0 and self.datahigh[0] >= lentryprice*(1+self.p.ltrail_target)):
                    ltrail_flag = 1
                    ltrail_price = self.datahigh[0]
                    
                if(ltrail_flag ==1 and (self.datahigh[0] - self.dataopen[0]) < (self.dataopen[0] - self.datalow[0])):
                    if(self.datahigh[0] >= ltrail_price):
                        ltrail_price = self.datahigh[0]
                    if(self.datalow[0] < ltrail_price*(1-self.p.ltrail_target_exit)):
                        self.order = self.sell(exectype=bt.Order.Stop, price=ltrail_price*(1-self.p.ltrail_target_exit))
                        currtrade = pd.DataFrame([[self.datas[0].datetime.date(0),instrument,"LongExit",ltrail_price*(1-self.p.ltrail_target_exit),strategyname,strategyname+'_LEXTT']], columns=cols)
                        histtrades = histtrades.append(currtrade, ignore_index=True)
                        histtrades.to_csv(os.path.join(path,tradefilename),index=False)        
                        lentryprice = 0
                        ltrail_flag = 0
                elif (ltrail_flag == 1 and (self.datahigh[0] - self.dataopen[0]) > (self.dataopen[0] - self.datalow[0])):        
                    if(self.datalow[0] < ltrail_price*(1-self.p.ltrail_target_exit)):
                        self.order = self.sell(exectype=bt.Order.Stop, price=ltrail_price*(1-self.p.ltrail_target_exit))
                        currtrade = pd.DataFrame([[self.datas[0].datetime.date(0),instrument,"LongExit",ltrail_price*(1-self.p.ltrail_target_exit),strategyname,strategyname+'_LEXTT']], columns=cols)
                        histtrades = histtrades.append(currtrade, ignore_index=True)
                        histtrades.to_csv(os.path.join(path,tradefilename),index=False)        
                        lentryprice = 0
                        ltrail_flag = 0
             '''           
            # pattern Short Exit        
            if self.position.size < 0:
                
                if(self.he[0] < minhe):
                    minhe = self.he[0]
                
                if(self.smaco > 0):
                    print("ShortPExit")
                    self.order = self.buy(exectype=bt.Order.Market)    
                    sentryprice = 0
                    
                
                '''
                # Short profit target exit    
                if(self.datalow[0] <= sentryprice*(1 - self.p.sprofit_target) and self.datahigh[0] >= sentryprice*(1-self.p.sprofit_target)):
                    self.order = self.buy(exectype=bt.Order.Limit, price=sentryprice*(1-self.p.sprofit_target))
                    currtrade = pd.DataFrame([[self.datas[0].datetime.date(0),instrument,"ShortExit",sentryprice*(1-self.p.sprofit_target),strategyname,strategyname+'_SEXPT']], columns=cols)
                    histtrades = histtrades.append(currtrade, ignore_index=True)
                    histtrades.to_csv(os.path.join(path,tradefilename),index=False)    
                    sentryprice = 0
                # Short stop loss exit    
                if(self.datalow[0] <= sentryprice*(1+self.p.sstop_loss) and self.datahigh[0] >= sentryprice*(1+self.p.sstop_loss)):
                    self.order = self.buy(exectype=bt.Order.Stop, price=sentryprice*(1+self.p.sstop_loss))
                    currtrade = pd.DataFrame([[self.datas[0].datetime.date(0),instrument,"ShortExit",sentryprice*(1+self.p.sstop_loss),strategyname,strategyname+'_SEXSL']], columns=cols)
                    histtrades = histtrades.append(currtrade, ignore_index=True)
                    histtrades.to_csv(os.path.join(path,tradefilename),index=False)       
                    sentryprice = 0
                 
                # Short Trailing flag trigger
                if(strail_flag == 0 and self.datalow[0] <= sentryprice*(1-self.p.strail_target)):
                    strail_flag = 1
                    strail_price = self.datalow[0]
                if(strail_flag == 1 and (self.datahigh[0] - self.dataopen[0]) > (self.dataopen[0] - self.datalow[0])):
                    if(self.datalow[0] <= strail_price):
                        strail_price = self.datalow[0]
                    if(self.datalow[0] > strail_price*(1+self.p.strail_target_exit)):
                        self.order = self.buy(exectype=bt.Order.Stop, price=strail_price*(1-self.p.strail_target_exit))
                        currtrade = pd.DataFrame([[self.datas[0].datetime.date(0),instrument,"ShortExit",strail_price*(1+self.p.strail_target_exit),strategyname,strategyname+'_SEXTT']], columns=cols)
                        histtrades = histtrades.append(currtrade, ignore_index=True)
                        histtrades.to_csv(os.path.join(path,tradefilename),index=False)        
                        sentryprice = 0
                        strail_flag = 0
                elif (strail_flag == 1 and (self.datahigh[0] - self.dataopen[0]) > (self.dataopen[0] - self.datalow[0])):        
                    if(self.datalow[0] < strail_price*(1-self.p.strail_target_exit)):
                        self.order = self.buy(exectype=bt.Order.Stop, price=strail_price*(1-self.p.strail_target_exit))
                        currtrade = pd.DataFrame([[self.datas[0].datetime.date(0),instrument,"ShortExit",strail_price*(1+self.p.strail_target_exit),strategyname,strategyname+'_SEXTT']], columns=cols)
                        histtrades = histtrades.append(currtrade, ignore_index=True)
                        histtrades.to_csv(os.path.join(path,tradefilename),index=False)        
                        sentryprice = 0
                        strail_flag = 0
               #print(maxmacdhist)         
              '''