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

#假数据1
def createSignalDataHill():
    # dateList = ['2010-01-01','2010-01-02','2010-01-03','2010-01-04']
    dateList1 = pd.date_range('2004-01-01','2004-06-30')
    dateList2 = pd.date_range('2004-07-01', '2004-12-31')

    df1 = createSignalDataHillMain(dateList1, True)
    df2 = createSignalDataHillMain(dateList2, False)
    df = df1.append(df2)
    # print(df)
    SourceDataDao.export_to_hdfstore(df, StockConst.ROOT + '/export/SignalDataHill.h5')
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



# 用于界面
# 只执行1次(假数据)
# 加2列到signalData: Mom2, Mom3
# 分批导出到h5文件
def createFakeSignalData(addr):
    signalData = SourceDataDao.load_signal_data(addr)
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
            subSignalData = SourceDataDao.select_by_date(signalData, exportStartDate, exportEndDate)
            print('exportStartDate:' + exportStartDate)
            print('exportEndDate:' + exportEndDate)
            print('subSignalData:' + str(len(subSignalData)))
            if (len(subSignalData) > 0):
                newSubSignalData = subSignalData.copy()
                newSubSignalData['Mom2'] = subSignalData['Mom']
                newSubSignalData['Mom3'] = subSignalData['Mom']
                SourceDataDao.export_to_hdfstore(newSubSignalData, StockConst.ROOT + StockConst.FAKE_SIGNAL_DATA_H5)

#只执行1次(测试)
# 加BuyFlg 到 groupedSignalData
# 导出到csv文件
def addBuySellFlgToSignalData(signalDataAddr,dailyQuoteAddr):
    signalData = SourceDataDao.load_signal_data(signalDataAddr)
    dailyQuote = SourceDataDao.load_new_daily_quote(dailyQuoteAddr)
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

#只执行1次(测试)
# 加BuyFlg 到 groupedSignalData
# 导出到csv文件
def addBuySellFlgToSignalData2(signalDataAddr,dailyQuoteAddr):
    signalData = SourceDataDao.load_signal_data(signalDataAddr)
    dailyQuote = SourceDataDao.load_new_daily_quote(dailyQuoteAddr)
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


# 只执行1次
#创建指数行情数据（假数据），没有真实数据的情况下暂时使用
#指数每日涨幅百分之0.01
def createFakeIndexQuote():
    dateRange = pd.date_range(start='2005-01-01',end='2005-12-31')
    codeList = [StockConst.HS300_CODE, StockConst.ZZ500_CODE, StockConst.ZZ800_CODE]
    multi_index = pd.MultiIndex.from_product([dateRange,codeList], names = ['TradingDay','WindCode'])
    indexDF = pd.DataFrame(index= multi_index, columns=['ChangePCT'])
    indexDF['ChangePCT'] = 0.01 #百分之
    # print(indexDF)
    SourceDataDao.export_to_hdfstore(indexDF, StockConst.ROOT + StockConst.FAKE_INDEX_QUOTE_H5)
    indexDF.to_csv(StockConst.ROOT + '\\export\\fakeIndexQuoteH5.csv')

# 只执行1次
#创建指数行情数据（假数据），没有真实数据的情况下暂时使用
#指数每日涨幅百分之1
def createFakeIndexQuote2():
    dateRange = pd.date_range(start='2005-01-01',end='2005-12-31')
    codeList = [StockConst.HS300_CODE, StockConst.ZZ500_CODE, StockConst.ZZ800_CODE]
    multi_index = pd.MultiIndex.from_product([dateRange,codeList], names = ['TradingDay','WindCode'])
    indexDF = pd.DataFrame(index= multi_index, columns=['ChangePCT'])
    indexDF['ChangePCT'] = 1 #百分之
    # print(indexDF)
    SourceDataDao.export_to_hdfstore(indexDF, StockConst.ROOT + StockConst.FAKE_INDEX_QUOTE_H5_2)
    indexDF.to_csv(StockConst.ROOT + '\\export\\fakeIndexQuoteH5_2.csv')


if __name__ == '__main__':
    # createFakeIndexQuote()
    createFakeIndexQuote2()
    # df = SourceDataDao.loadH5(StockConst.root + StockConst.fakeIndexQuoteH5)
    # print(df)

    pass


