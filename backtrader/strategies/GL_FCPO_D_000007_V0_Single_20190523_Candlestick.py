from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import pandas as pd 
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo
import pyfolio as pf

# Create a Strategy

lpt = 0.1
lsl = 0.03
ltt = 0.05
lttex = 0.05

spt = 0.1
ssl = 0.03
stt = 0.05
sttex = 0.05

maxmacdhist = 0
minmacdhist = 0
ltrail_flag = 0
ltrail_price = 0
strail_flag = 0
strail_price = 0
order = 0  

strategyname = 'SG_FCPO_D_000002'

class TestStrategy3(bt.Strategy):
    
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
        self.sma5 = bt.indicators.SMA(self.dataclose, period=5, plotname='mysma')
        self.sma25 = bt.indicators.SMA(self.dataclose, period=25, plotname='mysma')
        self.smaco = btind.CrossOver(self.sma5,self.sma25)
        #self.rsi = bt.indicators.RSI_EMA(self.dataclose,period=12)
        #self.rsi20 = bt.indicators.RSI_EMA(self.dataclose,period=20)
        self.macdhist = bt.indicators.MACDHisto(period_me1=12,period_me2 = 30,period_signal=12)
        self.bbands = bt.indicators.BollingerBands(self.dataclose,period=10)
        

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
        
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        global histtrades
        global maxrsi
        global minrsi
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
        global shorttrailexit, order
         
        
        #print(self.datas[0].datetime.date(0))
        #print(self.position.size)

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position: #self.macdhist.macd[0] > self.macdhist.signal[0] and 
            if self.dataclose[0] > self.dataopen[0] and self.datalow[0] > self.dataclose[-1] and self.datalow[-2] > self.dataclose[-1]:
                        lentryprice = self.dataclose[0]  
                        #maxrsi = self.rsi[0]
                        longpentry = self.buy(price = lentryprice,exectype=bt.Order.Market)
                        order = 0
                        longtrailexit = self.sell(exectype=bt.Order.StopTrail, trailpercent=self.p.ltrail_target_exit)
                        longpentry.addinfo(name=strategyname+'_LE')
                        print('long entry')
                        print(lentryprice)
            else:
                if self.dataclose[0] < self.dataopen[0] and self.datahigh[0] < self.dataclose[-1] and self.datahigh[-2] < self.dataclose[-1]:
                #self.dataopen[0] > self.bbands.top[0] and self.dataclose[0] < self.bbands.top[0] and (self.datahigh[0]-self.dataopen[0]) > (self.dataclose[0]-self.datalow[0]):
                        sentryprice = self.dataclose[0]
                        #minrsi = self.rsi[0]
                        shortpentry = self.sell(price=sentryprice,exectype=bt.Order.Market)
                        order = 0
                        shorttrailexit = self.buy(exectype=bt.Order.StopTrail, trailpercent=self.p.strail_target_exit)
                        shortpentry.addinfo(name=strategyname+'_SE')
                        print('short entry')
                        print(sentryprice)
        else:
            # Pattern Long exit
            if self.position.size > 0:
                #if(self.rsi[0] > maxrsi):
                    #maxrsi = self.rsi[0]
                if  self.datahigh[0] < self.datahigh[-1] and self.datalow[0] < self.datalow[-1] and self.datahigh[-1] < self.datahigh[-2] and self.datalow[-1] < self.datalow[-2] :
                    print("LongPExit")
                    longpexit = self.sell(exectype=bt.Order.Market) 
                    order = 1
                    cancellongtrailexit = self.broker.cancel(longtrailexit)
                    lentryprice = 0
                
                if order == 0:
                    # Long profit target exit    
                    if((self.datalow[0] <= lentryprice*(1+self.p.lprofit_target) and self.datahigh[0] >= lentryprice*(1+self.p.lprofit_target) and self.dataopen[0] < lentryprice*(1+self.p.lprofit_target)) or (self.dataopen[0] >= lentryprice*(1+self.p.lprofit_target))):
                        print("LPT")
                        longptexit = self.sell(exectype=bt.Order.Limit, price=lentryprice*(1+self.p.lprofit_target))
                        cancellongtrailexit = self.broker.cancel(longtrailexit)
                        lentryprice = 0
                    else:
                        # Long stop loss exit    
                        if((self.datalow[0] <= lentryprice*(1-self.p.lstop_loss) and self.datahigh[0] >= lentryprice*(1-self.p.lstop_loss) and self.dataopen[0] > lentryprice*(1-self.p.lstop_loss) ) or (self.dataopen[0] <= lentryprice*(1-self.p.lstop_loss))):
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
                #if(self.rsi[0] < minrsi):
                    #minrsi = self.rsi[0]
                if self.datahigh[0] > self.datahigh[-1] and self.datalow[0] > self.datalow[-1] and self.datahigh[-1] > self.datahigh[-2] and self.datalow[-1] > self.datalow[-2] :
                #self.bbands.bot[0] > self.bbands.bot[-1] and self.dataclose[0] > self.dataopen[0]:#and self.dataclose[-1] > self.bbands.top[-1]: #self.rsi[0] > self.rsi[-1] and self.rsi[-1] > minrsi :
                    print("ShortPExit")
                    shortpexit = self.buy(exectype=bt.Order.Market)  
                    order = -1
                    cancelshorttrailexit = self.broker.cancel(shorttrailexit)
                    sentryprice = 0          
                
                if order == 0:
                    # Short profit target exit    
                    if((self.datalow[0] <= sentryprice*(1 - self.p.sprofit_target) and self.datahigh[0] >= sentryprice*(1-self.p.sprofit_target) and self.dataopen[0] > sentryprice*(1-self.p.sprofit_target)) or (self.dataopen[0] <= sentryprice*(1-self.p.sprofit_target))):
                        print("SPT")
                        shortptexit = self.buy(exectype=bt.Order.Limit, price=sentryprice*(1-self.p.sprofit_target))
                        cancelshorttrailexit = self.broker.cancel(shorttrailexit)
                        sentryprice = 0
                    else:
                        # Short stop loss exit    
                        if((self.datalow[0] <= sentryprice*(1+self.p.sstop_loss) and self.datahigh[0] >= sentryprice*(1+self.p.sstop_loss) and self.dataopen[0] < sentryprice*(1+self.p.sstop_loss)) or (self.dataopen[0] >= sentryprice*(1+self.p.sstop_loss))):
                            print("SSL")
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