import pandas as pd
import numpy as np
from pandas.io.pytables import Term
from pandas import Series, DataFrame
from backtestData.Constance import StockConst
from backtestData.Util import DateUtil
from backtestData.Util import TimeUtil
from backtestData.Util import SelectUtil
import datetime
import calendar,time
import math

#获取信号数据
#Mom_5_D.h5:
#    index: TradingDay InnerCode
#    columns: Mom
#Mom_5_0302.h5:
#    TradingDay,WindCode,Mom
@TimeUtil.check_consumed_time4
def loadSignalData(signalDataAddr=''):
    print('loadSignalData1')
    if signalDataAddr == '':
        signalDataAddr = (StockConst.ROOT + StockConst.SIGNAL_DATA_H5)
    print(signalDataAddr)
    #Mom_5_D.h5
    store = pd.HDFStore(signalDataAddr)
    #print(store)
    signalData = store.select('Data'
        #[
        # Term('InnerCode', '=', 3),
        # Term('TradingDay', '>=', startDate),
        # Term('TradingDay', '<=', endDate),
        #Term('columns', '=', 'Mom')
        #]
    );
    #print(signalData.columns)
    #print(signalData)
    return signalData

# def loadSignalDataToDic(signalDataAddr=''):
#     signalData = loadSignalData(signalDataAddr)
#     tradingDayDic={}
#     for index, row in signalData.iterrows():
#         tradingDay = index[0]
#         innerCode = index[1]
#         tradingDayStr = DateUtil.datetime2Str(tradingDay)
#         if tradingDayStr not in tradingDayDic:
#             innerCodeDic={}
#             tradingDayDic.setdefault(tradingDayStr,innerCodeDic)
#         else:
#             innerCodeDic = tradingDayDic.get(tradingDayStr)
#         innerCodeDic.setdefault(innerCode,row)
#
#     return tradingDayDic

# dict = loadSignalDataToDic()
# print(dict.get('2004-01-12'))


@TimeUtil.check_consumed_time3
def loadSignalDataByDate(startDate,endDate,addr=''):
    print('loadSignalDataByDate')
    if addr == '':
        addr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
    #Mom_5_D.h5
    store = pd.HDFStore(addr)
    #print(store)
    t1 = pd.Timestamp(startDate)
    t2 = pd.Timestamp(endDate)
    signalData = store.select('Data',
        where = [
                'TradingDay>=Timestamp("'+startDate+'")',
                'TradingDay<=Timestamp("'+endDate+'")'
                ]
        # [
        # # Term('InnerCode', '=', 3),
        # # Term('TradingDay', '>=', startDate),
        # # Term('TradingDay', '<=', endDate)
        # pd.Term('Mom', '>=', '5')
        # ]
    );
    #print(signalData.columns)
    #print(signalData)
    return signalData

#直接从h5文件取得列名
def getColumsFromH5(addr):
    store = pd.HDFStore(addr)
    c = store.select(key = 'Data', stop = 0)
    # print(c)
    # print(c.columns.tolist())
    return c.columns.tolist()

#
def getLastRecordFromH5(addr):
    store = pd.HDFStore(addr)
    c = store.select(key = 'Data', start = -1)
    return c
    # return c.index[0][0]
    # print(c)
    # print(c.columns.tolist())
    # return c.columns.tolist()

def getFirstRecordFromH5(addr):
    store = pd.HDFStore(addr)
    c = store.select(key = 'Data', stop = 1)
    return c

#获取行情数据
#DailyQuote_Mi.h5
#    index: TradingDay InnerCode
#    columns:
#    'PrevClosePrice', 'OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice',
#    'TurnoverVolume', 'TurnoverValue', 'TurnoverDeals'
#BRPrice_0302.h5:
#    TradingDay,WindCode,DlyRet,VWAP,TurnoverVolume,Adj,CumAdj,BROpenPrice,BRHighPrice,BRLowPrice,BRClosePrice
@TimeUtil.check_consumed_time4
def loadDailyQuote(addr=''):
    print('loadDailyQuote')
    if addr == '':
        addr = StockConst.ROOT + StockConst.DAILY_QUOTE_H5
    #DailyQuote_Mi.h5
    store = pd.HDFStore(addr)
    dailyQuote = store.select('Data')
    #print(store)
    #print(dailyQuote.columns)
    #print(dailyQuote)
    return dailyQuote

#在DailyQuote_Mi的基础上加了buyFlg和sellFlg
@TimeUtil.check_consumed_time4
def loadNewDailyQuote(addr=''):
    print('loadNewDailyQuote')
    if addr == '':
        addr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
    #New_DailyQuote_Mi.h5
    store = pd.HDFStore(addr)
    dailyQuote = store.select('Data')
    #print(store)
    #print(dailyQuote)
    return dailyQuote

@TimeUtil.check_consumed_time3
def loadNewDailyQuoteByDate(startDate,endDate,addr=''):
    print('loadNewDailyQuoteByDate')
    if addr == '':
        addr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
    #Mom_5_D.h5
    store = pd.HDFStore(addr)
    #print(store)
    t1 = pd.Timestamp(startDate)
    t2 = pd.Timestamp(endDate)
    dailyQuote = store.select('Data',
        where = [
                'TradingDay>=Timestamp("'+startDate+'")',
                'TradingDay<=Timestamp("'+endDate+'")'
                ]
    )
    #print(dailyQuote.columns)
    #print(dailyQuote)
    return dailyQuote

# signalData = loadNewDailyQuoteByDate('20040112','20040115','')
# print(signalData)

#把一个df导出到h5
def exportToHDFStore(df, addr):
    store = pd.HDFStore(addr)
    #data_columns=['ComplaintType', 'Descriptor', 'Agency']
    store.append('Data', df)


#按TradingDay InnerCode查询
#停牌取最近一个交易日
#dailyQuote: dataFrame
def selectByInnerCodeAndDate(dailyQuote,tradingDate,innerCode):
    #找不到数据(停牌): 取最近一个交易日
    if (tradingDate, innerCode) not in dailyQuote.index:
        #entity = {StockConst.sellFlg: -1, StockConst.buyFlg: -1}]
        df = selectByPrevTradingDay(dailyQuote, tradingDate, innerCode)
        lastTradingDay = df.index[0][0] #为了格式和else中的一致
        entity = df.ix[(lastTradingDay, innerCode)] #为了格式和else中的一致
    else:
        entity = dailyQuote.ix[(tradingDate, innerCode)]
    return entity

#TODO 最近一个交易日也没有数据的情况
def selectSignalByDateAndInnerCode(signalData, tradingDate, innerCode):
    # 找不到数据(停牌): 取最近一个交易日
    if (tradingDate, innerCode) not in signalData.index:
        # print('selectSignalByDateAndInnerCode-stop')
        # entity = {StockConst.sellFlg: -1, StockConst.buyFlg: -1}]
        # print(tradingDate)
        # print(innerCode)
        df = selectSignalByPrevTradingDay(signalData, tradingDate, innerCode)
        lastTradingDay = df.index[0][0]
        entity = df.ix[(lastTradingDay, innerCode)]
    else:
        # print('selectSignalByDateAndInnerCode-none')
        entity = signalData.ix[(tradingDate, innerCode)]
    return entity

#test
def selectSignalByDateAndInnerCode2(signalData, tradingDate, innerCode, field):
    # 找不到数据(停牌): 取最近一个交易日
    if (tradingDate, innerCode) not in signalData.index:
        # print('selectSignalByDateAndInnerCode-stop')
        # entity = {StockConst.sellFlg: -1, StockConst.buyFlg: -1}]
        # print(tradingDate)
        # print(innerCode)
        df = selectSignalByPrevTradingDay(signalData, tradingDate, innerCode)
        lastTradingDay = df.index[0][0]
        entity = df.ix[(lastTradingDay, innerCode)]
    else:
        # print('selectSignalByDateAndInnerCode-none')
        entity = signalData.ix[(tradingDate, innerCode)]
    return entity[field]

#是否因为停牌和一字涨停不能买入
def checkIfCannotBuy(dailyQuote,tradingDate,innerCode):
    # 找不到数据: 停牌
    if (tradingDate, innerCode) not in dailyQuote.index:
        # print('isstop')
        return True
    else:
        entity = dailyQuote.ix[(tradingDate, innerCode)]
        #一字涨停
        if entity[StockConst.BUY_FLG] == -1:
            # print('isyizizhangting')
            return True
    return False

#是否因为停牌和一字涨停不能卖出
def checkIfCannotSell(dailyQuote,tradingDate,innerCode):
    # 找不到数据: 停牌
    if (tradingDate, innerCode) not in dailyQuote.index:
        # print('tradingDate:'+DateUtil.datetime2Str(tradingDate))
        # print('innerCode:' + str(innerCode))
        # print('checkIfCannotSell-stop')
        return True
    else:
        entity = dailyQuote.ix[(tradingDate, innerCode)]
        #一字跌停
        if entity[StockConst.SELL_FLG] == -1:
            # print('checkIfCannotSell-yzdt')
            return True
        else:
            # print('checkIfCannotSell-none')
            pass
    return False


"""暂时不用
#退市的股票，取最后一个交易日
def selectByLastDay(dailyQuote,innerCode):
    #dailyQuote = loadNewDailyQuote()
    dailyQuote2 = selectByInnerCode(dailyQuote, innerCode)
    dailyQuote2 = dailyQuote2[(dailyQuote2[StockConst.TurnoverVolume] != float(0)) & (dailyQuote2[StockConst.ClosePrice] != 0)]
    dailyQuote2 = dailyQuote2.sort_index(ascending=False)
    #closePrice = dailyQuote2['ClosePrice']
    #print(closePrice)
    return dailyQuote2[0:1]
"""
#tradingDate前最后一个交易日
def selectByPrevTradingDay(dailyQuote, tradingDate, innerCode):
    dailyQuote = selectByInnerCode(dailyQuote, innerCode)
    t2 = pd.Timestamp(tradingDate)
    dailyQuote = dailyQuote.loc[:t2, :]
    dailyQuote = dailyQuote.sort_index(ascending=False)
    return dailyQuote[0:1]

#tradingDate前最后一个交易日
def selectSignalByPrevTradingDay(signalData, tradingDate, innerCode):
    signalData = selectSignalByInnerCode(signalData, innerCode)
    t2 = pd.Timestamp(tradingDate)
    signalData = signalData.loc[:t2, :]
    signalData = signalData.sort_index(ascending=False)
    return signalData[0:1]

#按日期查询 ok
def selectByDate(dailyQuote,startDate,endDate):
    #dailyQuote2 = dailyQuote[(dailyQuote['TradingDay'] >= startDate) & (dailyQuote['TradingDay'] <= endDate)]
    #dailyQuote2 = dailyQuote.ix[startDate:endDate] 这种方法有报错的风险
    t1 = pd.Timestamp(startDate)
    t2 = pd.Timestamp(endDate)
    dailyQuote2 = dailyQuote.loc[t1:t2, :]
    return dailyQuote2

def selectSignalByDate(signalData,startDate,endDate):
    #dailyQuote2 = dailyQuote[(dailyQuote['TradingDay'] >= startDate) & (dailyQuote['TradingDay'] <= endDate)]
    #dailyQuote2 = dailyQuote.ix[startDate:endDate] 这种方法有报错的风险
    t1 = pd.Timestamp(startDate)
    t2 = pd.Timestamp(endDate)
    signalData2 = signalData.loc[t1:t2, :]
    return signalData2

"""
#弃用
#按innerCode查询
def selectByInnerCodeOld(dailyQuote,innerCode):
    dailyQuote[StockConst.InnerCode] = dailyQuote.index.get_level_values(1)
    dailyQuote2 = dailyQuote[(dailyQuote[StockConst.InnerCode] == innerCode)]
    return dailyQuote2
"""

#按innerCode查询
def selectByInnerCode(dailyQuote,innerCode):
    dailyQuote = dailyQuote[dailyQuote.index.get_level_values(1) == innerCode]
    return dailyQuote

#按innerCode查询
def selectSignalByInnerCode(signalData,innerCode):
    signalData = signalData[signalData.index.get_level_values(1) == innerCode]
    return signalData


#'2016-01-01':'2016-01-31'
#用信号数据取得唯一性日期
#筛选,取得索引,去重
#返回:列表
@TimeUtil.check_consumed_time5
def selectDateFromSignal(signalData,startDate='',endDate=''):
    print('selectDateFromSignal')
    #筛选
    df2 = signalData
    if startDate:
        if endDate:
            t1 = pd.Timestamp(startDate)
            t2 = pd.Timestamp(endDate)
            df2 = signalData.loc[t1:t2,:]
    #print(df2)
    #取得索引,去重
    #l2 = getIndexAndDistinct(df2)
    l2 = list(df2.index.get_level_values(StockConst.TRADINGDAY).unique())
    return l2

#数据源1
def addBuySellFlg1(dailyQuote):
    dailyQuote[StockConst.SELL_FLG] = np.where(
        # 一字跌停 或 停牌：-1
        (
            (
                (dailyQuote[StockConst.HIGH_PRICE] == dailyQuote[StockConst.LOW_PRICE]) & (
                    dailyQuote[StockConst.LOW_PRICE] < dailyQuote[StockConst.PREV_CLOSE_PRICE])  # 一字跌停
            ) | (dailyQuote[StockConst.CLOSE_PRICE] == 0) | (dailyQuote[StockConst.TURNOVER_VOLUME] == float(0))  # 停牌
        ), -1, 0
    )
    dailyQuote[StockConst.BUY_FLG] = np.where(
        # 一字涨停 或 停牌：-1
        (
            (
                (dailyQuote[StockConst.HIGH_PRICE] == dailyQuote[StockConst.LOW_PRICE]) & (
                    dailyQuote[StockConst.HIGH_PRICE] > dailyQuote[StockConst.PREV_CLOSE_PRICE])  # 一字涨停
            ) | (dailyQuote[StockConst.CLOSE_PRICE] == 0) | (dailyQuote[StockConst.TURNOVER_VOLUME] == float(0))  # 停牌
        ), -1, 0
    )
#数据源2
def addBuySellFlg2(dailyQuote):
    dailyQuote[StockConst.SELL_FLG] = np.where(
        # 一字跌停 或 停牌：-1
        (
            (
                (dailyQuote[StockConst.HIGH_PRICE] == dailyQuote[StockConst.LOW_PRICE]) & (
                    (dailyQuote[StockConst.DailyReturn] - 1) < 0)  # 一字跌停
            ) | (dailyQuote[StockConst.CLOSE_PRICE] == 0) | (dailyQuote[StockConst.TURNOVER_VOLUME] == float(0))  # 停牌
        ), -1, 0
    )
    dailyQuote[StockConst.BUY_FLG] = np.where(
        # 一字涨停 或 停牌：-1
        (
            (
                (dailyQuote[StockConst.HIGH_PRICE] == dailyQuote[StockConst.LOW_PRICE]) & (
                    (dailyQuote[StockConst.DailyReturn] - 1) > 0)  # 一字涨停
            ) | (dailyQuote[StockConst.CLOSE_PRICE] == 0) | (dailyQuote[StockConst.TURNOVER_VOLUME] == float(0))  # 停牌
        ), -1, 0
    )

#sellFlg: -1不能卖出
#buyFlg: -1不能买入
def addBuySellFlg(dailyQuoteParam):
    dailyQuote = dailyQuoteParam.copy()
    if StockConst.DATA_SOURCE_NO == 1:
        addBuySellFlg1(dailyQuote)
    elif StockConst.DATA_SOURCE_NO == 2:
        addBuySellFlg2(dailyQuote)
    return dailyQuote





#只执行1次
#加BuySellFlg到DailyQuote
#分批导出到h5文件
def addBuySellFlgAndExport(addr):
    dailyQuote = loadDailyQuote(addr)
    startDate = dailyQuote.index[0][0]
    endDate = dailyQuote.index[-1][0]
    startYear = DateUtil.datetime2_year_str(startDate)
    endYear = DateUtil.datetime2_year_str(endDate)
    FORMAT = "%d-%d-%d"
    #c = time.strftime('%Y%m%d', time.strptime(y, '%Y-%m-%d'))
    for year in range(int(startYear), int(endYear) + 1, 1):
        for month in range(1,13):
            d = calendar.monthrange(year, month)
            exportStartDate = FORMAT % (year, month, 1)
            exportEndDate = FORMAT % (year, month, d[1])
            #exportStartDate = str(year)+'-'+addZero(month)+'-'+'01'
            #exportEndDate = str(year) + '-' + addZero(month) + '-' + getMonthEndDay(month)
            subDailyQuote = selectByDate(dailyQuote, exportStartDate, exportEndDate)
            print('exportStartDate:' + exportStartDate)
            print('exportEndDate:' + exportEndDate)
            print('dailyQuote:'+str(len(subDailyQuote)))
            if(len(subDailyQuote) > 0):
                newSubDailyQuote = addBuySellFlg(subDailyQuote)
                exportToHDFStore(newSubDailyQuote, StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5)

# 用于界面
# 只执行1次
# 加2列到signalData: Mom2, Mom3 (假数据)
# 分批导出到h5文件
def createFakeSignalData(addr):
    signalData = loadSignalData(addr)
    startDate = signalData.index[0][0]
    endDate = signalData.index[-1][0]
    startYear = DateUtil.datetime2_year_str(startDate)
    endYear = DateUtil.datetime2_year_str(endDate)
    FORMAT = "%d-%d-%d"
    # c = time.strftime('%Y%m%d', time.strptime(y, '%Y-%m-%d'))
    for year in range(int(startYear), int(endYear) + 1, 1):
        for month in range(1, 13):
            d = calendar.monthrange(year, month)
            exportStartDate = FORMAT % (year, month, 1)
            exportEndDate = FORMAT % (year, month, d[1])
            # exportStartDate = str(year)+'-'+addZero(month)+'-'+'01'
            # exportEndDate = str(year) + '-' + addZero(month) + '-' + getMonthEndDay(month)
            subSignalData = selectByDate(signalData, exportStartDate, exportEndDate)
            print('exportStartDate:' + exportStartDate)
            print('exportEndDate:' + exportEndDate)
            print('subSignalData:' + str(len(subSignalData)))
            if (len(subSignalData) > 0):
                newSubSignalData = subSignalData.copy()
                newSubSignalData['Mom2'] = subSignalData['Mom']
                newSubSignalData['Mom3'] = subSignalData['Mom']
                exportToHDFStore(newSubSignalData, StockConst.ROOT + StockConst.FAKE_SIGNAL_DATA_H5)

#只执行1次
# 加BuyFlg 到 groupedSignalData
# 导出到csv文件
def addBuySellFlgToSignalData(signalDataAddr,dailyQuoteAddr):
    signalData = loadSignalData(signalDataAddr)
    dailyQuote = loadNewDailyQuote(dailyQuoteAddr)
    groupedSignalData = signalData.groupby(level=StockConst.TRADINGDAY).apply(SelectUtil.top, 5, StockConst.MOM, False)
    groupedSignalData.insert(1, StockConst.BUY_FLG, Series())
    groupedSignalData.insert(2, StockConst.SELL_FLG, Series())
    for index, row in groupedSignalData.iterrows():
        # print('tradingDate:'+str(index[0])+',innerCode:'+str(index[2]))
        if (index[0], index[2]) not in dailyQuote.index:
            groupedSignalData.ix[index, [StockConst.BUY_FLG]] = ''
        else:
            groupedSignalData.ix[index, [StockConst.BUY_FLG]] = dailyQuote.ix[(index[0], index[2]), [StockConst.BUY_FLG]]

        if (index[0], index[2]) not in dailyQuote.index:
            groupedSignalData.ix[index, [StockConst.SELL_FLG]] = ''
        else:
            groupedSignalData.ix[index, [StockConst.SELL_FLG]] = dailyQuote.ix[(index[0], index[2]), [StockConst.SELL_FLG]]

    groupedSignalData.to_csv(StockConst.ROOT + '\export\groupedSignalData.csv')
    # print(groupedSignalData)

#只执行1次
# 加BuyFlg 到 groupedSignalData
# 导出到csv文件
def addBuySellFlgToSignalData2(signalDataAddr,dailyQuoteAddr):
    signalData = loadSignalData(signalDataAddr)
    dailyQuote = loadNewDailyQuote(dailyQuoteAddr)
    groupedSignalData = signalData.groupby(level=StockConst.TRADINGDAY, as_index=False).apply(SelectUtil.top, 5, StockConst.MOM, False)
    groupedSignalData[StockConst.BUY_FLG] = dailyQuote[StockConst.BUY_FLG]
    groupedSignalData[StockConst.SELL_FLG] = dailyQuote[StockConst.SELL_FLG]
    # groupedSignalData.insert(1, StockConst.buyFlg, Series())
    # groupedSignalData.insert(2, StockConst.sellFlg, Series())
    # for index, row in groupedSignalData.iterrows():
    #     # print('tradingDate:'+str(index[0])+',innerCode:'+str(index[2]))
    #     groupedSignalData.ix[index, [StockConst.buyFlg]] = dailyQuote.ix[(index[0], index[2]), [StockConst.buyFlg]]
    #     groupedSignalData.ix[index, [StockConst.sellFlg]] = dailyQuote.ix[(index[0], index[2]), [StockConst.sellFlg]]
    groupedSignalData.to_csv(StockConst.ROOT + '\export\groupedSignalData.csv')
    # print(groupedSignalData)

def test10(addr):
    signalData = loadSignalData(addr)
    groupedSignalData = signalData.groupby(level=StockConst.TRADINGDAY, as_index=False).apply(SelectUtil.top, 5, StockConst.MOM, False)
    print(groupedSignalData)

#########################################################
def printByInnerCodeAndDate(addr):
    dailyQuote = loadDailyQuote(addr)
    dailyQuote = selectByInnerCodeAndDate(dailyQuote, '2004-01-17', '000049.SZ')
    print(dailyQuote)

def printByInnerCode(innerCode,addr):
    dailyQuote = loadNewDailyQuote(addr)
    # dailyQuote = selectByDate(dailyQuote,'2004-01-05','2004-01-06')
    # dailyQuote = selectByInnerCodeAndDate(dailyQuote,'2004-01-05','000049.SZ')
    #'000049.SZ'
    dailyQuote = selectByInnerCode(dailyQuote, innerCode)
    dailyQuote.to_csv(StockConst.ROOT + '\export\dailyQuoteDebug.csv')
    print(dailyQuote)

#分组信号
def printGroupedSingalData(addr):
    signalData = loadSignalData(addr)
    groupedSignalData = signalData.groupby(level=StockConst.TRADINGDAY).apply(SelectUtil.top, 5, StockConst.MOM, False)
    groupedSignalData.to_csv(StockConst.ROOT + '\export\groupedSignalData.csv')

def printSingalDataByDate(date,addr):
    signalData = loadSignalData(addr)
    t1 = pd.Timestamp(date)
    #t2 = pd.Timestamp(endDate)
    #signalData = signalData.loc[t1:t2, :]
    signalData = signalData[signalData.index.get_level_values(0) == t1]
    signalData = signalData.sort_values(by=[StockConst.MOM], ascending=False)
    print(signalData)


#信号的行情数据 '2001-07-30'
def debugDailyQuote(groupedSignalData,date,dailyQuote):
    """ """
    # 行情数据Debug
    #dailyQuoteToDebug = pd.DataFrame()
    signalDataToDebug = groupedSignalData.ix[date]
    print('行情数据:')
    #print('signalDataToDebug:'+str(len(signalDataToDebug)))
    for index, row in signalDataToDebug.iterrows():
        tradingDate = index[0]
        innerCode = index[1]
        dailyQuoteRow = selectByInnerCodeAndDate(dailyQuote, tradingDate, innerCode)
        #dailyQuoteToDebug.append(dailyQuoteRow)
        print(dailyQuoteRow)
    #dailyQuoteToDebug.to_csv(StockConst.root + '\export\dailyQuoteToDebug.csv')

# test
@TimeUtil.check_consumed_time2
def exportSignal():
    signalData = loadSignalData(StockConst.ROOT + '/Mom_5_0302.h5')
    # signalData.to_csv(StockConst.root + '\export2\signalData.csv')
    # signalData.to_excel(StockConst.root + '\export2\signalData.xls', sheet_name='Sheet1')
    signalData.to_json(StockConst.ROOT + '\export2\signalData.json')
    signalData.to_hdf(StockConst.ROOT + '\export2\signalData.h5')

# # test
# @TimeUtil.checkConsumedTime2
# def exportSignal():
#     signalData = loadSignalData(StockConst.root + '/Mom_5_0302.h5')
#     signalData.to_excel(StockConst.root + '\export2\signalData.csv')

#假数据1
def createSignalDataHill():
    # dateList = ['2010-01-01','2010-01-02','2010-01-03','2010-01-04']
    dateList1 = pd.date_range('2004-01-01','2004-06-30')
    dateList2 = pd.date_range('2004-07-01', '2004-12-31')

    df1 = createSignalDataHillMain(dateList1, True)
    df2 = createSignalDataHillMain(dateList2, False)
    df = df1.append(df2)
    # print(df)
    exportToHDFStore(df, StockConst.ROOT + '/export/SignalDataHill.h5')
    # df.to_csv(StockConst.root + '\export\SignalDataHill.csv')

#假数据1
def createSignalDataHillMain(dateList,asc):
    # tickerList = [1,2,3,4]
    # df = pd.DataFrame(data=tickerList,index=dateList,columns='Mom')
    # data = {'Mom': [4, 5, 6, 7]}
    df = pd.DataFrame(columns=['TradingDay', 'WindCode', 'WindCode2', 'Mom'])
    for date in dateList:
        subdf = pd.DataFrame({'TradingDay':date,'WindCode':range(1,21),'WindCode2':range(1,21)})
        df = df.append(subdf)

    df = df.set_index(['TradingDay','WindCode'])
    df = df.groupby(level='TradingDay').apply(createMomHill,asc)
    # print(df)
    return df

#假数据1
def createMomHill(df, asc=True):
    df['Mom'] = df['WindCode2'].rank(ascending=asc,method='first')
    return df

#假数据2
def createDailyQuoteHill():
    # dateList = ['2010-01-01','2010-01-02','2010-01-03','2010-01-04']
    dateList = pd.date_range('2004-01-01', '2004-12-31')
    tickerList1 = range(1,11)
    tickerList2 = range(11,21)

    df1 = createDailyQuoteHillMain(dateList, tickerList1, -1)
    df2 = createDailyQuoteHillMain(dateList, tickerList2, 1)
    df = df1.append(df2)
    # print(df)
    # exportToHDFStore(df, StockConst.root + '/export/DailyQuoteHill.h5')
    # df.to_csv(StockConst.root + '\export\DailyQuoteHill.csv')
    df.to_hdf(StockConst.ROOT + '/export/DailyQuoteHill.h5', 'Data')

#假数据2
def createDailyQuoteHillMain(dateList,tickerList,dir):
    # tickerList = [1,2,3,4]
    # df = pd.DataFrame(data=tickerList,index=dateList,columns='Mom')
    # data = {'Mom': [4, 5, 6, 7]}
    df = pd.DataFrame(columns=['TradingDay', 'WindCode', 'TradingDay2', 'BRClosePrice', 'VWAP', 'CumAdj', 'buyFlg', 'sellFlg'])
    for date in dateList:
        subdf = pd.DataFrame({'TradingDay':date,'WindCode':tickerList,'TradingDay2':date})
        df = df.append(subdf)

    df = df.set_index(['TradingDay','WindCode'])
    df = df.groupby(level='WindCode').apply(createPriceHill2,dir)
    # print(df)
    return df

#假数据2
def createPriceHill2(df, dir=1):
    initPrice = 1000
    # df['rowno'] = df['TradingDay2'].rank(ascending=True, method='first')
    rowno = 1
    for index, row in df.iterrows():
        df.ix[index,'BRClosePrice'] = initPrice * math.pow( (1 + (dir) * 0.001) , rowno )
        #mypow( (1 + (dir) * 0.001) , df['rowno'] ) #math.pow( (1 + (dir) * 0.001) , df['rowno'] )
        # df['BRClosePrice'] = df['TradingDay2'].rank(ascending=True, method='first')
        df.ix[index,'VWAP'] = df.ix[index,'BRClosePrice']
        df.ix[index,'CumAdj'] = 1.0
        df.ix[index,'buyFlg'] = ''
        df.ix[index,'sellFlg'] = ''
        rowno += 1
    return df

#not work
def createPriceHill(df, dir=1):
    initPrice = 1000
    df['rowno'] = df['TradingDay2'].rank(ascending=True, method='first')
    df['BRClosePrice'] = math.pow( (1 + (dir) * 0.001) , range(1,len(df)+1) )
    #mypow( (1 + (dir) * 0.001) , df['rowno'] ) #math.pow( (1 + (dir) * 0.001) , df['rowno'] )
    # df['BRClosePrice'] = df['TradingDay2'].rank(ascending=True, method='first')
    df['VWAP'] = df['BRClosePrice']
    df['CumAdj'] = 1
    df['buyFlg'] = ''
    df['sellFlg'] = ''
    return df

# dailyQuote = loadNewDailyQuote('')
# start = time.clock()
# entity = dailyQuote.loc[('2004-01-12', '000049.SZ')]
# end = time.clock()
# print("main花费时间：%f s" % (end - start))
# print(entity)

# def mypow(a, times):
#     ret = 1
#     for x in range(times):
#         ret = ret * a
#     return ret

# createSignalDataHill()
# createDailyQuoteHill()

# exportSignal()

#loadNewDailyQuote()
#'2016-01-05':'2016-01-08'

#printByInnerCodeAndDate()

#printGroupedSingalData()

#printSingalDataByDate('2004-01-06')

# createFakeSignalData()

# getColumsFromH5('')

# print(getFirstRecordFromH5(StockConst.root+StockConst.fakeSignalDataH5).index[0][0])

# signalData = loadSignalData('')
# print(signalData)

# dailyQuote = loadNewDailyQuote(StockConst.root + '/export/DailyQuoteHill.h5')
# print(dailyQuote)

#测试 导出一个子集到h5文件
# addBuySellFlgAndExport()

"""
dailyQuote = loadNewDailyQuote()
df = selectByInnerCodeAndDate(dailyQuote,'2004-02-10','000521.SZ')
print(df)
"""

"""
#dailyQuote = selectDateFromSignal(dailyQuote)#'2016-01-01','2016-01-08'
dailyQuote = loadDailyQuote()
#signalData = loadSignalData()
#print(signalData)
dailyQuote = selectByDate(dailyQuote,'2004-01-05','2004-01-05')
print(dailyQuote)
"""

"""
dailyQuote = loadDailyQuote()
dailyQuote2 = dailyQuote.ix['2016', :]
print(dailyQuote2)
"""

"""
dailyQuote = loadDailyQuote()
df = selectByDate(dailyQuote,'2016-01-01','2016-01-05')
print(df)
"""

#print(dailyQuote2)
"""
signalData = loadSignalData()
ss = signalData.index.get_level_values(0)
l2 = list(set(ss))
#l2.sort(key=signalData.index)
l2.sort()
print(l2)
"""



"""
signalData = loadSignalData()
#ss = selectDateFromSignal(signalData,'2016-01-01','2016-01-31')
#print(ss)
t1 = pd.Timestamp('2016-01-01')
t2 = pd.Timestamp('2016-01-31')
df2 = signalData.loc[t1:t2,:]
#print(df2)
#取得索引,去重
#l2 = getIndexAndDistinct(df2)
#ss = df2.index.levels[0] # 已经去重,且保持原来的顺序
"""

"""
signalData = loadSignalData()
entity = signalData.ix[('2001-07-27',1880)]
print(entity)
"""

"""
import pandas as pd
import numpy as np
a = pd.DataFrame(data=np.random.randn([2,3]))
"""