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


# 数据源1
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


# 数据源2
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


# sellFlg: -1不能卖出
# buyFlg: -1不能买入
def addBuySellFlg(dailyQuoteParam):
    dailyQuote = dailyQuoteParam.copy()
    if StockConst.DATA_SOURCE_NO == 1:
        addBuySellFlg1(dailyQuote)
    elif StockConst.DATA_SOURCE_NO == 2:
        addBuySellFlg2(dailyQuote)
    elif StockConst.DATA_SOURCE_NO == 3:
        addBuySellFlg1(dailyQuote)
    return dailyQuote


# 只执行1次
# 加BuySellFlg到DailyQuote
# 分批导出到h5文件
def addBuySellFlgAndExport(addr):
    dailyQuote = SourceDataDao.load_daily_quote(addr)
    startDate = dailyQuote.index[0][0]
    endDate = dailyQuote.index[-1][0]
    startYear = DateUtil.datetime2_year_str(startDate)
    endYear = DateUtil.datetime2_year_str(endDate)
    FORMAT = "%d-%d-%d"
    # c = time.strftime('%Y%m%d', time.strptime(y, '%Y-%m-%d'))
    for year in range(int(startYear), int(endYear) + 1, 1):
        for month in range(1 ,13):
            d = calendar.monthrange(year, month)
            exportStartDate = FORMAT % (year, month, 1)
            exportEndDate = FORMAT % (year, month, d[1])
            # exportStartDate = str(year)+'-'+addZero(month)+'-'+'01'
            # exportEndDate = str(year) + '-' + addZero(month) + '-' + getMonthEndDay(month)
            subDailyQuote = SourceDataDao.select_by_date(dailyQuote, exportStartDate, exportEndDate)
            print('exportStartDate:' + exportStartDate)
            print('exportEndDate:' + exportEndDate)
            print( 'dailyQuote:' +str(len(subDailyQuote)))
            if(len(subDailyQuote) > 0):
                newSubDailyQuote = addBuySellFlg(subDailyQuote)
                SourceDataDao.export_to_hdfstore(newSubDailyQuote, StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5)


# 如果是退市股，返回最后一条记录
def getDelist(df, lastTradingDay):
    df = df.sort_index(level=0, ascending=False)
    lastRecordDf = df.iloc[0:1]
    # print(lastRecordDf)
    tradingDay = lastRecordDf.index[0][0]
    # print(tradingDay)
    # print(lastTradingDay)
    if tradingDay != lastTradingDay:
        # print(tradingDay)
        return lastRecordDf


# 只执行1次
# 加delist到DailyQuote，退市强制卖出标记，delist=1表示退市前最后交易日
# 分批导出到h5文件
def addDelistFlgAndExport(sourceAddr,targetAddr):
    dailyQuote = SourceDataDao.load_daily_quote(sourceAddr)

    # print(dailyQuote)

    lastTradingDay = max(list(dailyQuote.index.get_level_values(0).unique()))
    # lastTradingDayTsp = pd.Timestamp(DateUtil.datetime2Str(lastTradingDay))
    # print('lastTradingDay:'+lastTradingDayTsp)

    # 全部退市股
    delistDf = dailyQuote.groupby(level=StockConst.INNERCODE).apply(getDelist, lastTradingDay)  # False True
    # print(delistDf)

    # 退市标记
    dailyQuote.insert(len(dailyQuote.columns),'delistFlg', None) # 退市股delistFlg=1
    for index, row in delistDf.iterrows():
        tradingDay = index[1]
        innerCode = index[2]
        dailyQuote.ix[(tradingDay,innerCode), 'delistFlg'] = '1'
        # print(dailyQuote.ix[(tradingDay,innerCode)])

    # 导出到h5
    SourceDataDao.export_to_hdfstore(dailyQuote, StockConst.ROOT + '/' + targetAddr + '.h5') # dailyQuote.to_csv(StockConst.root + '\export\'+targetAddr+'.csv')

    # check
    # dailyQuote = dailyQuote[dailyQuote['delistFlg']=='1']
    # print(dailyQuote)

    # check
    # dailyQuote = selectByInnerCode(dailyQuote, '600788.SH')
    # print(dailyQuote)


# 只执行1次
# 过滤信号数据，只保留指数成分股的信号，导出到h5
def mergeSignalWithHS300():
    signalDataDf = SourceDataDao.load_signal_data('')
    indexDf = SourceDataDao.load_h5(StockConst.ROOT + StockConst.HS300H5)
    # signalDataDf = selectSignalByDate(signalDataDf,'2005-01-01','2005-04-08')
    # hs300Df = hs300Df.loc[(hs300Df['NatureDay'] == '2005-04-08')]
    mergeSignalWithIndexMain(signalDataDf, indexDf, StockConst.SIGNAL_DATA_BASEDON_HS300)

def mergeSignalWithZZ500():
    signalDataDf = SourceDataDao.load_signal_data('')
    indexDf = SourceDataDao.load_h5(StockConst.ROOT + StockConst.ZZ500H5)
    # signalDataDf = selectSignalByDate(signalDataDf,'2005-01-01','2005-04-08')
    # hs300Df = hs300Df.loc[(hs300Df['NatureDay'] == '2007-01-15')]
    mergeSignalWithIndexMain(signalDataDf, indexDf, StockConst.SIGNAL_DATA_BASEDON_ZZ500)

def mergeSignalWithZZ800():
    signalDataDf = SourceDataDao.load_signal_data('')
    indexDf = SourceDataDao.load_h5(StockConst.ROOT + StockConst.ZZ800H5)
    # signalDataDf = selectSignalByDate(signalDataDf,'2005-01-01','2005-04-08')
    # hs300Df = hs300Df.loc[(hs300Df['NatureDay'] == '2005-04-08')]
    mergeSignalWithIndexMain(signalDataDf, indexDf, StockConst.SIGNAL_DATA_BASEDON_ZZ800)


# def convertDate(row):
#     row['NatureDay'] = pd.Timestamp(row['NatureDay'])
#     # print(type(row['NatureDay']))
#     return row


# 只执行1次
def mergeSignalWithIndexMain(signalDataDf, indexDf, addr):
    # print(signalDataDf)
    # print(indexDf)
    # newIndexDf = indexDf.apply(convertDate, axis=1)
    # # indexDf['NatureDay'] = DateUtil.str2Datetime(indexDf['NatureDay'])
    # print(newIndexDf)

    # 取交集
    df = pd.merge(indexDf, signalDataDf, left_on=['NatureDay','WindCode'], right_index=True)  # NatureDay,WindCode
    # 取3列
    df = df[['NatureDay','WindCode','Mom']]
    # 重命名
    df. rename(columns={'NatureDay': 'TradingDay'}, inplace=True)
    # 设置索引
    df = df.set_index(['TradingDay','WindCode'])
    # 导出h5
    SourceDataDao.export_to_hdfstore(df, StockConst.ROOT + addr)

    # df.to_csv(StockConst.root + '\export\mergeSignalWithIndexMain.csv')

    # print(df)



if __name__ == '__main__':
    # mergeSignalWithHS300()
    # mergeSignalWithZZ500()
    # mergeSignalWithZZ800()

    # indexDf = SourceDataDao.loadH5(StockConst.root + StockConst.ZZ500H5)
    # print(indexDf)
    pass