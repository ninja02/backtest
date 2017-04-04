from backtestData.Dao import SourceDataDao
from backtest.Util import SelectUtil
from backtest.Util import DateUtil
from backtest.Util import SetUtil
from backtest.Util import NumUtil
from backtest.Entity import StockHoldEntity
from backtest.Entity import StockTradeEntityBak
from backtest.Entity import CapitalEntity
from backtest.Constance import StockConst
from backtest.Service import StockMaxDropService
from backtest.Service import StockMaxDropNewService
from backtest.Service import SharpRatioService
from backtest.Service import SharpRatioNewService
from backtest.Service import StockYearService
from backtest.Service import BackTestHelper
from backtest.Util import TimeUtil

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from datetime import datetime
import math

#实际买入个数
def getNumOfActualBuy(tradingDate,buyList,dailyQuote):
    if len(buyList) == 0:
        return 0

    numOfActualBuy = 0
    for innerCode in buyList:
        dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        buyFlg = dailyQuoteRow[StockConst.BUY_FLG]
        # 可买
        if buyFlg != -1:
            numOfActualBuy += 1

    return numOfActualBuy


#买入列表中实际买入的股票(排除了停牌和一字涨停)
def getToBuyInBuyList(buyList,dailyQuote,tradingDate,cannotBuyList):
    toBuyInBuyList = []
    for innerCode in buyList:
        dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        buyFlg = dailyQuoteRow[StockConst.BUY_FLG]
        #可买
        if buyFlg != -1:
            toBuyInBuyList.append(innerCode)
        else:
            cannotBuyList.append(innerCode)

    return toBuyInBuyList

#卖出列表中实际卖出的股票（去停牌，去一字跌停，去保留股）
#排序：Mom降序
#分成2部分
#toKeepInSellList: 需要保留的股票(包括停牌和一字跌停和为了满足当日持仓个数保留的股票)
#toSellInSellList: 要卖出的股票(剩下的)
#cannotSellList: 停牌和一字跌停不能卖出
#返回:toSellInSellList
def getToSellInSellList(sellList,tradingDate,signalData,dailyQuote,numOfToKeepInSellList,cannotSellList,currHoldSet):
    if len(sellList) == 0:
        return sellList
    #创建2列DF，innerCode，Mom（空）
    dic = {StockConst.INNERCODE: sellList}
    sortedSellDf = pd.DataFrame(data=dic)
    sortedSellDf.insert(1, StockConst.MOM, Series())
    #print(sortedSellList)
    #从信号数据中获取Mom
    for innerCode in sellList:
        entity = signalData.ix[(tradingDate, innerCode)]
        sortedSellDf.loc[(sortedSellDf[StockConst.INNERCODE] == innerCode), [StockConst.MOM]] = entity[StockConst.MOM]
    #按Mom倒序排序
    sortedSellDf = sortedSellDf.sort_values(by=StockConst.MOM, ascending=False)

    #卖出列表中保留的股票
    toKeepInSellList = []
    #保留的股票: 停牌或一字跌停股
    #if len(toKeepInSellList) < numOfToKeepInSellList:
    for index,row in sortedSellDf.iterrows():
        innerCode = row[StockConst.INNERCODE]
        sellFlg = 0
        try:
            dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        except:
             #print('tradingDate:'+DateUtil.datetime2Str(tradingDate))
             #print(sortedSellDf)
             #print(sellList)
             #print(currHoldSet)
             #print(dailyQuoteRow)
             sellFlg = 0
        sellFlg = dailyQuoteRow[StockConst.SELL_FLG]
        #不能卖
        if sellFlg == -1:
            toKeepInSellList.append(innerCode)
            cannotSellList.append(innerCode)

    # 保留的股票:按sortedSellDf的顺序加入
    for index,row in sortedSellDf.iterrows():
        if len(toKeepInSellList) < numOfToKeepInSellList:
            innerCode = row[StockConst.INNERCODE]
            if(innerCode not in toKeepInSellList) :
                toKeepInSellList.append(innerCode)

    #去掉需要保留的股票
    toSellInSellList = sortedSellDf[~(sortedSellDf[StockConst.INNERCODE].isin(toKeepInSellList))][StockConst.INNERCODE].values
    #print('toSellInSellList')
    #print(toSellInSellList)

    return toSellInSellList

#处理买入交易
def handleBuyList(tradingDate,buyList,dailyQuote,usableVol,stockHoldDF,stockTradeList,currHoldSet,actualBuyList,cannotBuyList,capitalEntity):
    usableCach = capitalEntity.get_usable_cash()
    if usableCach == 0:
        return

    #if usableVol == 0:
        #return 0

    if len(buyList) == 0:
        return

    #可买列表
    buyList = getToBuyInBuyList(buyList,dailyQuote,tradingDate,cannotBuyList)
    if len(buyList) == 0:
        return

    turnover = usableCach/len(buyList)
    #print('vol:'+vol)
    partChangePCT = 0
    for innerCode in buyList:
        dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        #print('innerCode:'+str(innerCode))
        #print(dailyQuoteRow)
        turnoverValue = dailyQuoteRow[StockConst.TURNOVER_VALUE]
        turnoverVolume = dailyQuoteRow[StockConst.TURNOVER_VOLUME]
        #buyFlg = dailyQuoteRow[StockConst.buyFlg]
        #可买
        #if buyFlg != -1:
        #actualBuyList.append(innerCode)
        #平均买入价（没有算佣金）
        buyPrice = turnoverValue/turnoverVolume
        #成本价（算佣金）
        cost = buyPrice*(1 + StockConst.BUY_COMMISSION / 100)
        #仓位（股）
        #vol = NumUtil.getRound(turnover/cost,StockConst.volScale)
        #佣金（元）
        commission = BackTestHelper.get_buy_commission(turnover, StockConst.BUY_COMMISSION / 100)
        #买入市值
        buyMV = turnover - commission
        #更新可用金额(减少)
        capitalEntity.reduce_usable_cash(turnover)
        #changePCT = NumUtil.getChangePCT(cost, closePrice, 2)
        #realChangePCT = (changePCT - StockConst.buyCommission) * vol / 100.0
        #partChangePCT = partChangePCT + realChangePCT
        #
        #stockHold = StockHoldEntity.StockHoldEntity(tradingDate,innerCode,vol)
        #stockTrade = StockTradeEntity.StockTradeEntity(tradingDate, innerCode, 1, vol, cost, '', '')
        stockTradeDict = {'tradingDate':tradingDate,'innerCode':innerCode,'type':1,'vol':0,
                          'price':buyPrice,'turnover':turnover,'commission': commission,'MV':buyMV}
        stockTradeList.append(stockTradeDict)
        #插入表
        #stockHoldDF.setdefault(innerCode,stockHold)
        #当前持仓
        stockHoldEntity = StockHoldEntity.StockHoldEntity(innerCode, vol, buyPrice, cost, DateUtil.datetime2_str(tradingDate)) #tradingDate,
        currHoldSet.setdefault(innerCode,stockHoldEntity) #vol
        """
        if (DateUtil.datetime2Str(tradingDate) == '2014-12-08') | (DateUtil.datetime2Str(tradingDate) == '2014-12-09'):
            print('-----handleBuyList-----')
            print(DateUtil.datetime2Str(tradingDate))
            print(innerCode)
            print(vol)
            print(buyPrice)
            print(cost)
            print(turnoverValue)
            print(dailyQuoteRow)
            print('----------')
        """
        #else:
            #cannotBuyList.append(innerCode)

    #return partChangePCT




#处理卖出交易
#实际卖出数不能大于实际买入数
#1.currHoldSet释放仓位
#2.capitalEntity更新可用金额
#3.partChangePCT计算卖出部分的盈利
def handleSellList(tradingDate,sellList,dailyQuote,stockHoldDF,stockTradeList,currHoldSet,cannotSellList,
                   capitalEntity,numOfActualBuy,signalData,prevHoldList,numOfDailyHolding):
    partChangePCT = 0
    dateStr = DateUtil.datetime2_str(tradingDate)

    if len(sellList) == 0:
        return

    #卖出列表中要保留的股票数
    numOfToKeepInSellList = numOfDailyHolding - numOfActualBuy - len(prevHoldList)

    #卖出数 > 实际买入数：对卖出列表进行排序
    #if len(sellList) > numOfActualBuy:
    sellList = getToSellInSellList(sellList,tradingDate,signalData,dailyQuote,numOfToKeepInSellList,cannotSellList,currHoldSet)
    if len(sellList) == 0:
        return

    #numOfActualSell = 0
    for innerCode in sellList:
        #print('innerCode:' + str(innerCode))
        try:
            dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        except:
            #退市的股票: 查询不到行情,取最后一个交易日
            dailyQuoteRow = SourceDataDao.selectByLastDay(dailyQuote,innerCode)
        #print('innerCode:' + str(innerCode))
        # print(dailyQuoteSingle)
        #try:
        turnoverValue = dailyQuoteRow[StockConst.TURNOVER_VALUE]
        #except:
            #print('tradingDate:'+dateStr)
            #print('innerCode:' + str(innerCode))
            #print(dailyQuoteRow)
        turnoverVolume = dailyQuoteRow[StockConst.TURNOVER_VOLUME]

        #可卖
        #if sellFlg != -1:
        #actualSellList.append(innerCode)
        stockHoldEntity = currHoldSet.pop(innerCode)
        vol = stockHoldEntity.vol
        sellPrice = turnoverValue / turnoverVolume
        #卖出后所得资金（没有扣佣金）
        turnover = sellPrice * vol
        # 佣金（元）
        commission = BackTestHelper.get_sell_commission(turnover, StockConst.SELL_COMMISSION / 100)
        # 扣掉佣金后所得金额
        turnover = turnover - commission
        # 更新可用金额(增加)
        capitalEntity.increase_usable_cash(turnover)
        # 加入交易表
        stockTradeDict = {'tradingDate': tradingDate, 'innerCode': innerCode, 'type': -1, 'vol': vol, 'price': sellPrice,
                          'turnover': turnover, 'commission': commission}
        stockTradeList.append(stockTradeDict)
        #实际卖出数
        #numOfActualSell += 1
        """
        if DateUtil.datetime2Str(tradingDate) == '2014-12-09':
            print('-----handleSellList-----')
            print(DateUtil.datetime2Str(tradingDate))
            print(innerCode)
            print(vol)
            print(sellPrice)
            print(turnoverValue)
            print(dailyQuoteRow)
            print('----------')
        """

        #changePCT = NumUtil.getChangePCT(prevClosePrice, sellPrice, 2)
        #realChangePCT = (changePCT - StockConst.sellCommission) * vol / 100.0
        #partChangePCT = partChangePCT + realChangePCT
        """
        if dateStr == '2001-01-17':
            print("vol:"+str(vol)+" turnoverValue:"+str(turnoverValue)+" turnoverVolume:"+str(turnoverVolume)+
                  " prevClosePrice:"+str(prevClosePrice)+" closePrice:"+str(closePrice)+" sellPrice:"+str(sellPrice)+
                  " changePCT:"+str(changePCT)+
                  " realChangePCT:"+str(realChangePCT)+" partChangePCT:"+str(partChangePCT))
        """
        #else:
            #cannotSellList.append(innerCode)
    #return partChangePCT



#今日选股和昨日选股的差集
#currSourceData: dataFrame
#currHoldSet: dict
#return: innerCode list
#currList - lastList
def getDifference(currSourceData, currHoldSet, typ):
    currList = []
    lastList = []

    if len(currSourceData) != 0:
        #for index, row in currSourceData.iterrows():
            #currList.append(index[1])
        currList = list(currSourceData.index.get_level_values(1))

    if len(currHoldSet) != 0:
        #for innerCode in currHoldSet:
            #lastList.append(innerCode)
        lastList = list(currHoldSet.keys())
        lastList.sort()

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

    if len(currSourceData) != 0:
        #for index, row in currSourceData.iterrows():
            #currList.append(index[1])
        currList = list(currSourceData.index.get_level_values(1))

    if len(currHoldSet) != 0:
        #for innerCode in currHoldSet:
            #lastList.append(innerCode)
        lastList = list(currHoldSet.keys())
        lastList.sort()

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
"""
def calculateUsableVol(currHoldSet):
    currVol = 0;
    for innerCode in currHoldSet:
        vol = currHoldSet[innerCode]
        currVol = currVol + vol
    return 100 - currVol
"""

#计算当日总市值:股票市值+可用资金
#closePrice mv放入持仓表
def calculateDailyMV(currHoldSet,capitalEntity,dailyQuote,tradingDate,stockHoldDailyList,initialMV):
    usableCach = capitalEntity.get_usable_cash()
    dailyMV = 0
    for innerCode in currHoldSet:
        dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        stockHoldEntity = currHoldSet[innerCode]
        vol = stockHoldEntity.vol
        # print('innerCode:' + str(innerCode))
        closePrice = dailyQuoteRow[StockConst.CLOSE_PRICE]
        mv = vol * closePrice
        dailyMV += mv
        cost = stockHoldEntity.cost
        profit = (closePrice-cost) *vol

        holdDict = {'tradingDate': tradingDate,
                'innerCode': innerCode,
                'vol': vol,
                'buyPrice': stockHoldEntity.buyPrice,
                'cost': cost,
                'closePrice': closePrice,
                'mv': mv,
                'profit': profit,
                'profitPCT': NumUtil.get_round(profit / initialMV * 100, 5)}

        stockHoldDailyList.append(holdDict)
    #print('dailyMV:' + str(dailyMV))
    #print('usableCach:' + str(usableCach))
    dailyMV = dailyMV + usableCach
    return dailyMV



def debugDailyQuote(groupedSignalData):
    """
    # 行情数据Debug
    #dailyQuoteToDebug = pd.DataFrame()
    signalDataToDebug = groupedSignalData.ix['2001-07-30']
    print('行情数据:')
    print('signalDataToDebug:'+str(len(signalDataToDebug)))
    for index, row in signalDataToDebug.iterrows():
        tradingDate = index[0]
        innerCode = index[1]
        dailyQuoteRow = SourceDataDao.selectByInnerCodeAndDate(dailyQuote, tradingDate, innerCode)
        #dailyQuoteToDebug.append(dailyQuoteRow)
        print(dailyQuoteRow)
    #dailyQuoteToDebug.to_csv(StockConst.root + '\export\dailyQuoteToDebug.csv')
    """

#主程序
@TimeUtil.check_consumed_time2
def main():
    signalData = SourceDataDao.getSignalData()
    #dailyQuote = SourceDataDao.getDailyQuote()
    dailyQuote = SourceDataDao.getNewDailyQuote()

    #columns filter
    #df3 = sourceData.loc[(df['Mom'] <= 4) & (df['Mom'] <= 4), ['Mom']]

    #index filter
    #startDate=DateUtils.str2Datetime('20010105');
    #endDate=DateUtils.str2Datetime('20010111');
    #df4 = df3.ix[startDate:endDate]

    numOfDailyHolding = 5

    #select top 5 group by TradingDay order by Mom desc
    groupedSignalData = signalData.groupby(level=StockConst.TRADINGDAY).apply(SelectUtil.top, numOfDailyHolding, StockConst.MOM, False)

    #param
    #period = 5
    #startDate = '1/8/2001'
    startDate = '1/8/2001'
    #endDate = '1/1/2017'
    #eendDate = '5/18/2001'
    endDate = '12/31/2001'
    #endDate = '12/31/2002'
    #endDate = '1/9/2001'

    #time series
    #dateList = DateUtil.getDateList2(startDate,endDate)

    #当前持仓 key:innerCode value:
    currHoldSet = {}
    stockHoldDF = {}
    stockTradeList = []
    #资金情况
    #capitalDict = {'usableCach':1000000}
    #初始资金
    initialMV = 1000000
    capitalEntity = CapitalEntity.CapitalEntity(initialMV)
    lastMV = initialMV

    #lastSignalData = pd.DataFrame()
    #usableVol = 100;
    netValue = 1;
    #初始化每日统计表
    stockStatDailyDf = pd.DataFrame(index=pd.date_range(startDate, endDate),
                columns=['netValue','changePCT','buyCnt','sellCnt','prevHoldCnt','currHoldCnt','cannotSellCnt','cannotBuyCnt',
                         'usableCach','mv'])
    #初始化每日持仓表
    stockHoldDailyList = []
    #从信号表中取得唯一性日期
    dateList = SourceDataDao.select_date_from_signal(signalData, startDate, endDate)
    for date in dateList:
        dateStr = DateUtil.datetime2_str(date)
        #print(dateStr)
        #isinstance(date, datetime)
        currSignalData = groupedSignalData.ix[date]
        if StockConst.IS_DEBUG:
            print("currSignalData:"+str(len(currSignalData)))
            #print(currSignalData)
        # 计划买入列表
        buyList = getBuyList(currSignalData,currHoldSet)
        # 计划卖出列表
        sellList = getSellList(currSignalData,currHoldSet)
        # 昨日持仓部分（在今日持仓中）
        prevHoldList = getPrevHoldList(currSignalData,currHoldSet)

        """
        if (dateStr >= '2015-01-05') & (dateStr <= '2015-01-05'):
            print('-----'+dateStr+'-----')
            #print(currSignalData)
            #print(buyList)
            print(list(currHoldSet.keys()))
            for key in currHoldSet.keys():
                print(str(key) + ':' + currHoldSet.get(key).openDate)
            print('----------------')
        """
        #dailyChangePCT = 0
        #actualSellList=[]
        #actualBuyList=[]
        cannotSellList=[]
        cannotBuyList = []

        #实际买入个数
        numOfActualBuy = getNumOfActualBuy(date, buyList, dailyQuote)
        #1.处理卖出
        handleSellList(date,sellList,dailyQuote,stockHoldDF,stockTradeList,currHoldSet,cannotSellList,
                       capitalEntity,numOfActualBuy,signalData,prevHoldList,numOfDailyHolding)
        #2.处理买入
        handleBuyList(date,buyList,dailyQuote,stockHoldDF,stockTradeList,currHoldSet,cannotBuyList,capitalEntity)
        #3.计算当日净值
        currMV = calculateDailyMV(currHoldSet, capitalEntity, dailyQuote, date, stockHoldDailyList, initialMV)

        #4.个数
        buyCnt = len(buyList)#actualBuyList
        sellCnt = len(sellList)#actualSellList
        prevHoldCnt = len(prevHoldList)
        currHoldCnt = len(currHoldSet)
        cannotSellCnt = len(cannotSellList)
        cannotBuyCnt = len(cannotBuyList)

        #if StockConst.isDebug:
            #print("dateStr:" + dateStr + " changePCTBuy:" + str(changePCTBuy) + " changePCTSell:" + str(changePCTSell) +
                  #" changePCTHold:" + str(changePCTHold))

        #每日净值
        netValue = currMV / initialMV
        #print("netValue:" + str(netValue))
        #每日收益
        dailyChangePCT = NumUtil.get_change_pct(lastMV, currMV, 2)
        #每日可用现金
        usableCach = capitalEntity.get_usable_cash()
        #
        stockStatDailyDf.ix[dateStr] = netValue,dailyChangePCT,buyCnt,sellCnt,prevHoldCnt,currHoldCnt,cannotSellCnt,cannotBuyCnt,usableCach,currMV
        #
        lastMV = currMV

    #debug 行情数据
    debugDailyQuote(groupedSignalData)

    # 信号数据
    #groupedSignalData.to_csv(StockConst.root + '\export\groupedSignalData.csv')

    # 每日交易
    # print('每日交易:')
    stockTradeDailyDf = pd.DataFrame(stockTradeList)
    stockTradeDailyDf.sort_values(by=['tradingDate'], ascending=True)
    stockTradeDailyDf.to_csv(StockConst.ROOT + '\export\stockTradeDaily.csv')

    # 每日持仓
    #print('每日持仓:')
    stockHoldDailyDf = pd.DataFrame(stockHoldDailyList)
    stockHoldDailyDf.sort_values(by=['tradingDate'],ascending=True)
    stockHoldDailyDf.to_csv(StockConst.ROOT + '\export\stockHoldDaily.csv')

    #每日统计(收益，净值，买入数，卖出数，持有数)
    stockStatDailyDf = stockStatDailyDf.dropna(how='all')
    print('每日统计:')
    print(stockStatDailyDf)
    stockStatDailyDf.to_csv(StockConst.ROOT + '\export\stockStatDaily.csv')

    # 每年统计
    yearDf = StockYearService.main(stockStatDailyDf)
    print('每年统计:')
    print(yearDf)

    # 最大回撤
    maxdrop = StockMaxDropNewService.get_max_drop(stockStatDailyDf)
    print('最大回撤:')
    print(maxdrop)
    #每年的最大回撤
    maxdropDf = StockMaxDropNewService.get_max_drop_for_each_year(stockStatDailyDf)
    maxdropDf.sort_values(by=["year"])
    print('每年的最大回撤:')
    print(maxdropDf)

    #夏普比率
    sharpRatio = SharpRatioNewService.get_sharp_ratio(stockStatDailyDf)
    print('夏普比率:')
    print(sharpRatio)
    #每年的夏普比率
    sharpRatioDf = SharpRatioNewService.get_sharp_ratio_for_each_year(stockStatDailyDf)
    sharpRatioDf.sort_values(by=["year"])
    print('每年的夏普比率:')
    print(sharpRatioDf)



main()




