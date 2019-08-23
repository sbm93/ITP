'''
Importing the required packages
importing Strategies as classes

'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import_package = False
#import datetime  # For datetime objects
#from datetime import datetime
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

from pyfolio import timeseries
# Import the backtrader platform
import backtrader as bt
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo
#from report import Cereb
import datetime
import pandas as pd

import backtrader.indicators as btind
from backtrader.strategies import gl_fcpo_d_000007_v0_Single
from backtrader.strategies import gl_fcpo_d_000003_v0_single_outsample
from backtrader.strategies import gl_fcpo_d_000003_v0_BracketOrder_outsample
from backtrader.strategies import gl_fcpo_d_000001_v0_Single
from backtrader.strategies import gl_fcpo_d_000003_v0_BracketOrde_SG
from backtrader.strategies import gl_fcpo_d_000001_v0_Single_BracketOrder
from backtrader.strategies import gl_fcpo_d_000001_v0_Multiple
from backtrader.strategies import sg_fcpo_d_000001_v1_Single
from backtrader.strategies import gl_fcpo_d_000003_v0_single

from backtrader.strategies import gl_fcpo_d_000001_v0_BracketOrder
from backtrader.strategies import gl_fcpo_d_000009_v0_Single
from backtrader.strategies import gl_fcpo_d_000011_v0_Single
from backtrader.strategies import gl_fcpo_d_000013_v0_Single
from backtrader.strategies import gl_fcpo_d_000013_v1_Single
from backtrader.strategies import gl_fcpo_d_000013_v1_Single
from backtrader.strategies import gl_fcpo_d_000015_v0_Multiple
from backtrader.strategies import custom_strat_vo_single_stochastic

from pandas_datareader import data as web
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pyfolio as pf
import numpy as np

import matplotlib

import_package = True


'''
Variable declaration

'''
import_Data = False
#path = 'C:/users/shubham.sharma1/Desktop/antima files/Download 24/project/python-problem-work/st-python'
#reportPath = 'C:/users/shubham.sharma1/Desktop/antima files/Download 24/project/python-problem-work/st-python/reports_24_05_19/'

path = 'D:/Projects-Global-Logic/RGEI/Documents/'
reportPath = 'C:/Users/sushil.dubey1/ITP/12July/'
filename = 'FCPO3-OHLCV.csv'
instrument = "FCPO"

strategy_list = {
         1: gl_fcpo_d_000007_v0_Single.CUSTOM_STRAT_VO_SINGLE,
         2: gl_fcpo_d_000003_v0_single_outsample.GL_FCPO_D_000003_V0_SINGLE_OUTPUTSAMPLE,
         3: gl_fcpo_d_000003_v0_BracketOrder_outsample.BRACKET_ORDER_OUTSAMPLE,
         4: gl_fcpo_d_000003_v0_BracketOrde_SG.BRACKET_ORDER_SG,
         5: gl_fcpo_d_000001_v0_Single_BracketOrder.SINGLE_BRACKET_ORDER,
         6: gl_fcpo_d_000001_v0_Multiple.CUSTOM_STRAT_MULT,
         7: gl_fcpo_d_000003_v0_single.CUSTOM_STRAT_THREE_VO_SINGLE,
         8: gl_fcpo_d_000001_v0_BracketOrder.BRACKET_ORDER_STR,
         9: gl_fcpo_d_000009_v0_Single.CUSTOM_STRAT_NINE_VO_SRT,
         10: gl_fcpo_d_000011_v0_Single.CUSTOM_STRAT_ELEVEN_VO_SRT,
         11: gl_fcpo_d_000013_v0_Single.CUSTOM_STRAT_THIRTEEN_VO_SRT,
         12: gl_fcpo_d_000015_v0_Multiple.CUSTOM_STRAT_FIFTEEN_VO_SRT,
         13: gl_fcpo_d_000013_v1_Single.CUSTOM_STRAT_THIRTEEN_V1_SRT
     }
    

strategy_index = [1,2,3,4,5,6,7,8,9,10,11,12]
noosstrategies = len(strategy_index)
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
todate = datetime.datetime.strptime(last_row.iloc[len(last_row)-1]['Date'], '%Y-%d-%m')

import_Data = True


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
   
class CUSTOM_STRAT_VO_SINGLE(bt.Strategy):
    
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
        dd = pd.read_csv(os.path.join(path,filename))
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
        self.rsi = bt.indicators.RSI_EMA(self.dataclose,period=12)
        self.rsi20 = bt.indicators.RSI_EMA(self.dataclose,period=20)
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

    def next(self):
        global histtrades
        global maxmacdhist
        global minmacdhist
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
        if not self.position: #self.macdhist.macd[0] > self.macdhist.signal[0] and 
            if self.datahigh[0] > self.bbands.top[0] and self.datahigh[-1] > self.bbands.top[-1] and self.dataclose[0] > self.dataopen[0] and self.dataclose[-1] > self.dataopen[-1]:
            #self.dataclose[0] > self.dataopen[0] and (self.datahigh[0]-self.datalow[0]) < (self.datahigh[-1]-self.datalow[-1]) and self.datahigh[0] < self.datahigh[-1]: # self.datahigh[-2] < self.datahigh[-1] 
                        lentryprice = self.dataclose[0]  
                        maxmacdhist = self.macdhist.histo[0]
                        longpentry = self.buy(price = lentryprice,exectype=bt.Order.Market)
                        longtrailexit = self.sell(exectype=bt.Order.StopTrail, trailpercent=self.p.ltrail_target_exit)
                        longpentry.addinfo(name=strategyname+'_LE')
                        print('long entry')
                        print(lentryprice)
            else:
                if self.datalow[0] < self.bbands.bot[0] and self.datalow[-1] < self.bbands.bot[-1]  and self.dataclose[0] < self.dataopen[0] and  self.dataclose[-1] < self.dataopen[-1]:
                #self.dataclose[0] < self.dataopen[0] and (self.datahigh[0]-self.datalow[0]) < (self.datahigh[-1]-self.datalow[-1]) and self.datahigh[0] > self.datahigh[-1]: #self.datalow[-2] > self.datalow[-1]
                #self.dataopen[0] > self.bbands.top[0] and self.dataclose[0] < self.bbands.top[0] and (self.datahigh[0]-self.dataopen[0]) > (self.dataclose[0]-self.datalow[0]):
                        sentryprice = self.dataclose[0]
                        minmacdhist = self.macdhist.histo[0]
                        shortpentry = self.sell(price=sentryprice,exectype=bt.Order.Market)
                        shorttrailexit = self.buy(exectype=bt.Order.StopTrail, trailpercent=self.p.strail_target_exit)
                        shortpentry.addinfo(name=strategyname+'_SE')
                        
                        print('short entry')
                        print(sentryprice)
        else:
            # Pattern Long exit
            if self.position.size > 0:
                if(self.macdhist.histo[0] > maxmacdhist):
                    maxmacdhist = self.macdhist.histo[0]
                if self.macdhist.histo[0] < self.macdhist.histo[-1] and self.macdhist.histo[-1] < maxmacdhist:
                    print("LongPExit")
                    longpexit = self.sell(exectype=bt.Order.Market) 
                    cancellongtrailexit = self.broker.cancel(longtrailexit)
                    lentryprice = 0
                
                # Long profit target exit    
                if(self.datalow[0] <= lentryprice*(1+self.p.lprofit_target) and self.datahigh[0] >= lentryprice*(1+self.p.lprofit_target)):
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
                if(self.macdhist.histo[0] < minmacdhist):
                    minmacdhist = self.macdhist.histo[0]
                if self.macdhist.histo[0] > self.macdhist.histo[-1] and self.macdhist.histo[-1] > minmacdhist:
                #self.bbands.bot[0] > self.bbands.bot[-1] and self.dataclose[0] > self.dataopen[0]:#and self.dataclose[-1] > self.bbands.top[-1]: #self.rsi[0] > self.rsi[-1] and self.rsi[-1] > minrsi :
                    print("ShortPExit")
                    shortpexit = self.buy(exectype=bt.Order.Market)  
                    cancelshorttrailexit = self.broker.cancel(shorttrailexit)
                    sentryprice = 0          
                
                # Short profit target exit    
                if(self.datalow[0] <= sentryprice*(1 - self.p.sprofit_target) and self.datahigh[0] >= sentryprice*(1-self.p.sprofit_target)):
                    shortptexit = self.buy(exectype=bt.Order.Limit, price=sentryprice*(1-self.p.sprofit_target))
                    cancelshorttrailexit = self.broker.cancel(shorttrailexit)
                    sentryprice = 0
                # Short stop loss exit    
                if(self.datalow[0] <= sentryprice*(1+self.p.sstop_loss) and self.datahigh[0] >= sentryprice*(1+self.p.sstop_loss)):
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
               
               
               

def run_strategy(strategy, variables):
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
    cerebro.addstrategy(strategy)

    # Set our desired cash start
    cerebro.broker.setcash(variables['investment'])
    cerebro.broker.setcommission(commission=variables['commission'], margin=variables['investment']*(1-riskpercentage), mult=variables['lotsize'],leverage=leverage)

    # Run over everything{}
    result = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    return result


def gen_report(returns, positions, transactions, gross_lev, benchmark, variables):
    returns, trip_tear_fig, round_trip_data, drawdown_df, cob_data, return_tear_sheet_charts, round_trip_trades, show_perf_stats = pf.create_full_tear_sheet(returns=returns,
                            positions=positions,
                            transactions=transactions,
                            market_data=None,
                            benchmark_rets=benchmark,
                            slippage=0,
                            live_start_date=None,
                            sector_mappings=None,
                            bayesian=False,
                            round_trips=True,
                            hide_positions=False,
                            cone_std=(1.0, 1.5, 2.0),
                            bootstrap=False,
                            unadjusted_returns=None,
                            style_factor_panel=None,
                            sectors=None,
                            caps=None,
                            shares_held=variables['lotsize'],
                            volumes=None,
                            percentile=None,
                            turnover_denom='AGB',
                            set_context=True,
                            factor_returns=None,
                            factor_loadings=None,
                            pos_in_dollars=True,
                            header_rows=None,
                            investment=variables['investment'])
    return round_trip_data, drawdown_df


result_sg = run_strategy(sg_fcpo_d_000001_v1_Single.SG_FCPO_Single_v1, strategy_variable['SG'])
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



lpt = 0.1
lsl = 0.03
ltt = 0.05
lttex = 0.03

spt = 0.1
ssl = 0.03
stt = 0.05
sttex = 0.03
final_results_list= []
for lpt in np.arange(8, 20, 3):
    for lsl in np.arange(2, 4, 0.5):
        for lttex in np.arange(2, 4, 0.5):
            for spt in np.arange(8, 20, 2):
                for ssl in np.arange(2, 4, 0.5):
                    for sttex in np.arange(2, 4, 0.5):
                        res = run_strategy(CUSTOM_STRAT_VO_SINGLE, strategy_variable['SG'])                        
                        pyfolio = res[0].analyzers.getbyname('pyfolio')
                        returns, positions, transactions, gross_lev = pyfolio.get_pf_items()
                        round_trip_data, drawdown_df = gen_report(returns, positions, transactions, gross_lev, benchmark, strategy_variable['SG'])
                        print(round_trip_data)
                        print(drawdown_df)
                        df_per = drawdown_df['percentage']
                        df_abs = drawdown_df['absolute']
                        rd_ret = round_trip_data['returns']
                        final_results_list.append([lpt,lsl,lttex,spt,ssl,sttex,rd_ret[rd_ret.columns[0]].iloc[0],round_trip_data['pnl'][round_trip_data['pnl'].columns[0]].iloc[0].round(2), df_per[df_per.columns[0]].iloc[0], df_abs[df_abs.columns[0]].iloc[0] ])
                        

pd.DataFrame(final_results_list, columns = ['lpt','lsl','lttex','spt','ssl','sttex', 'return', 'pnl', 'drawdown (%)', 'drawdown (abs)']).to_csv("optimization_result.csv")


