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
    
    print(strategy_result)
    for key, value in strategy_result.items():
        
        returns, trip_tear_fig, round_trip_data, drawdown_df, cob_data, return_tear_sheet_charts, round_trip_trades, show_perf_stats = pf.create_full_tear_sheet(returns=value['returns'],
                               positions=value['positions'],
                               transactions=value['transactions'],
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
        
        summary_result.append(round_trip_data['summary'])
        pnl_result.append(round_trip_data['pnl'])
        annual_result.append(cob_data['annual_return'])
        monthly_result.append(cob_data['monthly_return'].fillna(0))
        weekly_result.append(pd.DataFrame(cob_data['club_data']['is_weekly']).fillna(0))
        return_data.append(round_trip_data['returns'])
        duration_data.append(round_trip_data['duration'])
        round_trip_trade.append(round_trip_trades)
        list_of_returns.append(returns)
    
    
    # In[ ]:
    
    
    
    
    
    # In[ ]:
    
    
    returns_add = list_of_returns[0]
    tpnl = 0
    for index, val in enumerate(list_of_returns):
       cumret = timeseries.cum_returns(val, starting_value=variables['investment'])
       tpnl = tpnl + (cumret.shift()*val)
    
       returns_add = returns_add + val
    portvalue = tpnl.cumsum() + variables['tinvestment']
    returns_avg = tpnl / portvalue.shift()
    returns_avg[0:2] = 0
    
    
    # In[ ]:
    
    
    
    
    
    # In[ ]:
    
    
    # Fetching Drawdown charts and Data
    
    drawdown_fig, drawdown_df = pf.create_returns_tear_sheet_multi(
            returns_avg,
            live_start_date=None,
            cone_std=(1.0, 1.5, 2.0),
            benchmark_rets=benchmark,
            bootstrap=False,
            set_context=True,
            investment=variables['tinvestment'],
            shares_held=variables['lotsize'])
    
    
    # In[ ]:
    
    
    # Fetching cimulative returns and Annual Data
    cumulative_fig, show_perf_stats = pf.create_returns_tear_sheet_cum(
            returns_avg,
            live_start_date=None,
            cone_std=(1.0, 1.5, 2.0),
            benchmark_rets=benchmark,
            bootstrap=False,
            set_context=True,
            investment=variables['tinvestment'])
    
    
    # In[ ]:
    
    
    # Fetching Group Charts and Data
    
    sheer_fig, cob_new_data = pf.create_returns_tear_sheet_ret(
            returns_avg,
            live_start_date=None,
            cone_std=(1.0, 1.5, 2.0),
            benchmark_rets=benchmark,
            bootstrap=False,
            set_context=True,
            investment=variables['investment'])
    
    
    # In[ ]:
    
    
    
    
    
    # In[ ]:
    
    
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
    
    
    # In[ ]:
    
    
    # Creating PnL table
    
    pnl_tmp = pnl_result.copy()
    pnl_tmp_first = pnl_tmp[0]
    for index, val in enumerate(pnl_tmp[1:]):
        pnl_tmp_first.iloc[0] = pnl_tmp_first.iloc[0].add(val.iloc[0],fill_value=0)  
        pnl_tmp_first.iloc[1] = pnl_tmp_first.iloc[1].add(val.iloc[1],fill_value=0)
        pnl_tmp_first.iloc[2] = pnl_tmp_first.iloc[2].add(val.iloc[2],fill_value=0)
        pnl_tmp_first.iloc[3] = pnl_tmp_first.iloc[1].div(pnl_tmp_first.iloc[2].abs(),fill_value=0) # Need to discuss logic here
    
    
    # In[ ]:
    
    
    # Creating Annual result Table
    
    annual_result_first = annual_result[0]
    for index, val in enumerate(annual_result[1:]):
        annual_result_first = annual_result_first + val
    annual_result_first = annual_result_first/len(annual_result)
    
    
    # In[ ]:
    
    
    # Creating Monthly Result Table
    
    monthly_result_first = monthly_result[0]
    for index, val in enumerate(monthly_result[1:]):
        monthly_result_first = monthly_result_first + val
    
    monthly_result_first = monthly_result_first/len(monthly_result) 
    print(monthly_result_first)
    
    
    # In[ ]:
    
    
    # Creating Weekly result Table
    weekly_result_first = weekly_result[0]
    for index, val in enumerate(weekly_result[1:]):
        weekly_result_first = weekly_result_first + val
    
    weekly_result_first = weekly_result_first/len(weekly_result)
    
    
    # In[ ]:
    
    
    # Profit Data Table
    
    dict = {
        'Proftitable Years in (%)': (annual_result_first[annual_result_first[0]>=0].count()/annual_result_first.count())*100,
        'Monthly profit in (%)': (monthly_result_first[monthly_result_first >= 0].count().sum()/monthly_result_first.count().sum())*100,
        'Weekly profit in (%)':(weekly_result_first[weekly_result_first>=0].count()/weekly_result_first.count())*100
    }
    profit_data = pd.DataFrame(dict)
    
    
    # In[ ]:
    
    
    # Returns Data Table
    return_data_first = return_data[0]
    for index, val in enumerate(return_data[1:]):
        return_data_first.iloc[0] = return_data_first.iloc[0].add(val.iloc[0], fill_value=0)
        return_data_first.iloc[1] = return_data_first.iloc[1].add(val.iloc[1],fill_value=0)
        return_data_first.iloc[2] = return_data_first.iloc[[2]].append(val.iloc[[2]]).max()
        return_data_first.iloc[3] = return_data_first.iloc[[3]].append(val.iloc[[3]]).min()
    
    return_data_first.iloc[1] = return_data_first.iloc[1]/len(return_data)
    return_data_first.iloc[0] = (return_data_first.iloc[0]/(variables['investment']*len(return_data))) * 100   
    return_data_first.iloc[1] = (return_data_first.iloc[1]/(variables['investment'] * len(return_data))) * 100   
    return_data_first.iloc[1] =  return_data_first.iloc[1] * noosstrategies 
    
    
    # In[ ]:
    
    
    # Calculating Duration Data
    duration_data_first = duration_data[0]
    
    for index, val in enumerate(duration_data[1:]):
        duration_data_first = duration_data_first + val
    duration_data_first = duration_data_first/len(duration_data)
    
    
    # In[ ]:
    
    
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
    
    
    # In[ ]:
    
    
    # Creating Pyfolio Report
    
    
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
                         "max_drawdown":"Max drawdown (%)", 
                         "information_ratio":"information ratio", 
                         "alpha":"alpha (%)", 
                         "beta":"beta (%)"}, 
                                     inplace = True) 
    
    show_perf_stats.loc['Annual return (%)'] = show_perf_stats.iloc[0] * 100
    show_perf_stats.loc['Annual volatility (%)'] = show_perf_stats.iloc[1] * 100
    show_perf_stats.loc['Max drawdown (%)'] = drawdown_per['net drawdown in %'].iloc[0]
    show_perf_stats.loc['alpha (%)'] = show_perf_stats.loc['alpha (%)']*100
    show_perf_stats.loc['beta (%)'] = show_perf_stats.loc['beta (%)']*100
    show_perf_stats.loc['information ratio'] = show_perf_stats.loc['information ratio'] * 100
    show_perf_stats.loc['Max drawdown ($)'] = drawdown_abs['net drawdown'].iloc[0]
    
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
    HTML(string=html_out).write_pdf("report"+str(datetime.datetime.now()).replace(":", "_").replace(" ", "_").replace(".","_")+".pdf")
    #HTML(string=html_out).write_pdf("SG1_cons_report_2019_1.3.pdf")
