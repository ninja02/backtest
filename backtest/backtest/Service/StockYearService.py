from backtest.Util import NumUtil
from backtest.Util import DateUtil

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from datetime import datetime
import math

def get_year_profit(df, column=''):
    df = df.sort_index(ascending=True)
    start = df.ix[0][column]
    end = df.ix[-1][column]
    # print("start:" + str(start))
    # print("end:" + str(end))
    profit = NumUtil.get_change_pct(start, end, 2);
    return profit

# yearList = [2016,2017]
#for year in yearList:
# startDate = str(year) + "-01-01"
# endDate = str(year) + "-12-31"
# try:         except: continue
def main(net_value_list):
    #startYear = DateUtil.datetime2YearStr(netValueList.index[0])
    #endYear = DateUtil.datetime2YearStr(netValueList.index[-1]) #len(netValueList) - 1
    net_value_list['year'] = DateUtil.datetime2_year_str(net_value_list.index)
    #print(netValueList)
    #['netValue']
    stockYearList = net_value_list.groupby(net_value_list['year']).apply(get_year_profit, 'netValue')
    # 非时间序列DF
    df = pd.DataFrame(stockYearList, columns=['profit'])
    return df;

#测试代码 时间索引
def create_net_value2():
    netvalue_list = pd.DataFrame(index=pd.date_range('1/1/2016', '1/7/2017'), columns=['netValue'])
    netvalue_list.ix['2016-01-01'] = 1
    netvalue_list.ix['2016-01-02'] = 0.96
    netvalue_list.ix['2016-01-03'] = 0.94
    netvalue_list.ix['2016-01-04'] = 1.1
    netvalue_list.ix['2016-01-05'] = 0.94
    netvalue_list.ix['2016-01-06'] = 0.91
    netvalue_list.ix['2016-12-31'] = 1.2
    netvalue_list.ix['2017-01-01'] = 1.2
    netvalue_list.ix['2017-01-07'] = 1.3
    return netvalue_list

"""
#测试代码
netValueList = createNetValue2()
print(netValueList)
stockYearList = main(netValueList)
#stockYearList.sort_values(by=["year"])
print(stockYearList)
"""