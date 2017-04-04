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
import matplotlib.pyplot as plt

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from datetime import datetime
import math
import time

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

    if StockConst.IS_DEBUG:
        start_1 = time.clock()

    # #创建2列DF: innerCode，Mom（空）
    # dic = {StockConst.InnerCode: planSellList}
    # sortedSellDf = pd.DataFrame(data=dic)
    # sortedSellDf.insert(1, StockConst.Mom, Series())
    # sortedSellDf = sortedSellDf.set_index([StockConst.InnerCode])
    # # print(sortedSellDf)
    #
    # # sortedSellDf = sortedSellDf.groupby(level=0).apply(setMom,tradingDate,signalData)#tradingDate,signalData
    # # print(sortedSellDf)
    #
    # for index, row in sortedSellDf.iterrows():
    #     innerCode = index
    #     signalEntity = SourceDataDao.selectSignalByDateAndInnerCode2(signalData, tradingDate, innerCode, StockConst.Mom)
    #     # sortedSellDf.loc[index, [StockConst.Mom]] = signalEntity[StockConst.Mom]
    #     sortedSellDf.loc[index, [StockConst.Mom]] = signalEntity

    techDict = {}
    for innerCode in planSellList:
        signalEntity = SourceDataDao.select_signal_by_date_and_inner_code(signalData, tradingDate, innerCode)
        techDict.setdefault(innerCode, signalEntity[StockConst.MOM])#TODO

    dict = sorted(techDict.items(), key=lambda d: d[1], reverse=True)
    # print(dict)
    planSellList = []
    for x in dict: planSellList.append(x[0])

    #print(sortedSellList)
    #从信号数据中获取Mom用于排序
    # for innerCode in planSellList:
    #     # signalEntity = SourceDataDao.selectSignalByDateAndInnerCode(signalData, tradingDate, innerCode)
    #     #entity = signalData.ix[(tradingDate, innerCode)]
    #     sortedSellDf.loc[(sortedSellDf[StockConst.InnerCode] == innerCode), [StockConst.Mom]] = 1 # signalEntity[StockConst.Mom]

    # sortedSellDf = signalData[(signalData.index.get_level_values(0) == tradingDate) & (signalData.index.get_level_values(1).isin(planSellList))]

    #按Mom倒序排序
    # sortedSellDf = sortedSellDf.sort_values(by=StockConst.Mom, ascending=False)
    # print(sortedSellDf)

    if StockConst.IS_DEBUG:
        end_1 = time.clock()
        print("节点1花费时间：%f s" % (end_1 - start_1))

    if StockConst.IS_DEBUG:
        start_2 = time.clock()

    #卖出列表中保留的股票
    toKeepInSellList = []
    #保留的股票: 停牌或一字跌停股
    #if len(toKeepInSellList) < numOfToKeepInSellList:
    for innerCode in planSellList:
    # for index,row in sortedSellDf.iterrows():
        # innerCode = row[StockConst.InnerCode]
        # innerCode = index
        #try:
        isCannotSell = SourceDataDao.check_if_cannot_sell(dailyQuote, tradingDate, innerCode)
        # isCannotSell = False
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

    if StockConst.IS_DEBUG:
        end_2 = time.clock()
        print("节点2花费时间：%f s" % (end_2 - start_2))

    if StockConst.IS_DEBUG:
        start_3 = time.clock()

    # 保留的股票:按sortedSellDf的顺序加入
    # for index,row in sortedSellDf.iterrows():
    for innerCode in planSellList:
        if len(toKeepInSellList) < numOfToKeepInSellList:
            # innerCode = row[StockConst.InnerCode]
            # innerCode = index
            if(innerCode not in toKeepInSellList) :
                toKeepInSellList.append(innerCode)

    #去掉需要保留的股票
    # actualSellList = sortedSellDf[~(sortedSellDf.index.get_level_values(1).isin(toKeepInSellList))].index.get_level_values(1)
    # actualSellList = sortedSellDf[~(sortedSellDf[StockConst.InnerCode].isin(toKeepInSellList))][StockConst.InnerCode].values
    actualSellList = list(set(planSellList).difference(set(toKeepInSellList)))
    #print('toSellInSellList')
    #print(toSellInSellList)

    if StockConst.IS_DEBUG:
        end_3 = time.clock()
        print("节点3花费时间：%f s" % (end_3 - start_3))

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
# @TimeUtil.checkConsumedTime6
def main(select_stock_1day_func,trade_1day_func,techList,signalDataAddr = '', dailyQuoteAddr = '', startDate = '2004-01-01', endDate = '2005-12-31'):
    start = time.clock()

    signalData = SourceDataDao.load_signal_data(signalDataAddr) #ByDate
    #dailyQuote = SourceDataDao.loadDailyQuote()
    dailyQuote = SourceDataDao.load_new_daily_quote(dailyQuoteAddr) #ByDate

    start_1 = time.clock()
    signalData = signalData[(signalData.index.get_level_values(0) >= startDate) & (signalData.index.get_level_values(0) <= endDate) ]
    end_1 = time.clock()
    print("signalData花费时间：%f s" % (end_1 - start_1))

    # print(startDate)
    # print(endDate)
    dateList = SourceDataDao.select_date_from_signal(signalData, startDate, endDate)
    # print(dateList)

    # 统计结果
    stockStatDailyDf = pd.DataFrame(index=pd.date_range(startDate, endDate),
                                    columns=['netValue', 'changePCT', 'buyCnt', 'sellCnt', 'prevHoldCnt',
                                             'currHoldCnt', 'cannotSellCnt', 'cannotBuyCnt',
                                         'usableCach', 'mv'])
    # 每日持仓
    stockHoldDailyList = []
    # 交易结果
    stockTradeList = []

    start_trade = time.clock()
    # 交易
    t1d = process1day(startDate, endDate, dailyQuote, signalData, dateList, stockStatDailyDf, stockHoldDailyList, stockTradeList)
    res = signalData.groupby(level=StockConst.TRADINGDAY).apply(t1d.deal, techList, select_stock_1day_func, trade_1day_func)
    end_trade = time.clock()
    print("交易花费时间：%f s" % (end_trade - start_trade))


    result = ''

    start_stat = time.clock()
    # 信号数据
    #groupedSelectStock.to_csv(StockConst.root + '\export\groupedSelectStock.csv')

    # 每日交易
    # print('每日交易:')
    # print(stockTradeList)
    stockTradeDailyDf = pd.DataFrame(stockTradeList)
    stockTradeDailyDf.sort_values(by=['tradingDate'], ascending=True)
    # stockTradeDailyDf.to_csv(StockConst.root + '\export\stockTradeDaily.csv')

    # 每日持仓
    #print('每日持仓:')
    stockHoldDailyDf = pd.DataFrame(stockHoldDailyList)
    stockHoldDailyDf.sort_values(by=['tradingDate'],ascending=True)
    # stockHoldDailyDf.to_csv(StockConst.root + '\export\stockHoldDaily.csv')

    #每日统计(收益，净值，买入数，卖出数，持有数)
    stockStatDailyDf = stockStatDailyDf.dropna(how='all')
    result += '--' * 70 + '\n'
    result += '每日统计:' + '\n'
    result += stockStatDailyDf.to_string() + '\n'
    # stockStatDailyDf.to_csv(StockConst.root + '\export\stockStatDaily.csv')

    # 每年统计
    result += '--' * 70 + '\n'
    yearDf = StockYearService.main(stockStatDailyDf)
    result += '每年统计:' + '\n'
    result += yearDf.to_string() + '\n'

    # 最大回撤
    result += '--' * 70 + '\n'
    maxdrop = StockMaxDropNewService.get_max_drop(stockStatDailyDf)
    result += '最大回撤:' + '\n'
    result += SetUtil.dict_to_string(maxdrop) + '\n'
    #每年的最大回撤
    maxdropDf = StockMaxDropNewService.get_max_drop_for_each_year(stockStatDailyDf)
    maxdropDf.sort_values(by=["year"])
    result += '每年的最大回撤:' + '\n'
    result += maxdropDf.to_string() + '\n'

    #夏普比率
    result += '--' * 70 + '\n'
    sharpRatio = SharpRatioNewService.get_sharp_ratio(stockStatDailyDf)
    result += '夏普比率:' + '\n'
    result += str(sharpRatio) + '\n'
    #每年的夏普比率
    sharpRatioDf = SharpRatioNewService.get_sharp_ratio_for_each_year(stockStatDailyDf)
    sharpRatioDf.sort_values(by=["year"])
    result += '每年的夏普比率:' + '\n'
    result += sharpRatioDf.to_string() + '\n'

    end_stat = time.clock()
    print("统计花费时间：%f s" % (end_stat - start_stat))

    # result += '回测完成'
    end = time.clock()
    print("main花费时间：%f s" % (end - start))

    # 净值曲线图
    stockStatDailyDf['netValue'].plot()
    plt.show()

    resultDic={'stockStatDailyDf':stockStatDailyDf,'result':result}

    print(result)
    return resultDic

#处理1天
#startDate,endDate,
class process1day():
    def __init__(self,startDate,endDate,dailyQuote,signalData,dateList,stockStatDailyDf,stockHoldDailyList,stockTradeList):
        self.startDate = startDate
        self.endDate = endDate
        self.dailyQuote = dailyQuote
        self.signalData = signalData
        self.dateList = dateList
        self.currHoldSet = {}
        self.initialMV = 1000000
        self.capitalEntity = CapitalEntity.CapitalEntity(self.initialMV)
        self.lastMV = self.initialMV

        self.stockStatDailyDf = stockStatDailyDf
        self.stockHoldDailyList = stockHoldDailyList
        self.stockTradeList = stockTradeList

    #处理1天
    #signalData1day: 当天全部信号
    def deal(self,signalData1day,techList,select_stock_1day_func,trade_1day_func):
        #是否有更好的获取当天日期的方法？
        signalDay = signalData1day.index.get_level_values(0).unique()
        signalDayIndex = self.dateList.index(signalDay)

        #非最后一天
        if signalDayIndex < (len(self.dateList) - 1):
            #交易日
            tradingDay = self.dateList[signalDayIndex + 1]
            tradingDayStr = DateUtil.datetime2_str(tradingDay)
            #print('dateStr:'+dateStr)
        # 最后一天
        else:
            return

        #选股结果（当天）
        currSelectStock = select_stock_1day_func(signalData1day,techList)

        #交易结果
        dict = trade_1day_func(currSelectStock, self.currHoldSet, self.dailyQuote, tradingDay, self.signalData, self.capitalEntity)
        # end_inloop1 = time.clock()
        # print("trade_func花费时间：%f s" % (end_inloop1 - start_inloop1))

        actualBuyList = dict['actualBuyList']
        actualSellList = dict['actualSellList']
        prevHoldList = dict['prevHoldList']
        cannotBuyList = dict['cannotBuyList']
        cannotSellList = dict['cannotSellList']
        stockTradeListDaily = dict['stockTradeList']

        if len(stockTradeListDaily) > 0 :
            self.stockTradeList.extend(stockTradeListDaily)

        #当日市值
        currMV = calculateDailyMV(self.currHoldSet, self.capitalEntity, self.dailyQuote, tradingDay, self.stockHoldDailyList, self.initialMV)

        #个数
        buyCnt = len(actualBuyList)
        sellCnt = len(actualSellList)
        prevHoldCnt = len(prevHoldList)
        currHoldCnt = len(self.currHoldSet)
        cannotSellCnt = len(cannotSellList)
        cannotBuyCnt = len(cannotBuyList)

        # print(currMV)

        # if StockConst.isDebug:
        # print("dateStr:" + dateStr + " changePCTBuy:" + str(changePCTBuy) + " changePCTSell:" + str(changePCTSell) +
        # " changePCTHold:" + str(changePCTHold))

        # 当日净值
        netValue = currMV / self.initialMV
        # print("netValue:" + str(netValue))
        # 当日收益
        dailyChangePCT = NumUtil.get_change_pct(self.lastMV, currMV, 2)
        # 当日可用现金
        usableCach = self.capitalEntity.get_usable_cash()
        #
        self.stockStatDailyDf.ix[tradingDayStr] = netValue, dailyChangePCT, buyCnt, sellCnt, prevHoldCnt, currHoldCnt, cannotSellCnt, cannotBuyCnt, usableCach, currMV
        #
        self.lastMV = currMV


def select_stock_1day_func1(signalData1day,techList):
    numOfDailySignal = 5
    return SelectUtil.top(signalData1day, numOfDailySignal, techList[0], False)

def select_stock_1day_func2(signalData1day,techList):
    numOfDailySignal = 5
    return SelectUtil.top(signalData1day, numOfDailySignal, techList[0], True)

def select_stock_1day_func3(signalData1day,techList):
    numOfDailySignal = 5

    data = {'Momp': np.random.randint(0, 101, size=len(signalData1day))}
    randDf = DataFrame(data, index=signalData1day.index)
    signalData1day['Momp'] = randDf['Momp']

    return SelectUtil.top_with_weight(signalData1day, numOfDailySignal, techList, False, SelectUtil.handle_na1)

    # groupedSelectStock = signalData.groupby(level=StockConst.TradingDay).apply(SelectUtil.topWithWeight,numOfDailySignal, techList, False,SelectUtil.handleNA1)  # False True  StockConst.Mom,'Momp'
    # groupedSelectStock.to_csv(StockConst.root + '\export\select_stock_func3.csv')
    # return groupedSelectStock


#交易方法1
#numOfDailySignal,
#算出实际买入和卖出的股票
def trade_1day_func1(currSelectStock, currHoldSet, dailyQuote, tradingDay, signalData, capitalEntity):
    # 计划买入列表
    t1 = time.time()
    planBuyList = getPlanBuyList(currSelectStock, currHoldSet)
    # 计划卖出列表
    t2 = time.time()

    planSellList = getPlanSellList(currSelectStock, currHoldSet)
    # 昨日持仓部分（在今日持仓中）
    t3 = time.time()

    prevHoldList = getPrevHoldList(currSelectStock, currHoldSet)
    # dailyChangePCT = 0
    t4 = time.time()

    cannotSellList = []
    cannotBuyList = []
    # 实际买入列表
    actualBuyList = getActualBuyList(planBuyList, dailyQuote, tradingDay, cannotBuyList)
    t5 = time.time()

    # "卖出列表"中要保留的股票数
    numOfToKeepInSellList = len(cannotBuyList)
    t6 = time.time()

    # 实际卖出列表
    actualSellList = getActualSellList(planSellList, tradingDay, signalData, dailyQuote, numOfToKeepInSellList,
                                       cannotSellList)
    stockTradeList = []
    t7 = time.time()

    # 1.处理实际卖出
    handleSellList(tradingDay, dailyQuote, stockTradeList, currHoldSet, capitalEntity, actualSellList)
    t8 = time.time()

    # 2.处理实际买入
    handleBuyList(tradingDay, dailyQuote, stockTradeList, currHoldSet, capitalEntity, actualBuyList)
    t9 = time.time()


    # print(stockTradeList)

    #
    dict = {'actualBuyList':actualBuyList,'actualSellList':actualSellList,'prevHoldList':prevHoldList,
           'cannotBuyList':cannotBuyList,'cannotSellList':cannotSellList,'stockTradeList':stockTradeList}
    t10 = time.time()

    # import numpy as np
    # print(np.array([t2,t3,t4,t5,t6,t7,t8,t9,t10] - np.array([t1,t2,t3,t4,t5,t6,t7,t8,t9] )))

    return dict






