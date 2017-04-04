from backtest.Util import NumUtil
from backtest.Util import DateUtil

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from datetime import datetime
import math

def get_max_drop(net_value_list_param):
    net_value_list = net_value_list_param.copy()
    net_value_list.insert(1, 'hightestNetValue', Series())
    net_value_list.insert(2, 'drop', Series())
    hightest = 0
    #算出历史最高,和当日相对于历史最高的回撤
    for index, row in net_value_list.iterrows():
        #print(row['netValue'])
        if row['netValue'] > hightest:
            hightest = row['netValue']
        net_value_list.ix[index, ['hightestNetValue']] = hightest
        net_value_list.ix[index, ['drop']] = NumUtil.get_change_pct(hightest, row['netValue'], 2) * -1

    #最大回撤
    max_drop = net_value_list['drop'].max()

    # 最大回撤
    max_drop_rows=net_value_list.loc[(net_value_list['drop'] == max_drop)]
    # 最大回撤发生日
    max_drop_end_date = DateUtil.datetime2_str(max_drop_rows.index[0]) #& (netValueList.index > maxDropStartDate)
    hightest_net_value = max_drop_rows.ix[0,['hightestNetValue']][0] #['hightestNetValue']

    #print('maxDropEndDate:'+str(maxDropEndDate))
    #print('hightestNetValue:' + str(hightestNetValue))

    # 最大回撤开始日
    # 找到净值最高的记录 且 离开回撤发生日最近
    hightest_rows = net_value_list.loc[(net_value_list['netValue'] == hightest_net_value)]  # & (DateUtil.datetime2Str(netValueList.index) <= maxDropEndDate)
    hightest_rows = hightest_rows.sort_index(ascending=False)
    max_drop_start_date = DateUtil.datetime2_str(hightest_rows.index[0])
    #print('maxDropStartDate:' + str(maxDropStartDate))

    max_drop_dict = {'maxDrop': NumUtil.get_round(max_drop, 2), 'maxDropStartDate': max_drop_start_date, 'maxDropEndDate': max_drop_end_date}

    return max_drop_dict

def get_max_drop_for_each_year(net_value_list):
    #netValueList2 = pd.DataFrame(data=netValueList,columns=['netValue','hightestNetValue'])
    #netValueList2['hightestNetValue'] = 0;

    stock_trade_result_max_drop_list = []
    start_year = DateUtil.datetime2_year_str(net_value_list.index[0])
    end_year = DateUtil.datetime2_year_str(net_value_list.index[-1])

    for year in range(int(start_year), int(end_year)+1, 1):
        year_str = str(year)
        #print("yearStr:" + str(yearStr))
        #把总列表按年切分成子列表
        sub_net_value_list = net_value_list.ix[year_str]
        max_drop_dict = get_max_drop(sub_net_value_list)
        max_drop_dict.setdefault("year",year_str)
        #print(maxDropDict)
        stock_trade_result_max_drop_list.append(max_drop_dict)

    #非时间序列DF
    df = pd.DataFrame(stock_trade_result_max_drop_list)
    return df;


#测试代码 数字索引,2列
def create_net_value():
    rows_list = []
    # for row in rows:
    dict1 = {'netValue': 1, 'Tradeday': '2016-01-01'}
    dict2 = {'netValue': 0.96, 'Tradeday': '2016-01-02'}
    dict3 = {'netValue': 0.94, 'Tradeday': '2016-01-03'}
    dict4 = {'netValue': 1.1, 'Tradeday': '2016-01-04'}
    dict5 = {'netValue': 0.94, 'Tradeday': '2016-01-05'}
    dict6 = {'netValue': 0.91, 'Tradeday': '2016-01-06'}
    dict7 = {'netValue': 1.2, 'Tradeday': '2016-01-07'}
    rows_list.append(dict1)
    rows_list.append(dict2)
    rows_list.append(dict3)
    rows_list.append(dict4)
    rows_list.append(dict5)
    rows_list.append(dict6)
    rows_list.append(dict7)
    df = pd.DataFrame(rows_list)
    return df

#测试代码 时间索引
def create_net_value2():
    netvalueList = pd.DataFrame(index=pd.date_range('1/1/2016', '1/7/2016'), columns=['netValue'])
    netvalueList.ix['2016-01-01'] = 1
    netvalueList.ix['2016-01-02'] = 0.96
    netvalueList.ix['2016-01-03'] = 0.94
    netvalueList.ix['2016-01-04'] = 1.1
    netvalueList.ix['2016-01-05'] = 0.94
    netvalueList.ix['2016-01-06'] = 0.91
    netvalueList.ix['2016-01-07'] = 1.2
    return netvalueList

"""
#测试代码
netValueList = createNetValue2()
print(netValueList)
maxdropList = getMaxDrop(netValueList)
print(maxdropList)
maxdropList2 = getMaxDropForEachYear(netValueList)
print(maxdropList2)
"""


