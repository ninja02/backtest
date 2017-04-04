from backtest.Util import NumUtil
from backtest.Util import DateUtil

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from datetime import datetime
import math


def cal(yearList):
    print('mean:'+str(yearList['profit'].mean))

def avg(yearList):
    if (len(yearList) > 0):
        ave = 0.0;
        sum = 0.0;
        for index, row in yearList.iterrows():
            profit = row['profit']
            sum = sum + profit;

        ave = sum / len(yearList);
        return ave

def var(yearList):
    if (len(yearList) > 0):
        ave = 0.0;
        sum = 0.0;
        ret = 0.0;
        for index, row in yearList.iterrows():
            profit = row['profit']
            sum = sum + profit

        ave = sum / len(yearList)

        for index, row in yearList.iterrows():
            profit = row['profit']
            ret = ret + (ave - profit) * (ave - profit)

        ret = ret / len(yearList)

        return ret

def std(yearList):
    v = var(yearList);
    std = math.sqrt(v)
    return std


def main(yearList):
    sharpRatioList = []

    avgVal = avg(yearList)
    stdVal = std(yearList)
    noneRiskProfit = 3.0
    sharpRatio = (avgVal - noneRiskProfit) / stdVal;
    #print(avgVal)
    #print(stdVal)
    #print(sharpRatio)

    return sharpRatio

def createNetValue():
    rows_list = []
    # for row in rows:
    dict1 = {'year': 2016, 'profit': 10}
    dict2 = {'year': 2017, 'profit': 15}

    rows_list.append(dict1)
    rows_list.append(dict2)

    df = pd.DataFrame(rows_list)
    return df

"""
#测试代码
yearList = createNetValue()
print(yearList)
sharpRatio = main(yearList)
print(sharpRatio)
"""

"""
    for index, row in yearList.iterrows():
        profit = row['profit']
        print(profit)
"""