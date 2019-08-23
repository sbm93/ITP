
def createReports(summary_result, pnl_result, cob_data, annual_result, monthly_result, weekly_result, return_data, duration_data, round_trip_trade, list_of_returns, returns):
    returns_add = list_of_returns[0]
    tpnl = 0
    for index, val in enumerate(list_of_returns):
       cumret = timeseries.cum_returns(val, starting_value=investment)
       tpnl = tpnl + (cumret.shift()*val)
    
       returns_add = returns_add + val
    portvalue = tpnl.cumsum() + tinvestment
    returns_avg = tpnl / portvalue.shift()
    returns_avg[0:2] = 0
    
    
    
    # Fetching Drawdown charts and Data
    
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
    
    
    
    # Fetching Group Charts and Data
    
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

