from backtest.Util import NumUtil
from backtest.Util import DateUtil
from backtest.Constance import StockConst

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from datetime import datetime
import math

def get_sharp_ratio_common(profit_series, none_risk_profit):
    avg_val = profit_series.mean()
    std_val = profit_series.std()
    #stdVal = NumUtil.std(profitSeries)
    #noneRiskProfit = 3.0
    sharp_ratio = (avg_val - none_risk_profit) / std_val;
    #print('noneRiskProfit:' + str(noneRiskProfit))
    #print('avgVal:' + str(avgVal))
    #print('stdVal:' + str(stdVal))
    #print('sharpRatio:' + str(sharpRatio))
    return sharp_ratio

#按年算夏普:用年化无风险收益
def get_sharp_ratio_common_year(profit_series):
    return get_sharp_ratio_common(profit_series, StockConst.NONE_RISK_PROFIT_FOR_YEAR)

#按日算夏普:用年化无风险收益/365天
def get_sharp_ratio_common_day(profit_series):
    return get_sharp_ratio_common(profit_series, StockConst.NONE_RISK_PROFIT_FOR_YEAR / 365)

#obsolete
#用年收益算夏普
def get_sharp_ratio_old(year_list):
    ss = year_list['profit']
    sharp_ratio = get_sharp_ratio_common_year(ss)
    return sharp_ratio

#用日收益算夏普
def get_sharp_ratio(net_value_list):
    ss = net_value_list['changePCT']
    sharp_ratio = get_sharp_ratio_common_day(ss)
    return sharp_ratio

#用日收益算每年的夏普
def get_sharp_ratio_for_each_year(net_value_list):
    sharpRatioList = []
    startYear = DateUtil.datetime2_year_str(net_value_list.index[0])
    endYear = DateUtil.datetime2_year_str(net_value_list.index[-1])

    for year in range(int(startYear), int(endYear) + 1, 1):
        yearStr = str(year)
        # print("yearStr:" + str(yearStr))
        # 把总列表按年切分成子列表
        subNetValueList = net_value_list.ix[yearStr]
        ss = subNetValueList['changePCT']
        sharpRatio = get_sharp_ratio_common_day(ss)
        sharpRatioDict = {'year': yearStr, 'sharpRatio': sharpRatio}
        sharpRatioList.append(sharpRatioDict)

    # 非时间序列DF
    df = pd.DataFrame(sharpRatioList)
    return df;

def create_net_value():
    rows_list = []
    # for row in rows:
    dict1 = {'year': 2016, 'profit': 10}
    dict2 = {'year': 2017, 'profit': 15}

    rows_list.append(dict1)
    rows_list.append(dict2)

    df = pd.DataFrame(rows_list)
    return df

#测试代码 时间索引
def create_net_value2():
    netvalueList = pd.DataFrame(index=pd.date_range('12/25/2016', '1/2/2017'), columns=['changePCT'])
    netvalueList.ix['2016-12-25'] = 1
    netvalueList.ix['2016-12-26'] = 2
    netvalueList.ix['2016-12-27'] = 1
    netvalueList.ix['2016-12-28'] = 2
    netvalueList.ix['2016-12-29'] = 2
    netvalueList.ix['2016-12-30'] = 1
    netvalueList.ix['2016-12-31'] = 2
    netvalueList.ix['2017-01-01'] = 1
    netvalueList.ix['2017-01-02'] = 2
    return netvalueList

"""
#测试代码
netvalueList = createNetValue2()
print(netvalueList)
sharpRatio = getSharpRatio(netvalueList)
print(sharpRatio)
sharpRatioList = getSharpRatioForEachYear(netvalueList)
print(sharpRatioList)
"""

"""
#测试代码
yearList = createNetValue()
print(yearList)
sharpRatio = getSharpRatioOld(yearList)
print(sharpRatio)
"""

"""
    for index, row in yearList.iterrows():
        profit = row['profit']
        print(profit)
"""