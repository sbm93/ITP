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
order = 0

strategyname = 'SG_FCPO_D_000002'

class TestStrategy(bt.Strategy):
    
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
        self.sma25 = bt.indicators.SMA(self.dataclose, period=20, plotname='mysma')
        #self.smaco = btind.CrossOver(self.sma5,self.sma25)
        self.direc = bt.indicators.DirectionalMovement(self.datas[0],period=20,plot=False)    
        self.he = bt.indicators.HurstExponent(self.dataclose,period=20)
        self.direcco = btind.CrossOver(self.direc.plusDI,self.direc.minusDI,plot=False)
        self.highest = bt.indicators.Highest(self.datahigh,period=3)
        self.lowest = bt.indicators.Lowest(self.datalow,period=3)
        #self.rsi = bt.indicators.RSI_EMA(self.datalow,period=20)
        

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
        global shorttrailexit, order
         
        
        #print(self.datas[0].datetime.date(0))
        #print(self.position.size)

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            if self.direc.plusDI[0] > self.direc.minusDI[0] and self.dataclose[0] > self.dataopen[0] and self.sma5[0] > self.sma25[0] and self.dataclose[-1] > self.dataopen[-1]:
                        lentryprice = self.dataclose[0]  
                        maxhe = self.he[0]
                        longpentry = self.buy(price = lentryprice,exectype=bt.Order.Market)
                        order = 0
                        longtrailexit = self.sell(exectype=bt.Order.StopTrail, trailpercent=self.p.ltrail_target_exit)
                        longpentry.addinfo(name=strategyname+'_LE')
                        print('long entry')
                        print(lentryprice)
            if self.direc.plusDI[0] < self.direc.minusDI[0] and self.dataclose[0] < self.dataopen[0]  and self.sma5[0] < self.sma25[0] and self.dataclose[-1] < self.dataopen[-1]:
                    sentryprice = self.dataclose[0]
                    minhe = self.he[0]
                    shortpentry = self.sell(price=sentryprice,exectype=bt.Order.Market)
                    order = 0
                    shorttrailexit = self.buy(exectype=bt.Order.StopTrail, trailpercent=self.p.strail_target_exit)
                    shortpentry.addinfo(name=strategyname+'_SE')
                    print('short entry')
                    print(sentryprice)
        else:
            # Pattern Long exit
            if self.position.size > 0:
                if(self.he[0] > maxhe):
                    maxhe = self.he[0]
                #if self.he[0] < self.he[-1] and self.he[-1] < maxhe and self.dataclose[0] > self.dataopen[0] : #and self.sma5[0] < self.sma25[0]:
                if self.direc.plusDI[0] < self.direc.minusDI[0] and self.dataclose[0] > self.dataopen[0] : #and self.sma5[0] < self.sma25[0]:
                    print("LongPExit")
                    longpexit = self.sell(exectype=bt.Order.Market)
                    order = 1
                    cancellongtrailexit = self.broker.cancel(longtrailexit)
                    if (bool(longptexit)):
                        if(longptexit.alive()==True):
                            cancellongptexit = self.broker.cancel(longptexit)
                    lentryprice = 0
                
                if order == 0:
                    # Long profit target exit    
                    if((self.datalow[0] <= lentryprice*(1+self.p.lprofit_target) and self.datahigh[0] >= lentryprice*(1+self.p.lprofit_target) and self.dataopen[0] < lentryprice*(1+self.p.lprofit_target)) or (self.dataopen[0] >= lentryprice*(1+self.p.lprofit_target))):
                        longptexit = self.sell(exectype=bt.Order.Limit, price=lentryprice*(1+self.p.lprofit_target))
                        cancellongtrailexit = self.broker.cancel(longtrailexit)
                        lentryprice = 0
                    else:
                        # Long stop loss exit    
                        if((self.datalow[0] <= lentryprice*(1-self.p.lstop_loss) and self.datahigh[0] >= lentryprice*(1-self.p.lstop_loss) and self.dataopen[0] > lentryprice*(1-self.p.lstop_loss) ) or (self.dataopen[0] <= lentryprice*(1-self.p.lstop_loss))):
                            print("LSL")
                            longslexit = self.sell(exectype=bt.Order.Market)
                            cancellongtrailexit = self.broker.cancel(longtrailexit)
                            if (bool(longptexit)):
                                if(longptexit.alive()==True):
                                    cancellongptexit = self.broker.cancel(longptexit)
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
                #if self.he[0] > self.he[-1] and self.he[-1] > minhe  and self.dataclose[0] < self.dataopen[0] :#and self.sma5[0] > self.sma25[0]:
                if self.direc.plusDI[0] > self.direc.minusDI[0] and self.dataclose[0] > self.dataopen[0]: #self.sma5[0] > self.sma25[0]
                    print("ShortPExit")
                    shortpexit = self.buy(exectype=bt.Order.Market)  
                    order = -1
                    cancelshorttrailexit = self.broker.cancel(shorttrailexit)
                    if (bool(shortptexit)):
                        if(shortptexit.alive()==True):
                            cancelshortptexit = self.broker.cancel(shortptexit)
                    sentryprice = 0
                   
                if order == 0:
                    # Short profit target exit    
                    if((self.datalow[0] <= sentryprice*(1 - self.p.sprofit_target) and self.datahigh[0] >= sentryprice*(1-self.p.sprofit_target) and self.dataopen[0] > sentryprice*(1-self.p.sprofit_target)) or (self.dataopen[0] <= sentryprice*(1-self.p.sprofit_target))):
                        shortptexit = self.buy(exectype=bt.Order.Limit, price=sentryprice*(1-self.p.sprofit_target))
                        cancelshorttrailexit = self.broker.cancel(shorttrailexit)
                        sentryprice = 0
                    else: 
                        # Short stop loss exit    
                        if((self.datalow[0] <= sentryprice*(1+self.p.sstop_loss) and self.datahigh[0] >= sentryprice*(1+self.p.sstop_loss) and self.dataopen[0] < sentryprice*(1+self.p.sstop_loss)) or (self.dataopen[0] >= sentryprice*(1+self.p.sstop_loss))):
                            shortslexit = self.buy(exectype=bt.Order.Stop, price=sentryprice*(1+self.p.sstop_loss))
                            cancelshorttrailexit = self.broker.cancel(shorttrailexit)
                            if (bool(shortptexit)):
                                if(shortptexit.alive()==True):
                                    cancelshortptexit = self.broker.cancel(shortptexit)
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