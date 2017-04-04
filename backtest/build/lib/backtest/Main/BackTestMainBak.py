from backtestData.Dao import SourceDataDao
from backtest.Util import SelectUtil
from backtest.Util import DateUtil
from backtest.Util import SetUtil
from backtest.Util import NumUtil
from backtest.Entity import StockHoldEntity
from backtest.Entity import StockTradeEntityBak


from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from datetime import datetime
import math

#处理买入交易
def handleBuyList(tradingDate,buyList,dailyQuote,usableVol,stockHoldDF,stockTradeDF):
    vol = usableVol/len(buyList)
    #print('vol:'+vol)
    partChangePCT = 0
    for innerCode in buyList:
        dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        #print('innerCode:'+str(innerCode))
        #print(dailyQuoteRow)
        turnoverValue = dailyQuoteRow["TurnoverValue"]
        turnoverVolume = dailyQuoteRow["TurnoverVolume"]
        closePrice = dailyQuoteRow["ClosePrice"]
        cost = turnoverValue/turnoverVolume
        changePCT = NumUtil.get_change_pct(cost, closePrice, 2)
        realChangePCT = changePCT * vol / 100.0
        partChangePCT = partChangePCT + realChangePCT
        hold = StockHoldEntity.StockHoldEntity(tradingDate,innerCode,vol)
        trade = StockTradeEntityBak.StockTradeEntity(tradingDate, innerCode, 1, vol, cost, changePCT, realChangePCT)
        stockHoldDF.setdefault(innerCode,hold)
        #TODO trade

    return partChangePCT

#处理卖出交易
def handleSellList(tradingDate,sellList,dailyQuote,usableVol,stockHoldDF,stockTradeDF):
    partChangePCT = 0
    dateStr = DateUtil.datetime2_str(tradingDate)
    for innerCode in sellList:
        dailyQuoteSingle = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        #print('innerCode:' + str(innerCode))
        hold = stockHoldDF.pop(innerCode)
        vol = hold.vol
        # print(dailyQuoteSingle)
        turnoverValue = dailyQuoteSingle["TurnoverValue"]
        turnoverVolume = dailyQuoteSingle["TurnoverVolume"]
        prevClosePrice = dailyQuoteSingle["PrevClosePrice"]
        sellPrice = turnoverValue / turnoverVolume
        changePCT = NumUtil.get_change_pct(prevClosePrice, sellPrice, 2)
        realChangePCT = changePCT * vol / 100.0
        partChangePCT = partChangePCT + realChangePCT;

        if dateStr == '2001-01-17':
            print("vol:"+str(vol)+" turnoverValue:"+str(turnoverValue)+" turnoverVolume:"+str(turnoverVolume)+
                  " prevClosePrice:"+str(prevClosePrice)+" sellPrice:"+str(sellPrice)+" changePCT:"+str(changePCT)+
                  " realChangePCT:"+str(realChangePCT)+" partChangePCT:"+str(partChangePCT))

    return partChangePCT

#卖出后释放仓位
def getReleasedVol(sellList,stockHoldDF):
    releasedVol = 0
    for innerCode in sellList:
        hold = stockHoldDF.get(innerCode)
        vol = hold.vol
        releasedVol = releasedVol + vol
    return releasedVol

#今日选股和昨日选股的差集
def getDifference(currSourceData, lastSourceData):
    currList = []
    lastList = []

    if len(currSourceData) != 0:
        for index, row in currSourceData.iterrows():
            currList.append(index[1])

    if len(lastSourceData) != 0:
        for index, row in lastSourceData.iterrows():
            lastList.append(index[1])

    returnList = SetUtil.difference(currList, lastList)
    return returnList

#今日选股和昨日选股的交集
def getIntersection(currSourceData, lastSourceData):
    currList = []
    lastList = []
    for index, row in currSourceData.iterrows():
        currList.append(index[1])
    for index, row in lastSourceData.iterrows():
        lastList.append(index[1])

    returnList = SetUtil.intersection(currList, lastList)
    return returnList

#买入列表
def getBuyList(currSourceData, lastSourceData):
    return getDifference(currSourceData,lastSourceData)

#卖出列表
def getSellList(currSourceData, lastSourceData):
    return getDifference(lastSourceData,currSourceData)

#昨日持有列表
def getHoldList(currSourceData, lastSourceData):
    return getIntersection(currSourceData,lastSourceData)

#主程序
def main():
    signalData = SourceDataDao.getSignalData()
    dailyQuote = SourceDataDao.getDailyQuote()

    #columns filter
    #df3 = sourceData.loc[(df['Mom'] <= 4) & (df['Mom'] <= 4), ['Mom']]

    #index filter
    #startDate=DateUtils.str2Datetime('20010105');
    #endDate=DateUtils.str2Datetime('20010111');
    #df4 = df3.ix[startDate:endDate]

    #select top 5 group by TradingDay order by Mom desc
    groupedSignalData = signalData.groupby(level='TradingDay').apply(SelectUtil.top,5,'Mom',False)

    #param
    period = 5
    startDate = '1/8/2001'
    #endDate = '1/1/2017'
    endDate = '1/18/2001'

    #time series
    dateList = DateUtil.get_date_list2(startDate, endDate)

    currHoldSet = {}
    stockHoldDF = {}
    stockTradeDF = {}
    #lastSignalData = pd.DataFrame()
    usableVol = 100;
    netValue = 1;
    stockStatDaily = pd.DataFrame(index=pd.date_range(startDate, endDate), columns=['netValue','changePCT','buyCnt','sellCnt','holdCnt'])
    for date in dateList.index:
        #print(date)
        dateStr = DateUtil.datetime2_str(date)
        #print(dateStr)
        #isinstance(date, datetime)
        #DateUtil.str2Datetime('20010108')

        # select by single date
        try:
            #print(1)
            currSignalData = groupedSignalData.ix[date]
            print("currSignalData:"+str(len(currSignalData)))
            #print(2)
            buyList = getBuyList(currSignalData,lastSignalData)
            #print(3)
            sellList = getSellList(currSignalData,lastSignalData)
            #print(4)
            holdList = getHoldList(currSignalData,lastSignalData)
            #print(currSignalData)
            #print("len:"+str(len(currSignalData)))
        except:
            #假期,双休日,原数据问题
            print(DateUtil.datetime2_str(date) + ': no data')
            continue

        buyCnt = len(buyList)
        sellCnt = len(sellList)
        holdCnt = len(holdList)

        dailyChangePCT = 0
        changePCTBuy = handleBuyList(date,buyList,dailyQuote,usableVol,stockHoldDF,stockTradeDF)
        releasedVol = getReleasedVol(sellList, stockHoldDF)
        usableVol = usableVol + releasedVol
        changePCTSell = handleSellList(date,sellList,dailyQuote,usableVol,stockHoldDF,stockTradeDF)
        #changePCTHold = handleHoldList(date, sellList, dailyQuote, usableVol, stockHoldDF, stockTradeDF)
        changePCTHold = 0

        print("dateStr:" + dateStr +
              " changePCTBuy:" + str(changePCTBuy) +
              " changePCTSell:" + str(changePCTSell) +
              " changePCTHold:" + str(changePCTHold))

        dailyChangePCT = changePCTBuy+changePCTSell+changePCTHold
        #print("dailyChangePCT:"+str(dailyChangePCT))
        netValue = netValue * (1 + dailyChangePCT / 100)
        #print("netValue:" + str(netValue))
        stockStatDaily.ix[dateStr] = netValue,dailyChangePCT,buyCnt,sellCnt,holdCnt

        #innerCodeList = currSignalData["InnerCode"]
        #print(innerCodeList)

        #lastSignalData = currSignalData

    print(stockStatDaily)

main()



