#!/usr/bin/env python
# coding: utf-8

'''
Importing the required packages
importing Strategies as classes
'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import_package = False
import datetime  # For datetime objects
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
# Importing Singapore Startegy
from backtrader.strategies import sg_fcpo_d_000001_v1_Single

#Importing GL Startegies
from backtrader.strategies import gl_fcpo_d_000003_v0_Outsample
from backtrader.strategies import gl_fcpo_d_000007_v0_Single_Bracket
from backtrader.strategies import gl_fcpo_d_000001_v0_Single
from backtrader.strategies import gl_fcpo_d_000014_v0_Single
from backtrader.strategies import gl_fcpo_d_000006_v0_single_stochastic
from backtrader.strategies import gl_fcpo_d_000006_v0_BracketOrderstochastic
from backtrader.strategies import gl_fcpo_d_000013_v1_Single
from backtrader.strategies import gl_fcpo_d_000001_v0_BracketOrder
from backtrader.strategies import gl_fcpo_d_000015_v0_Multiple
from backtrader.strategies import gl_fcpo_d_000011_v0_Single
from backtrader.strategies import gl_fcpo_d_000009_v0_Single
from backtrader.strategies import gl_fcpo_d_000003_v0_single
from backtrader.strategies import gl_fcpo_d_000007_v0_Single
from backtrader.strategies import gl_fcpo_d_000003_v0_BracketOrde_SG
from backtrader.strategies import gl_fcpo_d_000003_v0_single_outsample

# from backtrader.strategies import custom_strat_vo_single_stochastic


from pandas_datareader import data as web
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pyfolio as pf

import matplotlib
import_package = True


#Variable declaration

import_Data = False
path = 'D:/Projects-Global-Logic/RGEI/Documents/'
reportPath = 'C:/Users/sushil.dubey1/ITP/reports_24_05_19/'
filename = 'FCPO3-OHLCV.csv'
instrument = "FCPO"

#strategyname = 'SG_FCPO_D_000002'

strategy = 'GL'

#noosstrategies = 3

strategy_index = [1,2,3,4,5,6,7,8,9,10,11,12]
noosstrategies = len(strategy_index)

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

fromdate = datetime.datetime(2017,12,31)
todate = datetime.datetime(2019,6, 13)
# fromdate = datetime.datetime(2000, 1, 1)
# last_row = pd.read_csv(path+"/"+filename)
# todate = datetime.datetime.strptime(last_row.iloc[len(last_row)-1]['Date'], '%Y-%m-%d') + datetime.timedelta(days=1)
#todate = datetime.datetime(2019,2, 28)+ datetime.timedelta(days=1)
import_Data = True

# Defining strategies to run the reports

strategy_list = {
        gl_fcpo_d_000003_v0_Outsample.THREE_VO_STRAT_OUTSAMPLE,
        gl_fcpo_d_000007_v0_Single_Bracket.SEVEN_VO_SINGLE_BRACKET,
        gl_fcpo_d_000001_v0_Single.ONE_VO_STRAT_SINGLE,
        gl_fcpo_d_000014_v0_Single.CUSTOM_STRAT_FOURTEEN_VO_SRT,
        gl_fcpo_d_000006_v0_single_stochastic.SINGLE_STOCHASTIC_STR,
        gl_fcpo_d_000006_v0_BracketOrderstochastic.BRACKET_ORDER_STOCHASTIC_STR,
        gl_fcpo_d_000013_v1_Single.CUSTOM_STRAT_THIRTEEN_V1_SRT,
        gl_fcpo_d_000001_v0_BracketOrder.BRACKET_ORDER_STR,
        gl_fcpo_d_000015_v0_Multiple.CUSTOM_STRAT_FIFTEEN_VO_SRT,
        gl_fcpo_d_000011_v0_Single.CUSTOM_STRAT_ELEVEN_VO_SRT,
        gl_fcpo_d_000009_v0_Single.CUSTOM_STRAT_NINE_VO_SRT,
        gl_fcpo_d_000003_v0_single.CUSTOM_STRAT_THREE_VO_SINGLE,
        gl_fcpo_d_000007_v0_Single.CUSTOM_STRAT_VO_SINGLE,
        gl_fcpo_d_000003_v0_BracketOrde_SG.BRACKET_ORDER_SG,
        gl_fcpo_d_000003_v0_single_outsample.GL_FCPO_D_000003_V0_SINGLE_OUTPUTSAMPLE
  }

# Creating custom CSV Data feed

i = 0
result_dict = {}

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
    cerebro.addstrategy(cls)

    # Set our desired cash start
    cerebro.broker.setcash(investment)
    cerebro.broker.setcommission(commission=commission, margin=investment*(1-riskpercentage), mult=lotsize,leverage=leverage)

    # Run over everything{}
    result_dict['result_'+str(i)] = cerebro.run()
    i = i+1
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    return result_dict


if strategy=='SG':
    pyfolio = result_dict["result_0"][0].analyzers.getbyname('pyfolio')
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


# Fetching the data for Pyfolio Report

def gen_report(strategy_result, benchmark, variables):
    summary_result = []
    pnl_result = []
    annual_result = []
    monthly_result = []
    weekly_result = []
    return_data = []
    duration_data = []
    round_trip_trade = []
    list_of_returns = []
    
    for key, value in result_dict.items():
        print("printing key value")
        print(key, value)
        
        pyfolio = value[0].analyzers.getbyname('pyfolio')
        returns, positions, transactions, gross_lev = pyfolio.get_pf_items()
        positions.to_csv("position_"+key+".csv")
        returns.to_csv("returs_"+key+".csv")
        returns.to_csv("test1"+".csv")
        
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
                               shares_held=lotsize,
                               volumes=None,
                               percentile=None,
                               turnover_denom='AGB',
                               set_context=True,
                               factor_returns=None,
                               factor_loadings=None,
                               pos_in_dollars=True,
                               header_rows=None,
                               investment=investment)
        
        round_trip_trades.to_csv(key+"_roundTrip.csv")
        summary_result.append(round_trip_data['summary'])
        pnl_result.append(round_trip_data['pnl'])
        annual_result.append(cob_data['annual_return'])
        monthly_result.append(cob_data['monthly_return'].fillna(0))
        weekly_result.append(pd.DataFrame(cob_data['club_data']['is_weekly']).fillna(0))
        return_data.append(round_trip_data['returns'])
        duration_data.append(round_trip_data['duration'])
        round_trip_trade.append(round_trip_trades)
        list_of_returns.append(returns)
        createReport([round_trip_data['summary']],[round_trip_data['pnl']],[cob_data['annual_return']],[cob_data['monthly_return'].fillna(0)],[pd.DataFrame(cob_data['club_data']['is_weekly']).fillna(0)],[round_trip_data['returns']],[round_trip_data['duration']],[round_trip_trades],[returns])
        
    
def createReport(summary_result,pnl_result,annual_result, monthly_result, weekly_result, return_data, duration_data,round_trip_trade, list_of_returns):
    returns_add = list_of_returns[0]
    tpnl = 0
    for index, val in enumerate(list_of_returns):
       cumret = timeseries.cum_returns(val, starting_value=investment)
       tpnl = tpnl + (cumret.shift()*val)
    
       returns_add = returns_add + val
    portvalue = tpnl.cumsum() + tinvestment
    returns_avg = tpnl / portvalue.shift()
    returns_avg[0:2] = 0


    drawdown_fig, drawdown_df = pf.create_returns_tear_sheet_multi(
        returns_avg,
        live_start_date=None,
        cone_std=(1.0, 1.5, 2.0),
        benchmark_rets=benchmark,
        bootstrap=False,
        set_context=True,
        investment=tinvestment,
        shares_held=lotsize)
    
    
    # Fetching cimulative returns and Annual Data
    cumulative_fig, show_perf_stats = pf.create_returns_tear_sheet_cum(
        returns_avg,
        live_start_date=None,
        cone_std=(1.0, 1.5, 2.0),
        benchmark_rets=benchmark,
        bootstrap=False,
        set_context=True,
        investment=tinvestment)


    sheer_fig, cob_new_data = pf.create_returns_tear_sheet_ret(
            returns_avg,
            live_start_date=None,
            cone_std=(1.0, 1.5, 2.0),
            benchmark_rets=benchmark,
            bootstrap=False,
            set_context=True,
            investment=investment)

# Creating Summary Table Data

    summary_tmp = summary_result
    summary_data = summary_tmp[0]
    for index, val in enumerate(summary_tmp[1:]):
        summary_data.iloc[0] = val.iloc[0].add(summary_data.iloc[0],fill_value=0)
        summary_data.iloc[1] = val.iloc[1].add(summary_data.iloc[1],fill_value=0)
        summary_data.iloc[2] = val.iloc[2].add(summary_data.iloc[2],fill_value=0)
        summary_data.iloc[3] = summary_data.iloc[1].div(summary_data.iloc[0],fill_value=0) * 100
        summary_data.iloc[4] = summary_data.iloc[[4]].append(val.iloc[[4]]).max()
        summary_data.iloc[5] = summary_data.iloc[[5]].append(val.iloc[[5]]).min()


    # Creating PnL table
    
    pnl_tmp = pnl_result.copy()
    pnl_tmp_first = pnl_tmp[0]
    for index, val in enumerate(pnl_tmp[1:]):
        pnl_tmp_first.iloc[0] = pnl_tmp_first.iloc[0].add(val.iloc[0],fill_value=0)  
        pnl_tmp_first.iloc[1] = pnl_tmp_first.iloc[1].add(val.iloc[1],fill_value=0)
        pnl_tmp_first.iloc[2] = pnl_tmp_first.iloc[2].add(val.iloc[2],fill_value=0)
        pnl_tmp_first.iloc[3] = pnl_tmp_first.iloc[1].div(pnl_tmp_first.iloc[2].abs(),fill_value=0) # Need to discuss logic here


    pnl_tmp_first['All trades'].iloc[0]


# Creating Annual result Table

    annual_result_first = annual_result[0]
    for index, val in enumerate(annual_result[1:]):
        annual_result_first = annual_result_first + val
    annual_result_first = annual_result_first/len(annual_result)

    # Creating Monthly Result Table
    
    monthly_result_first = monthly_result[0]
    for index, val in enumerate(monthly_result[1:]):
        monthly_result_first = monthly_result_first + val
    
    monthly_result_first = monthly_result_first/len(monthly_result) 
    print(monthly_result_first)


    # Creating Weekly result Table
    weekly_result_first = weekly_result[0]
    for index, val in enumerate(weekly_result[1:]):
        weekly_result_first = weekly_result_first + val
    
    weekly_result_first = weekly_result_first/len(weekly_result)



    # Profit Data Table
    
    dict = {
        'Proftitable Years in (%)': (annual_result_first[annual_result_first[0]>=0].count()/annual_result_first.count())*100,
        'Monthly profit in (%)': (monthly_result_first[monthly_result_first >= 0].count().sum()/monthly_result_first.count().sum())*100,
        'Weekly profit in (%)':(weekly_result_first[weekly_result_first>=0].count()/weekly_result_first.count())*100
    }
    profit_data = pd.DataFrame(dict)


    # Returns Data Table
    return_data_first = return_data[0]
    for index, val in enumerate(return_data[1:]):
        return_data_first.iloc[0] = return_data_first.iloc[0].add(val.iloc[0], fill_value=0)
        return_data_first.iloc[1] = return_data_first.iloc[1].add(val.iloc[1],fill_value=0)
        return_data_first.iloc[2] = return_data_first.iloc[[2]].append(val.iloc[[2]]).max()
        return_data_first.iloc[3] = return_data_first.iloc[[3]].append(val.iloc[[3]]).min()
    
    # print(return_data_first.iloc[1])
    # return_data_first.iloc[1] = return_data_first.iloc[1]  /len(return_data)
    return_data_first.iloc[0] = (return_data_first.iloc[0]/(investment*len(return_data))) * 100   
    # return_data_first.iloc[1] = (return_data_first.iloc[1]/(investment * len(return_data))) * 100 
    # print(return_data_first.iloc[1])
    # print(investment)
    # print(len(return_data))
    # return_data_first.iloc[1] =  return_data_first.iloc[1] * noosstrategies 
    # print(return_data_first.iloc[1])
    return_data_first.iloc[1] = (return_data_first.iloc[1]/(investment * summary_data.iloc[0])) * 100 
    
    print(return_data_first)


    # Calculating Duration Data
    duration_data_first = duration_data[0]
    
    for index, val in enumerate(duration_data[1:]):
        duration_data_first = duration_data_first + val
    duration_data_first = duration_data_first/len(duration_data)

    # Method for Image Parsing
    
    import io
    import base64
    def imageParser(img):
        buf = io.BytesIO()
        img.savefig(buf, format='jpeg')
        buf.seek(0)
        buffer = b''.join(buf)
        b2 = base64.b64encode(buffer)
        return b2.decode('utf-8')
    

    # Creating Pyfolio Report
    
    from datetime import datetime
    pnl_data = pd.DataFrame.from_dict(round_trip_data['pnl']) 
    
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("myreport.html")
    weekly_df = pd.DataFrame(cob_data['club_data']['is_weekly'])
    
    drawdown_per = pd.DataFrame.from_dict(drawdown_df['percentage'])
    drawdown_per['net drawdown in %'] = drawdown_per['net drawdown in %'].astype(float).round(2)
    drawdown_abs = pd.DataFrame.from_dict(drawdown_df['absolute'])
    drawdown_abs['net drawdown'] = drawdown_abs['net drawdown'].astype(float).round(2)
    
    show_perf_stats.rename(index = {"annual_return": "Annual return (%)", 
                         "annual_volatility":"Annual volatility (%)", 
                         "sharpe_ratio":"Sharpe ratio", 
                         "information_ratio":"information ratio", 
                         "PnL_Max _DD": "PnL to Max DD",
                         "Return_Max _DD": "Return to Max DD",
                         "alpha":"alpha (%)", 
                         "beta":"beta (%)",
                          "max_drawdown":"Max drawdown (%)",
                          "max_drawdown":"Max drawdown ($)"
                                   }, 
                                     inplace = True) 
    
    show_perf_stats.loc['Annual return (%)'] = show_perf_stats.iloc[0] * 100
    show_perf_stats.loc['Annual volatility (%)'] = show_perf_stats.iloc[1] * 100
    show_perf_stats.loc['alpha (%)'] = show_perf_stats.loc['alpha (%)']*100
    show_perf_stats.loc['beta (%)'] = show_perf_stats.loc['beta (%)']*100
    show_perf_stats.loc['PnL to Max DD'] = (pnl_tmp_first['All trades'].iloc[0])/drawdown_abs['net drawdown'].iloc[0]
    show_perf_stats.loc['Return to Max DD'] = (return_data_first.iloc[0]['All trades'])/drawdown_per['net drawdown in %'].iloc[0]
    show_perf_stats.loc['information ratio'] = show_perf_stats.loc['information ratio'] 
    show_perf_stats.loc['Max drawdown ($)'] = drawdown_abs['net drawdown'].iloc[0]
    show_perf_stats.loc['Max drawdown (%)'] = drawdown_per['net drawdown in %'].iloc[0]
    
    
    template_vars = {"title" : "Data for Round Trip",
                     "PnL_data_table": pnl_tmp_first.round(2).to_html(),
                     "summary_data_table": summary_data.round(2).to_html(),
                     "profit_data_table" : profit_data.round(2).to_html(),
                     "duration_data_table": duration_data_first.round(2).to_html(),
                     "returns_data_table": (return_data_first.round(2)).to_html(),
                     "drawdown_data_table": drawdown_per.to_html(index=False),
                     "drawdown_abs_data_table": drawdown_abs.to_html(index=False),
                     "perf_stats_data_table": (show_perf_stats.round(2)).to_html(),
                     "monthly_data_table": ((monthly_result_first * 100).round(3)).to_html(),
                     "yearly_data_table": ((annual_result_first * 100).round(2)).to_html(),
                     "return_tear_fig_1": imageParser(cumulative_fig),
                     "return_tear_fig_2": imageParser(drawdown_fig),
                     "return_tear_fig_3": imageParser(sheer_fig),
                     "from_date": fromdate.date(),
                     "to_date": todate.date()
                    }
    
    html_out = template.render(template_vars)
    
    with open('my_new_html_file.html', 'w') as f:
        f.write(html_out)
    
    from weasyprint import HTML
    #HTML(string=html_out).write_pdf(reportPath+"report"+str(datetime.now()).replace(":", "_").replace(" ", "_").replace(".","_")+".pdf")
    HTML(string=html_out).write_pdf("GL_Consolidated_report_2016_2019_1.6.pdf")
    
    
result_sg = run_strategy(sg_fcpo_d_000001_v1_Single.SG_FCPO_Single_v1, strategy_variable['SG'])
sg_res = {0:{}}
pyfolio = result_sg[0].analyzers.getbyname('pyfolio')
sg_res[0]['returns'], sg_res[0]['positions'], sg_res[0]['transactions'], sg_res[0]['gross_lev']= pyfolio.get_pf_items()
sg_res[0]['returns'].to_csv("BenchMark.csv")


# Reading Benchmark Data from CSV file for Singapore Strategy

retdata = pd.read_csv('BenchMark.csv',header=None)
retdata.columns = ['Date', 'Return']
pd.to_datetime(retdata['Date'], errors='coerce')
retdata = retdata.set_index('Date')
retdata.index.names = [None] 
benchmark = retdata.ix[:,0].rename("BenchMark")
benchmark.index = pd.to_datetime(benchmark.index, errors='coerce')
benchmark = benchmark.tz_localize('UTC')

gen_report(sg_res, benchmark, strategy_variable['SG'])

# run  all strategy

strategy_result = {}
print("------------------------")
for idx in strategy_index:
    print(idx)
    print(strategy_list)
    res = run_strategy(strategy_list[idx], strategy_variable['GL'])
    strategy_result[idx] = {}
    pyfolio = res[0].analyzers.getbyname('pyfolio')
    strategy_result[idx]['returns'], strategy_result[idx]['positions'], strategy_result[idx]['transactions'], strategy_result[idx]['gross_lev']= pyfolio.get_pf_items()


gen_report(strategy_result, benchmark, strategy_variable['GL'])
# generate reports

#gen_report(strategy_result)    
    
    

def position_consolidation_report():
        import pandas as pd
        resultant_data = pd.DataFrame(columns=["Datetime", 
                                               'Strategy 1', 'Strategy 2', 
                                               'Strategy 3', 'Strategy 4', 
                                               'Strategy 5', 'Strategy 6', 'Strategy 7', 
                                               'Strategy 8', 'Strategy 9', 
                                               'Strategy 10', 'Strategy 11', 
                                               'Strategy 12', 'Strategy 13',
                                               'Strategy 14', 'Strategy 15',
                                               'Short', 'Long', 'Net'])
        
        positions = pd.read_csv("Position_result_1.csv", index_col=0)
        resultant_data['Datetime'] = positions.index.values
        resultant_data = resultant_data.fillna(0, inplace=False)
        
        for i in range(0,15):
            round_trips = pd.read_csv("result_"+str(i)+"_roundTrip.csv").drop(['Unnamed: 0'],axis=1)
            for rt, value in round_trips.iterrows():
                if value['long'] == False:
                     resultant_data.loc[(resultant_data['Datetime'] > value['open_dt']) & (resultant_data['Datetime'] < value['close_dt']), "Strategy "+str(i+1)] = resultant_data["Strategy "+str(i+1)]-1
                else:
                    resultant_data.loc[(resultant_data['Datetime'] > value['open_dt']) & (resultant_data['Datetime'] < value['close_dt']), "Strategy "+str(i+1)] = resultant_data["Strategy "+str(i+1)]+1
                    
    
        short = resultant_data[resultant_data<0].sum(axis=1)
        long = resultant_data[resultant_data>0].sum(axis=1)
        net = short + long
        resultant_data['Short'] = short
        resultant_data['Long'] = long
        resultant_data['Net'] = net
        
        resultant_data.to_csv("position_consolidation.csv", index=False)
