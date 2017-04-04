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
#import matplotlib.pyplot as plt

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from datetime import datetime
import math

#买入列表中实际买入的股票(排除了停牌和一字涨停)
def getActualBuyList(planBuyList,dailyQuote,tradingDate,cannotBuyList):
    if len(planBuyList) == 0:
        return planBuyList
    actualBuyList = []
    for innerCode in planBuyList:
        isCannotBuy = SourceDataDao.check_if_cannot_buy(dailyQuote, tradingDate, innerCode)
        #buyFlg = dailyQuoteRow[StockConst.buyFlg]
        #可买
        if not isCannotBuy:
            actualBuyList.append(innerCode)
        else:
            cannotBuyList.append(innerCode)

    return actualBuyList

#卖出列表中实际卖出的股票（去停牌，去一字跌停，去保留股）
#排序：Mom降序
#分成2部分
#toKeepInSellList: 需要保留的股票(包括停牌和一字跌停和为了满足当日持仓个数保留的股票)
#toSellInSellList: 要卖出的股票(剩下的)
#cannotSellList: 停牌和一字跌停不能卖出
#返回:toSellInSellList
def getActualSellList(planSellList,tradingDate,signalData,dailyQuote,numOfToKeepInSellList,cannotSellList):
    if len(planSellList) == 0:
        return planSellList
    #创建2列DF，innerCode，Mom（空）
    dic = {StockConst.INNERCODE: planSellList}
    sortedSellDf = pd.DataFrame(data=dic)
    sortedSellDf.insert(1, StockConst.MOM, Series())
    #print(sortedSellList)
    #从信号数据中获取Mom用于排序
    for innerCode in planSellList:
        signalEntity = SourceDataDao.select_signal_by_date_and_inner_code(signalData, tradingDate, innerCode)
        #entity = signalData.ix[(tradingDate, innerCode)]
        sortedSellDf.loc[(sortedSellDf[StockConst.INNERCODE] == innerCode), [StockConst.MOM]] = signalEntity[StockConst.MOM]
    #按Mom倒序排序
    sortedSellDf = sortedSellDf.sort_values(by=StockConst.MOM, ascending=False)

    #卖出列表中保留的股票
    toKeepInSellList = []
    #保留的股票: 停牌或一字跌停股
    #if len(toKeepInSellList) < numOfToKeepInSellList:
    for index,row in sortedSellDf.iterrows():
        innerCode = row[StockConst.INNERCODE]
        #try:
        isCannotSell = SourceDataDao.check_if_cannot_sell(dailyQuote, tradingDate, innerCode)
        #except:
             #print('getToSellInSellList '+DateUtil.datetime2Str(tradingDate)+' '+str(innerCode))
             #print(sortedSellDf)
             #print(sellList)
             #print(currHoldSet)
             #print(dailyQuoteRow)
             #退市的股票:卖出

        #不能卖
        if isCannotSell:
            toKeepInSellList.append(innerCode)
            cannotSellList.append(innerCode)

    # 保留的股票:按sortedSellDf的顺序加入
    for index,row in sortedSellDf.iterrows():
        if len(toKeepInSellList) < numOfToKeepInSellList:
            innerCode = row[StockConst.INNERCODE]
            if(innerCode not in toKeepInSellList) :
                toKeepInSellList.append(innerCode)

    #去掉需要保留的股票
    actualSellList = sortedSellDf[~(sortedSellDf[StockConst.INNERCODE].isin(toKeepInSellList))][StockConst.INNERCODE].values
    #print('toSellInSellList')
    #print(toSellInSellList)

    return actualSellList

#处理买入交易
def handleBuyList(tradingDate,dailyQuote,stockTradeList,currHoldSet,capitalEntity,actualBuyList):
    usableCach = capitalEntity.get_usable_cash()
    if usableCach == 0:
        return

    if len(actualBuyList) == 0:
        return

    buyCach = usableCach/len(actualBuyList)
    #print('vol:'+vol)
    #partChangePCT = 0
    # buyList全部可以买入
    for innerCode in actualBuyList:
        dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        #print('innerCode:'+str(innerCode))
        #print(dailyQuoteRow)
        #可买
        #if buyFlg != -1:
        #平均买入价（没有算佣金）
        buyPrice = BackTestHelper.get_vwap(dailyQuoteRow)
        #成本价（算佣金）
        cost = buyPrice*(1 + StockConst.BUY_COMMISSION / 100)
        #仓位（股）
        #vol = NumUtil.getRound(turnover/cost,StockConst.volScale)
        #佣金（元）
        commission = BackTestHelper.get_buy_commission(buyCach, StockConst.BUY_COMMISSION / 100)
        #买入市值
        buyMV = buyCach - commission
        #更新可用金额(减少)
        capitalEntity.reduce_usable_cash(buyCach)
        #changePCT = NumUtil.getChangePCT(cost, closePrice, 2)
        #realChangePCT = (changePCT - StockConst.buyCommission) * vol / 100.0
        #partChangePCT = partChangePCT + realChangePCT
        #
        #stockHold = StockHoldEntity.StockHoldEntity(tradingDate,innerCode,vol)
        #stockTrade = StockTradeEntity.StockTradeEntity(tradingDate, innerCode, 1, vol, cost, '', '')
        dateStr = DateUtil.datetime2_str(tradingDate)
        stockTradeDict = {'tradingDate':dateStr,'innerCode':innerCode,'type':1,
                          'price':buyPrice,'buyMV':buyMV,'sellMV':'','commission': commission,
                          'sellCach':'','buyCach':buyCach,'openDate':''}
        stockTradeList.append(stockTradeDict)
        #插入表
        #stockHoldDF.setdefault(innerCode,stockHold)
        #当前持仓
        stockHoldEntity = StockHoldEntity.StockHoldEntity(innerCode, buyPrice, cost, DateUtil.datetime2_str(tradingDate), buyMV)
        currHoldSet.setdefault(innerCode,stockHoldEntity)
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
def handleSellList(tradingDate,dailyQuote,stockTradeList,currHoldSet,capitalEntity,actualSellList):
    #partChangePCT = 0
    dateStr = DateUtil.datetime2_str(tradingDate)

    if len(actualSellList) == 0:
        return

    #sellList全部可以卖出
    for innerCode in actualSellList:
        #print('innerCode:' + str(innerCode))
        #try:
        dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        #except:
            #退市的股票: 查询不到行情,取最后一个交易日
            #dailyQuoteRow = SourceDataDao.selectByLastDay(dailyQuote,innerCode)
        # print(dailyQuoteSingle)

        #可卖
        #if sellFlg != -1:
        #actualSellList.append(innerCode)
        stockHoldEntity = currHoldSet.pop(innerCode)
        #vol = stockHoldEntity.vol
        sellPrice = BackTestHelper.get_vwap(dailyQuoteRow)
        #卖出市值（没有扣佣金）
        #turnover = sellPrice * vol
        sellMV = BackTestHelper.get_sell_mv(stockHoldEntity.buyPrice, stockHoldEntity.buyMV, sellPrice)
        #佣金（元）
        commission = BackTestHelper.get_sell_commission(sellMV, StockConst.SELL_COMMISSION / 100)
        #卖出后所得资金(扣掉佣金后所得金额)
        sellCach = sellMV - commission
        # 更新可用金额(增加)
        capitalEntity.increase_usable_cash(sellCach)
        # 开仓日
        openDate = stockHoldEntity.openDate
        # 加入交易表
        stockTradeDict = {'tradingDate': dateStr, 'innerCode': innerCode, 'type': -1, 'price': sellPrice,
                          'buyMV': '', 'sellMV': sellMV, 'commission': commission,
                          'sellCach': sellCach,'buyCach':'','openDate':openDate}
        stockTradeList.append(stockTradeDict)
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
def getPlanBuyList(currSourceData, currHoldSet):
    return getDifference(currSourceData,currHoldSet,1)

#卖出列表
def getPlanSellList(currSourceData, currHoldSet):
    return getDifference(currSourceData,currHoldSet,-1)

#昨日持有列表
def getPrevHoldList(currSourceData, currHoldSet):
    return getIntersection(currSourceData,currHoldSet)

#计算当日总市值:股票市值+可用资金
#closePrice mv放入持仓表
def calculateDailyMV(currHoldSet,capitalEntity,dailyQuote,tradingDate,stockHoldDailyList,initialMV):
    usableCach = capitalEntity.get_usable_cash()
    dailyMV = 0
    for innerCode in currHoldSet:
        #try:
        dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode)
        #except:
            #缺少数据,取最近一个交易日的数据
            #dailyQuoteRow = SourceDataDao.selectByPrevTradingDay(dailyQuote, tradingDate, innerCode)
            #print('calculateDailyMV '+DateUtil.datetime2Str(tradingDate)+' '+str(innerCode))

        stockHoldEntity = currHoldSet[innerCode]
        #vol = stockHoldEntity.vol
        # print('innerCode:' + str(innerCode))
        closePrice = BackTestHelper.get_close_price(dailyQuoteRow)
        #mv = vol * closePrice
        #收盘市值
        closeMV = BackTestHelper.get_sell_mv(stockHoldEntity.buyPrice, stockHoldEntity.buyMV, closePrice)
        #每日市值
        dailyMV += closeMV
        #该股收益(已扣佣金)(仅用于查看)
        profit = (closeMV - stockHoldEntity.buyMV) * (1 - StockConst.BUY_COMMISSION / 100)

        holdDict = {'tradingDate': tradingDate,
                'innerCode': innerCode,
                'buyPrice': stockHoldEntity.buyPrice,
                'buyMV': stockHoldEntity.buyMV,
                'cost': stockHoldEntity.cost,
                'closePrice': closePrice,
                'closeMV': closeMV,
                'profit': profit,
                'openDate': stockHoldEntity.openDate,
                'profitPCT': NumUtil.get_round(profit / initialMV * 100, 5)}

        stockHoldDailyList.append(holdDict)
    #print('dailyMV:' + str(dailyMV))
    #print('usableCach:' + str(usableCach))
    dailyMV = dailyMV + usableCach
    return dailyMV

#主程序
#@TimeUtil.checkConsumedTime2
def main(select_stock,numOfDailySignal):
    signalData = SourceDataDao.getSignalData()
    #dailyQuote = SourceDataDao.getDailyQuote()
    dailyQuote = SourceDataDao.getNewDailyQuote()

    #参数
    #每天信号数
    #numOfDailySignal = 5
    #初始资金
    initialMV = 1000000 #1000000
    #开始结束日期
    #startDate = '1/8/2001'
    startDate = '1/1/2004'
    #endDate = '1/1/2017'
    #eendDate = '5/18/2001'
    endDate = '12/31/2005'
    #endDate = '12/31/2002'
    #endDate = '1/9/2001'

    #select top 5 group by TradingDay order by Mom desc
    groupedSignalData = select_stock(signalData,numOfDailySignal)
    #groupedSignalData = signalData.groupby(level=StockConst.TradingDay).apply(SelectUtil.top,numOfDailySignal,StockConst.Mom,False) #False True

    #当前持仓 key:innerCode value:
    currHoldSet = {}
    stockTradeList = []
    #
    capitalEntity = CapitalEntity.CapitalEntity(initialMV)
    lastMV = initialMV

    #netValue = 1;
    #初始化每日统计表
    stockStatDailyDf = pd.DataFrame(index=pd.date_range(startDate, endDate),
                columns=['netValue','changePCT','buyCnt','sellCnt','prevHoldCnt','currHoldCnt','cannotSellCnt','cannotBuyCnt',
                         'usableCach','mv'])
    #初始化每日持仓表
    stockHoldDailyList = []
    #从信号表中取得唯一性日期
    dateList = SourceDataDao.select_date_from_signal(signalData, startDate, endDate)
    for index, item in enumerate(dateList):
    #for date in dateList:
        #print('index:'+str(index)+' len:'+str(len(dateList)))

        #信号日
        signalDay = dateList[index]
        # 非最后一天
        if index < (len(dateList) - 1):
            #交易日
            tradingDay = dateList[index + 1]
            tradingDayStr = DateUtil.datetime2_str(tradingDay)
            #print('dateStr:'+dateStr)
        # 最后一天
        else:
            break



        #print(dateStr)
        currSignalData = groupedSignalData.ix[signalDay]
        if StockConst.IS_DEBUG:
            print("currSignalData:"+str(len(currSignalData)))
            #print(currSignalData)

        # 计划买入列表
        planBuyList = getPlanBuyList(currSignalData,currHoldSet)
        # 计划卖出列表
        planSellList = getPlanSellList(currSignalData,currHoldSet)
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
        cannotSellList=[]
        cannotBuyList = []
        # 实际买入列表
        actualBuyList = getActualBuyList(planBuyList, dailyQuote, tradingDay, cannotBuyList)
        # "卖出列表"中要保留的股票数
        numOfToKeepInSellList = numOfDailySignal - len(actualBuyList) - len(prevHoldList)
        # 实际卖出列表
        actualSellList = getActualSellList(planSellList, tradingDay, signalData, dailyQuote, numOfToKeepInSellList,cannotSellList)

        #1.处理实际卖出
        handleSellList(tradingDay,dailyQuote,stockTradeList,currHoldSet,capitalEntity,actualSellList)
        #2.处理实际买入
        handleBuyList(tradingDay,dailyQuote,stockTradeList,currHoldSet,capitalEntity,actualBuyList)
        #3.计算当日市值
        currMV = calculateDailyMV(currHoldSet, capitalEntity, dailyQuote, tradingDay, stockHoldDailyList, initialMV)

        #4.个数
        buyCnt = len(actualBuyList)
        sellCnt = len(actualSellList)
        prevHoldCnt = len(prevHoldList)
        currHoldCnt = len(currHoldSet)
        cannotSellCnt = len(cannotSellList)
        cannotBuyCnt = len(cannotBuyList)

        #if StockConst.isDebug:
            #print("dateStr:" + dateStr + " changePCTBuy:" + str(changePCTBuy) + " changePCTSell:" + str(changePCTSell) +
                  #" changePCTHold:" + str(changePCTHold))

        #当日净值
        netValue = currMV / initialMV
        #print("netValue:" + str(netValue))
        #当日收益
        dailyChangePCT = NumUtil.get_change_pct(lastMV, currMV, 2)
        #当日可用现金
        usableCach = capitalEntity.get_usable_cash()
        #
        stockStatDailyDf.ix[tradingDayStr] = netValue,dailyChangePCT,buyCnt,sellCnt,prevHoldCnt,currHoldCnt,cannotSellCnt,cannotBuyCnt,usableCach,currMV
        #
        lastMV = currMV

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

    # #净值曲线图
    # stockTradeDailyDf['netValue'].plot()
    # plt.show()

#选股方法1:
#按Mom倒序选前N只
def select_stock1(signalData,numOfDailySignal):
    # numOfDailySignal = 5
    groupedSignalData = signalData.groupby(level=StockConst.TRADINGDAY).apply(SelectUtil.top, numOfDailySignal, StockConst.MOM, False) #False True
    return groupedSignalData

#选股方法2:
#按Mom正序选前N只
def select_stock2(signalData,numOfDailySignal):
    # numOfDailySignal = 5
    groupedSignalData = signalData.groupby(level=StockConst.TRADINGDAY).apply(SelectUtil.top, numOfDailySignal, StockConst.MOM, True) #False True
    return groupedSignalData

main(select_stock2,numOfDailySignal = 5)




