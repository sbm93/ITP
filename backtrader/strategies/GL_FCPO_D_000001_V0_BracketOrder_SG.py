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

# Create a Stratey

lpt = 0.1
lsl = 0.03
ltt = 0.1
lttex = 0.05

spt = 0.1
ssl = 0.03
stt = 0.1
sttex = 0.05

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
        self.sma5 = bt.indicators.SMA(self.data, period=5, plotname='mysma')
        self.sma20 = bt.indicators.SMA(self.data, period=20, plotname='mysma')
        self.smaco = btind.CrossOver(self.sma5,self.sma20)
        self.macdhist = bt.indicators.MACDHisto()

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
        global maxmacdhist
        global minmacdhist
        global lentryprice
        global sentryprice
        global ltrail_flag
        global ltrail_price
        global strail_flag
        global strail_price, order
         
        
        #print(self.datas[0].datetime.date(0))
        #print(self.position.size)

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            if self.smaco[0] > 0 and self.macdhist.macd[0] > self.macdhist.signal[0]:
                        lentryprice = self.dataclose[0]  
                        maxmacdhist = self.macdhist.histo[0]
                        longpentry = self.buy_bracket(price = lentryprice,exectype=bt.Order.Market,
                                                      limitprice=lentryprice*(1+self.p.lprofit_target),limitexec=bt.Order.Limit,
                                                      stopprice=lentryprice*(1-self.p.lstop_loss),stopexec=bt.Order.Stop )
                        order=0
                        #longpentry.addinfo(name=strategyname+'_LE')
                        print('long entry')
                        print(lentryprice)
            else:
                if self.smaco[0] < 0:
                    if self.macdhist.macd[0] < self.macdhist.signal[0]:
                        sentryprice = self.dataclose[0]
                        minmacdhist = self.macdhist.histo[0]
                        #shortpentry = self.sell(exectype=bt.Order.Market)
                        #shortpentry.addinfo(name=strategyname+'_SE')
                        self.order = self.sell_bracket(price=sentryprice,exectype=bt.Order.Market,
                                                       limitprice=sentryprice*(1 - self.p.sprofit_target),limitexec=bt.Order.Limit,
                                                       stopprice=sentryprice*(1+self.p.sstop_loss), stopexec=bt.Order.Stop)
                        order=0
                        print('short entry')
                        print(sentryprice)
        else:
            # Pattern Long exit
            if self.position.size > 0:
                if(self.macdhist.histo[0] > maxmacdhist):
                    maxmacdhist = self.macdhist.histo[0]
                if(self.macdhist.histo[0] < self.macdhist.histo[-1] and self.macdhist.histo[-1] < maxmacdhist):
                    print("LongPExit")
                    self.order = self.sell(exectype=bt.Order.Market) 
                    order = 1
                    lentryprice = 0
                if order == 0:
                    # Long profit target exit    
                    if((self.datalow[0] <= lentryprice*(1+self.p.lprofit_target) and self.datahigh[0] >= lentryprice*(1+self.p.lprofit_target) and self.dataopen[0] < lentryprice*(1+self.p.lprofit_target)) or (self.dataopen[0] >= lentryprice*(1+self.p.lprofit_target))):
                        self.order = self.sell(exectype=bt.Order.Limit, price=lentryprice*(1+self.p.lprofit_target))
                        lentryprice = 0
                    else:
                        # Long stop loss exit    
                        if((self.datalow[0] <= lentryprice*(1-self.p.lstop_loss) and self.datahigh[0] >= lentryprice*(1-self.p.lstop_loss) and self.dataopen[0] > lentryprice*(1-self.p.lstop_loss) ) or (self.dataopen[0] <= lentryprice*(1-self.p.lstop_loss))):
                            print("LSL")
                            print(self.datalow[0] <= lentryprice*(1-self.p.lstop_loss) and self.datahigh[0] >= lentryprice*(1-self.p.lstop_loss))
                            print(lentryprice*(1-self.p.lstop_loss))
                            #self.order = self.sell(exectype=bt.Order.Stop, price=lentryprice*(1-self.p.lstop_loss))
                            self.order = self.sell()
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
                if(self.macdhist.histo[0] < minmacdhist):
                    minmacdhist = self.macdhist.histo[0]
                if(self.macdhist.histo[0] > self.macdhist.histo[-1] and self.macdhist.histo[-1] > minmacdhist):
                    print("ShortPExit")
                    self.order = self.buy(exectype=bt.Order.Market)
                    order = -1
                    sentryprice = 0          
                if order == 0:
                    # Short profit target exit    
                    if((self.datalow[0] <= sentryprice*(1 - self.p.sprofit_target) and self.datahigh[0] >= sentryprice*(1-self.p.sprofit_target) and self.dataopen[0] > sentryprice*(1-self.p.sprofit_target)) or (self.dataopen[0] <= sentryprice*(1-self.p.sprofit_target))):
                        self.order = self.buy(exectype=bt.Order.Limit, price=sentryprice*(1-self.p.sprofit_target))
                        sentryprice = 0
                    else:
                        # Short stop loss exit    
                        if((self.datalow[0] <= sentryprice*(1+self.p.sstop_loss) and self.datahigh[0] >= sentryprice*(1+self.p.sstop_loss) and self.dataopen[0] < sentryprice*(1+self.p.sstop_loss)) or (self.dataopen[0] >= sentryprice*(1+self.p.sstop_loss))):
                            self.order = self.buy(exectype=bt.Order.Stop, price=sentryprice*(1+self.p.sstop_loss))
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