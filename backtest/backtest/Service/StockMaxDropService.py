from backtest.Util import NumUtil
from backtest.Util import DateUtil

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from datetime import datetime
import math

def main(netValueList):
    standardMaxDrop = -5;

    stockTradeResultMaxDropList = []

    startPoint = None;
    startDate = None;
    endDate = None;
    changePCTToStart = None;

    maxDrop = None;
    happenDate = None;
    maxDate = None;
    maxDropNumOfDay = None;

    dateIndexFromStart = 1
    dateIndexFromHappen = 1
    dateIndex = 1

    totalNumOfDay = len(netValueList)

    #for stockTradeResultDailyEntity in netValueList:
    for index, row in netValueList.iterrows():
        msgIsNewMaxDrop = ""
        msgIsNewStartPoint = ""
        msgIsEndPoint = ""
        msgInsert = ""

        currNetValue = row['netValue']
        currDate = DateUtil.datetime2_str(index)

        if (startPoint == None):
            startPoint = currNetValue;
            startDate = currDate;
            dateIndexFromStart = 1;
            dateIndexFromHappen = 1;
            msgIsNewStartPoint = "newStartPoint";

            dateIndexFromStart = dateIndexFromStart + 1;
            dateIndexFromHappen = dateIndexFromHappen + 1;
            dateIndex = dateIndex + 1;

        else:

            changePCTToStart = NumUtil.get_change_pct(startPoint, currNetValue, 2);

            if maxDrop == None:
                check = True
            elif changePCTToStart < maxDrop:
                check = True
            else:
                check = False

            if ((changePCTToStart <= standardMaxDrop) & check):

                if(maxDrop == None):
                    happenDate = currDate;
                    dateIndexFromHappen = 1;

                maxDrop = changePCTToStart;
                maxDate = currDate;

                maxDropNumOfDay = dateIndexFromHappen;
                msgIsNewMaxDrop = "newMaxDrop";

            if((currNetValue >= startPoint) | (dateIndex == totalNumOfDay)):

                if (maxDrop != None):
                    endDate = currDate;

                    #msgInsert = "    [insert]" + startDate + " " + endDate + " " + happenDate + " " + maxDrop + " " + maxDate + " " + maxDropNumOfDay;
                    #StockTradeResultMaxDropEntity stockTradeResultMaxDropEntity = new StockTradeResultMaxDropEntity(
                        # execModelId, startDate, endDate, happenDate, maxDrop, maxDate,
                                          #maxDropNumOfDay, DateUtils.getCurrentDateWithSecond3());

                    #if (stockTradeResultMaxDropList == null):stockTradeResultMaxDropList = new ArrayList();

                    #stockTradeResultMaxDropList.add(stockTradeResultMaxDropEntity);
                    dict1 = {'startDate': startDate, 'endDate':endDate, 'happenDate':happenDate, 'maxDrop':maxDrop, 'maxDate':maxDate}
                    stockTradeResultMaxDropList.append(dict1)

                    maxDrop = None;
                    happenDate = None;
                    maxDate = None;
                    maxDropNumOfDay = None;
                    msgIsEndPoint = "endPoint";

            if (currNetValue >= startPoint):
                startPoint = currNetValue;
                startDate = currDate;
                dateIndexFromStart = 1;
                msgIsNewStartPoint = "newStartPoint";


            dateIndexFromStart = dateIndexFromStart + 1;
            dateIndexFromHappen = dateIndexFromHappen + 1;
            dateIndex = dateIndex + 1;

    #非时间序列DF
    df = pd.DataFrame(stockTradeResultMaxDropList)
    return df;

#测试代码 数字索引,2列
def createNetValue():
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
def createNetValue2():
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
maxdropList = main(netValueList)
maxdropList.sort_values(by=["startDate","endDate"])
print(maxdropList)
"""