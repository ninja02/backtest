from backtestData.Dao import SourceDataDao
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


#########################################################
def printByInnerCodeAndDate(addr):
    dailyQuote = SourceDataDao.load_daily_quote(addr)
    dailyQuote = SourceDataDao.select_by_inner_code_and_date(dailyQuote, '2004-01-17', '000049.SZ')
    print(dailyQuote)

def printByInnerCode(innerCode,addr):
    dailyQuote = SourceDataDao.load_new_daily_quote(addr)
    # dailyQuote = selectByDate(dailyQuote,'2004-01-05','2004-01-06')
    # dailyQuote = selectByInnerCodeAndDate(dailyQuote,'2004-01-05','000049.SZ')
    #'000049.SZ'
    dailyQuote = SourceDataDao.select_by_inner_code(dailyQuote, innerCode)
    dailyQuote.to_csv(StockConst.ROOT + '\export\dailyQuoteDebug.csv')
    print(dailyQuote)

#分组信号
def printGroupedSingalData(addr):
    signalData = SourceDataDao.load_signal_data(addr)
    groupedSignalData = signalData.groupby(level=StockConst.TRADINGDAY).apply(SelectUtil.top, 5, StockConst.MOM, False)
    groupedSignalData.to_csv(StockConst.ROOT + '\export\groupedSignalData.csv')

def printSingalDataByDate(date,addr):
    signalData = SourceDataDao.load_signal_data(addr)
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
        dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        #dailyQuoteToDebug.append(dailyQuoteRow)
        print(dailyQuoteRow)
    #dailyQuoteToDebug.to_csv(StockConst.root + '\export\dailyQuoteToDebug.csv')

# test
@TimeUtil.check_consumed_time2
def exportSignal():
    signalData = SourceDataDao.load_signal_data(StockConst.ROOT + '/Mom_5_0302.h5')
    # signalData.to_csv(StockConst.root + '\export2\signalData.csv')
    # signalData.to_excel(StockConst.root + '\export2\signalData.xls', sheet_name='Sheet1')
    signalData.to_json(StockConst.ROOT + '\export2\signalData.json')
    signalData.to_hdf(StockConst.ROOT + '\export2\signalData.h5')

# # test
# @TimeUtil.checkConsumedTime2
# def exportSignal():
#     signalData = loadSignalData(StockConst.root + '/Mom_5_0302.h5')
#     signalData.to_excel(StockConst.root + '\export2\signalData.csv')


def test10(addr):
    signalData = SourceDataDao.load_signal_data(addr)
    groupedSignalData = signalData.groupby(level=StockConst.TRADINGDAY, as_index=False).apply(SelectUtil.top, 5, StockConst.MOM, False)
    print(groupedSignalData)


# dailyQuote = SourceDataDao.loadDailyQuote(StockConst.root+'/New_Daily_Bars2.h5')
# dailyQuote = SourceDataDao.selectByInnerCode(dailyQuote,'000001.SZ')
# print(dailyQuote)

def getMaxDate(df):
    l2 = list(df.index.get_level_values(0))
    record = l2[-1]


if __name__ == '__main__':

    # colums = SourceDataDao.get_columns(StockConst.ROOT + '/0_Data/DataCsv.csv') #DataXlsx.xlsx DataCsv.csv
    # print(colums)

    # colums = SourceDataDao.get_colums_from_h5(StockConst.ROOT + '/0_Data/Mom_basedon_HS300.h5')
    # print(colums)

    data = SourceDataDao.get_colums_include_index_from_h5(StockConst.ROOT + '/0_Data/Mom_basedon_HS300.h5')
    print(data)


    # signalData = SourceDataDao.read_file_set_index(StockConst.ROOT + '/0_Data/Mom_basedon_HS300.h5')
    # # signalData = signalData.reset_index(drop=True)
    # # print(signalData)
    #
    # signalData = pd.DataFrame(signalData, columns=['TradingDay1', 'InnerCode2', 'Mom'])
    # print(signalData)

    # signalData = SourceDataDao.read_file(StockConst.root + '/0_Data/test.csv')
    # print(signalData)

    # signalData = SourceDataDao.read_file_setindex(StockConst.root + '/signalDataXlsx.xlsx') #signalDataXlsx.xlsx signalDataCsv.csv
    # date = SourceDataDao.getMaxDate(StockConst.root + StockConst.signalDataH5)
    # print(date)
    #
    # date = SourceDataDao.getMinDate(StockConst.root + StockConst.signalDataH5)
    # print(date)

    # indexQuote = SourceDataDao.read_file_setindex(indexQuoteAddr)

    #
    # print(signalData)

    # signalData = pd.read_excel(StockConst.root + '/Data.xls')
    # # dateList = list(signalData[StockConst.TradingDay])
    # #
    # # r=DateUtil.datetime2StrFormat(dateList[-1], '%Y-%m-%d')
    # #
    # print(signalData['TradingDay'][0])

    # df=SourceDataDao.read_file_setindex(StockConst.root + '/DataCsv.csv')
    # print(df)

    # l2 = list(signalData['TradingDay'])
    #
    # # print(l2[0])
    # print(DateUtil.datetime2Str(DateUtil.str2DatetimeFormat(l2[-1],'%Y/%m/%d')))
    # pass

    # lastRecord = SourceDataDao.getLastRecordFromH5(StockConst.root + StockConst.signalDataH5)
    # print(DateUtil.datetime2Str(lastRecord.index[0][0]))

    pass



