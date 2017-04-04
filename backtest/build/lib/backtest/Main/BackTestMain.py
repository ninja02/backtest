from backtestData.Dao import SourceDataDao
from backtest.Util import SelectUtil
from backtest.Util import DateUtil
from backtest.Util import SetUtil
from backtest.Util import NumUtil
from backtest.Entity import StockHoldEntity
from backtest.Entity import StockTradeEntityBak
from backtest.Constance import StockConst
from backtest.Service import StockMaxDropService
from backtest.Service import StockMaxDropNewService
from backtest.Service import SharpRatioService
from backtest.Service import SharpRatioNewService
from backtest.Service import StockYearService
from backtest.Service import BackTestHelper

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from datetime import datetime
import math



#处理买入交易
def handleBuyList(tradingDate,buyList,dailyQuote,usableVol,stockHoldDF,stockTradeDF,currHoldSet,actualBuyList,cannotBuyList):
    if usableVol == 0:
        return 0

    if len(buyList) == 0:
        return 0

    vol = usableVol/len(buyList)
    #print('vol:'+vol)
    partChangePCT = 0
    for innerCode in buyList:
        dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        #print('innerCode:'+str(innerCode))
        #print(dailyQuoteRow)
        turnoverValue = dailyQuoteRow["TurnoverValue"]
        turnoverVolume = dailyQuoteRow["TurnoverVolume"]
        prevClosePrice = dailyQuoteRow["PrevClosePrice"]
        closePrice = dailyQuoteRow["ClosePrice"]
        highPrice = dailyQuoteRow["HighPrice"]
        lowPrice = dailyQuoteRow["LowPrice"]
        # 非停牌 且 非一字涨停: 可以卖出
        check = not BackTestHelper.isYiZiZhangTing(highPrice,lowPrice,prevClosePrice)
        if (closePrice != 0) & (turnoverValue != float(0)) & check:
            actualBuyList.append(innerCode)
            cost = turnoverValue/turnoverVolume
            changePCT = NumUtil.get_change_pct(cost, closePrice, 2)
            realChangePCT = (changePCT - StockConst.BUY_COMMISSION) * vol / 100.0
            partChangePCT = partChangePCT + realChangePCT
            #
            stockHold = StockHoldEntity.StockHoldEntity(tradingDate,innerCode,vol)
            stockTrade = StockTradeEntityBak.StockTradeEntity(tradingDate, innerCode, 1, vol, cost, changePCT, realChangePCT)
            #插入表
            #stockHoldDF.setdefault(innerCode,stockHold)
            #当前持仓
            currHoldSet.setdefault(innerCode,vol)

            #TODO trade
        else:
            cannotBuyList.append(innerCode)

    return partChangePCT

#处理卖出交易
#1.currHoldSet释放仓位
#2.partChangePCT计算卖出部分的盈利
def handleSellList(tradingDate,sellList,dailyQuote,usableVol,stockHoldDF,stockTradeDF,currHoldSet,actualSellList,cannotSellList):
    partChangePCT = 0
    dateStr = DateUtil.datetime2_str(tradingDate)

    if len(sellList) == 0:
        return 0

    for innerCode in sellList:
        dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        #print('innerCode:' + str(innerCode))
        # print(dailyQuoteSingle)
        turnoverValue = dailyQuoteRow["TurnoverValue"]
        turnoverVolume = dailyQuoteRow["TurnoverVolume"]
        prevClosePrice = dailyQuoteRow["PrevClosePrice"]
        closePrice = dailyQuoteRow["ClosePrice"]
        highPrice = dailyQuoteRow["HighPrice"]
        lowPrice = dailyQuoteRow["LowPrice"]
        #非停牌 且 非一字跌停: 可以卖出
        check = not BackTestHelper.isYiZiDieTing(highPrice,lowPrice,prevClosePrice)
        if (closePrice != 0) & (turnoverValue != float(0)) & check:
            actualSellList.append(innerCode)
            vol = currHoldSet.pop(innerCode)
            sellPrice = turnoverValue / turnoverVolume
            changePCT = NumUtil.get_change_pct(prevClosePrice, sellPrice, 2)
            realChangePCT = (changePCT - StockConst.SELL_COMMISSION) * vol / 100.0
            partChangePCT = partChangePCT + realChangePCT
            """
            if dateStr == '2001-01-17':
                print("vol:"+str(vol)+" turnoverValue:"+str(turnoverValue)+" turnoverVolume:"+str(turnoverVolume)+
                      " prevClosePrice:"+str(prevClosePrice)+" closePrice:"+str(closePrice)+" sellPrice:"+str(sellPrice)+
                      " changePCT:"+str(changePCT)+
                      " realChangePCT:"+str(realChangePCT)+" partChangePCT:"+str(partChangePCT))
            """
        else:
            cannotSellList.append(innerCode)
    return partChangePCT

def handleHoldList(tradingDate,holdList,dailyQuote,usableVol,stockHoldDF,stockTradeDF,currHoldSet):
    partChangePCT = 0
    #dateStr = DateUtil.datetime2Str(tradingDate)
    if len(holdList) == 0:
        return 0

    for innerCode in holdList:
        dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        #print('innerCode:' + str(innerCode))
        # print(dailyQuoteSingle)
        turnoverValue = dailyQuoteRow["TurnoverValue"]
        #turnoverVolume = dailyQuoteRow["TurnoverVolume"]
        prevClosePrice = dailyQuoteRow["PrevClosePrice"]
        closePrice = dailyQuoteRow["ClosePrice"]
        #非停牌
        if (closePrice != 0) & (turnoverValue != float(0)):
            vol = currHoldSet.get(innerCode)
            changePCT = NumUtil.get_change_pct(prevClosePrice, closePrice, 2)
            realChangePCT = changePCT * vol / 100.0
            partChangePCT = partChangePCT + realChangePCT

    return partChangePCT

#今日选股和昨日选股的差集
#currSourceData: dataFrame
#currHoldSet: dict
#return: innerCode list
#currList - lastList
def getDifference(currSourceData, currHoldSet, typ):
    currList = []
    lastList = []

    if len(currSourceData) != 0:
        for index, row in currSourceData.iterrows():
            currList.append(index[1])

    if len(currHoldSet) != 0:
        for innerCode in currHoldSet:
            lastList.append(innerCode)

    #currList - lastList
    if typ == 1:
        returnList = SetUtil.difference(currList, lastList)
    #lastList - currList
    else:
        returnList = SetUtil.difference(lastList, currList)
    return returnList


#今日选股和昨日选股的交集
#currSourceData: dataFrame
#currHoldSet: dict
#return: innerCode list
#currList 交集 lastList
def getIntersection(currSourceData, currHoldSet):
    currList = []
    lastList = []
    for index, row in currSourceData.iterrows():
        currList.append(index[1])

    for innerCode in currHoldSet:
        lastList.append(innerCode)

    returnList = SetUtil.intersection(currList, lastList)
    return returnList

#买入列表
def getBuyList(currSourceData, currHoldSet):
    return getDifference(currSourceData,currHoldSet,1)

#卖出列表
def getSellList(currSourceData, currHoldSet):
    return getDifference(currSourceData,currHoldSet,-1)

#昨日持有列表
def getPrevHoldList(currSourceData, currHoldSet):
    return getIntersection(currSourceData,currHoldSet)

#遍历持仓表
def calculateUsableVol(currHoldSet):
    currVol = 0;
    for innerCode in currHoldSet:
        vol = currHoldSet[innerCode]
        currVol = currVol + vol
    return 100 - currVol

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
    #period = 5
    #startDate = '1/8/2001'
    startDate = '1/8/2001'
    #endDate = '1/1/2017'
    endDate = '2/18/2002'
    #endDate = '12/31/2016'
    #endDate = '12/31/2002'

    #time series
    #dateList = DateUtil.getDateList2(startDate,endDate)

    currHoldSet = {}
    stockHoldDF = {}
    stockTradeDF = {}
    #lastSignalData = pd.DataFrame()
    usableVol = 100;
    netValue = 1;
    #初始化每日统计表
    stockStatDaily = pd.DataFrame(index=pd.date_range(startDate, endDate),
                columns=['netValue','changePCT','buyCnt','sellCnt','prevHoldCnt','currHoldCnt','cannotSellCnt','cannotBuyCnt'])
    #从信号表中取得唯一性日期
    dateList = SourceDataDao.select_date_from_signal(signalData, startDate, endDate)
    for date in dateList:
    #for date in dateList.index:
        #print(date)
        dateStr = DateUtil.datetime2_str(date)
        #print(dateStr)
        #isinstance(date, datetime)

        # select by single date
        #try:

        #print(1)
        currSignalData = groupedSignalData.ix[date]
        if StockConst.IS_DEBUG:
            print("currSignalData:"+str(len(currSignalData)))
        #print(2)
        buyList = getBuyList(currSignalData,currHoldSet)
        #print(3)
        sellList = getSellList(currSignalData,currHoldSet)
        #print(4)
        prevHoldList = getPrevHoldList(currSignalData,currHoldSet)
        #print(currSignalData)

        #except:
            #假期,双休日,原数据问题
            #if StockConst.isDebug:
                #print(DateUtil.datetime2Str(date) + ': no data')
            #continue

        dailyChangePCT = 0
        actualSellList=[]
        actualBuyList=[]
        cannotSellList=[]
        cannotBuyList = []
        #1.sell
        changePCTSell = handleSellList(date,sellList,dailyQuote,usableVol,stockHoldDF,stockTradeDF,currHoldSet,actualSellList,cannotSellList)
        usableVol = calculateUsableVol(currHoldSet)
        #2.buy
        changePCTBuy = handleBuyList(date,buyList,dailyQuote,usableVol,stockHoldDF,stockTradeDF,currHoldSet,actualBuyList,cannotBuyList)
        #3.hold
        changePCTHold = handleHoldList(date,prevHoldList,dailyQuote,usableVol,stockHoldDF,stockTradeDF,currHoldSet)
        #changePCTHold = 0

        buyCnt = len(actualBuyList)
        sellCnt = len(actualSellList)
        prevHoldCnt = len(prevHoldList)
        currHoldCnt = len(currHoldSet)
        cannotSellCnt = len(cannotSellList)
        cannotBuyCnt = len(cannotBuyList)

        if StockConst.IS_DEBUG:
            print("dateStr:" + dateStr +
                  " changePCTBuy:" + str(changePCTBuy) +
                  " changePCTSell:" + str(changePCTSell) +
                  " changePCTHold:" + str(changePCTHold))

        dailyChangePCT = changePCTBuy+changePCTSell+changePCTHold
        #print("dailyChangePCT:"+str(dailyChangePCT))
        netValue = netValue * (1 + dailyChangePCT / 100)
        #print("netValue:" + str(netValue))
        stockStatDaily.ix[dateStr] = netValue,dailyChangePCT,buyCnt,sellCnt,prevHoldCnt,currHoldCnt,cannotSellCnt,cannotBuyCnt

        #innerCodeList = currSignalData["InnerCode"]
        #print(innerCodeList)

        #lastSignalData = currSignalData

    #每日统计(收益，净值，买入数，卖出数，持有数)
    stockStatDaily = stockStatDaily.dropna(how='all')
    print('每日统计:')
    print(stockStatDaily)
    stockStatDaily.to_csv('F:\export\stockStatDaily.csv')

    # 每年统计
    yearList = StockYearService.main(stockStatDaily)
    print('每年统计:')
    print(yearList)

    # 最大回撤
    maxdrop = StockMaxDropNewService.get_max_drop(stockStatDaily)
    print('最大回撤:')
    print(maxdrop)
    #每年的最大回撤
    maxdropList = StockMaxDropNewService.get_max_drop_for_each_year(stockStatDaily)
    maxdropList.sort_values(by=["year"])
    print('每年的最大回撤:')
    print(maxdropList)

    #夏普比率
    sharpRatio = SharpRatioNewService.get_sharp_ratio(stockStatDaily)
    print('夏普比率:')
    print(sharpRatio)
    #每年的夏普比率
    sharpRatioList = SharpRatioNewService.get_sharp_ratio_for_each_year(stockStatDaily)
    sharpRatioList.sort_values(by=["year"])
    print('每年的夏普比率:')
    print(sharpRatioList)

main()




