from backtestData.Dao import SourceDataDao
from backtestData.Dao.mssql import SignalDataMSSQLDao
from backtest.Util import SelectUtil
from backtest.Util import DateUtil
from backtest.Util import SetUtil
from backtest.Util import NumUtil
from backtest.Entity import StockHoldEntity
from backtest.Entity import StockTradeEntityBak
from backtest.Entity import CapitalEntity
from backtest.Entity import MVEntity
from backtest.Constance import StockConst
from backtest.Service import StockMaxDropService
from backtest.Service import StockMaxDropNewService
from backtest.Service import SharpRatioService
from backtest.Service import SharpRatioNewService
from backtest.Service import StockYearService
from backtest.Service import BackTestHelper
from backtest.Util import TimeUtil
import matplotlib.pyplot as plt
import copy

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from datetime import datetime
import math
import time

planDictMV = 'MV'
planDictPrice = 'price'
planDictIsAdjust = 'isAdjust'

is_export = True

# #买入列表中实际买入的股票(排除了停牌和一字涨停)
# def get_actual_buy_list(plan_buy_list, daily_quote, trading_day, cannot_buy_list, daily_quote_pn, daily_quote1day):
#     '''
#
#     :param plan_buy_list:
#     :param daily_quote:
#     :param trading_day:
#     :param cannot_buy_list:
#     :param daily_quote_pn:
#     :param daily_quote1day:
#     :return:
#     '''
#     if len(plan_buy_list) == 0:
#         return plan_buy_list
#     actual_buy_list = []
#     for innerCode in plan_buy_list:
#         # print('dailyQuote:' + str(len(dailyQuote)))
#         # print('dailyQuote1day:'+str(len(dailyQuote1day)))
#         # isCannotBuy = SourceDataDao.checkIfCannotBuy(dailyQuote,tradingDay,innerCode)
#         isCannotBuy = SourceDataDao.check_if_cannot_buy_1day(daily_quote1day, innerCode)
#         # isCannotBuy = SourceDataDao.checkIfCannotBuyPn(dailyQuotePn, tradingDay, innerCode)
#         # isCannotBuy = False
#         #buyFlg = dailyQuoteRow[StockConst.buyFlg]
#         #可买
#         if not isCannotBuy:
#             actual_buy_list.append(innerCode)
#         else:
#             cannot_buy_list.append(innerCode)
#
#     return actual_buy_list

#昨日总现金 = 可用现金+可用股票市值折合现金(用于计划买入)
def get_last_total_cash(lastCapitalEntity):
    lastStockMV = lastCapitalEntity.get_stock_mv()  # 昨日股票市值
    lastUsableCash = lastCapitalEntity.get_usable_cash()  # 昨日现金
    # 佣金（元）
    commission = BackTestHelper.get_sell_commission(lastStockMV, StockConst.SELL_COMMISSION / 100)
    # 昨日市值扣掉佣金后可得现金
    # lastMVToCash = lastStockMV - commission
    lastMVToCash = lastStockMV
    # 昨日总现金
    lastTotalCash = lastUsableCash + lastMVToCash

    return lastTotalCash

#计划买入列表（去掉停牌，算出买入现金）：必须是扣掉佣金后的现金，不是市值
def get_plan_buy_list_mv(planBuyList, dailyQuote, tradingDay, cannotBuyList, dailyQuotePn, dailyQuote1day, lastCapitalEntity, currSelectStock, preHoldList, currHoldSet):
    planBuyListMV = []
    if len(planBuyList) == 0:
        return planBuyListMV

    #无需排序，因为planBuyList已经排过序

    # 昨日总现金
    lastTotalCash = get_last_total_cash(lastCapitalEntity)

    for innerCode in planBuyList:
        # print('dailyQuote:' + str(len(dailyQuote)))
        # print('dailyQuote1day:'+str(len(dailyQuote1day)))
        # isCannotBuy = SourceDataDao.checkIfCannotBuy(dailyQuote,tradingDay,innerCode)
        isCannotBuy = SourceDataDao.check_if_cannot_buy_1day(dailyQuote1day, innerCode)
        # isCannotBuy = SourceDataDao.checkIfCannotBuyPn(dailyQuotePn, tradingDay, innerCode)
        # isCannotBuy = False
        #buyFlg = dailyQuoteRow[StockConst.buyFlg]
        #可买
        if not isCannotBuy:
            dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDay, innerCode)
            # 当前vwap
            buyPrice = BackTestHelper.get_vwap(dailyQuoteRow)

            volWeight = currSelectStock.ix[innerCode][StockConst.VOL_WEIGHT]
            # 计划买入现金=昨日总现金*仓位权重
            buyCash = lastTotalCash * volWeight

            # [处理调整仓位2017-03-28]######################################
            # 在昨日持有列表中：调整仓位
            isAdjust = None
            partialFlg = None
            if innerCode in preHoldList:
                stockHoldEntity = currHoldSet.get(innerCode)
                # 当前vwap
                sellPrice = BackTestHelper.get_vwap(dailyQuoteRow)
                # 当前市值
                sellMV = BackTestHelper.get_sell_mv(stockHoldEntity.closePrice, stockHoldEntity.closeMV, sellPrice)
                # 不买的情况
                if buyCash <= sellMV:
                    buyCash = 0
                # 调整仓位
                else:
                    buyCash = buyCash - sellMV
                    isAdjust = 1
                    partialFlg = 1
            #################################################

            # 有买入
            if buyCash > 0:
                planDict = {StockConst.TRADINGDAY: tradingDay, StockConst.INNERCODE: innerCode, planDictMV:buyCash, planDictPrice:buyPrice, planDictIsAdjust:isAdjust, 'partialFlg': partialFlg}
                planBuyListMV.append(planDict)
        else:
            cannotBuyList.append(innerCode)

    return planBuyListMV

#numOfToKeepInSellList,
#计划卖出列表（去掉停牌，算出卖出市值）
def get_plan_sell_list_mv(planSellList, tradingDay, signalData, dailyQuote, cannotSellList, dailyQuote1day, currHoldSet, preHoldList, currSelectStock, lastCapitalEntity):
    planSellListMV = []
    if len(planSellList) == 0:
        return planSellListMV

    # 昨日总现金
    lastTotalCash = get_last_total_cash(lastCapitalEntity)

    # 排序
    planSellList = sort_by_tech(planSellList, signalData, tradingDay, StockConst.MOM) #TODO 排序

    for innerCode in planSellList:
        isCannotSell = SourceDataDao.check_if_cannot_sell_1day(dailyQuote1day, innerCode)

        #能卖
        if not isCannotSell:
            dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDay, innerCode)

            stockHoldEntity = currHoldSet.get(innerCode)
            # 当前vwap
            sellPrice = BackTestHelper.get_vwap(dailyQuoteRow)
            # 当前市值
            sellMV = BackTestHelper.get_sell_mv(stockHoldEntity.closePrice, stockHoldEntity.closeMV, sellPrice) #stockHoldEntity.buyPrice, stockHoldEntity.buyMV

            # [处理调整仓位2017-03-28]######################################
            # 在昨日持有列表中：调整仓位
            isAdjust = None
            partialFlg = None
            if innerCode in preHoldList:
                volWeight = currSelectStock.ix[innerCode][StockConst.VOL_WEIGHT]
                # 计划买入现金=昨日总现金*仓位权重
                buyCash = lastTotalCash * volWeight
                # 不卖的情况
                if sellMV <= buyCash:
                    sellMV = 0
                # 调整仓位
                else:
                    sellMV = sellMV - buyCash
                    isAdjust = 1
                    partialFlg = 1
            #################################################

            # 有卖出
            if sellMV > 0:
                planDict = {StockConst.TRADINGDAY: tradingDay, StockConst.INNERCODE: innerCode, planDictMV: sellMV, planDictPrice: sellPrice, planDictIsAdjust:isAdjust, 'partialFlg': partialFlg}
                planSellListMV.append(planDict)
        else:
            cannotSellList.append(innerCode)

    return planSellListMV

#强制卖出
def get_force_sell_list_mv(prevHoldList, tradingDay, signalData, dailyQuote, dailyQuote1day, currHoldSet):
    forceSellListMV = []
    if len(prevHoldList) == 0:
        return forceSellListMV

    for innerCode in prevHoldList:
        dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDay, innerCode)
        delistFlg = dailyQuoteRow['delistFlg']

        #退市
        if delistFlg == '1':
            stockHoldEntity = currHoldSet.get(innerCode)
            # 当前vwap
            sellPrice = BackTestHelper.get_vwap(dailyQuoteRow)
            # 当前市值
            sellMV = BackTestHelper.get_sell_mv(stockHoldEntity.closePrice, stockHoldEntity.closeMV, sellPrice) #stockHoldEntity.buyPrice, stockHoldEntity.buyMV

            # mVEntity = MVEntity.MVEntity(innerCode, currMV)
            planDict = {StockConst.TRADINGDAY: tradingDay, StockConst.INNERCODE: innerCode, planDictMV: sellMV, planDictPrice:sellPrice, planDictIsAdjust:None, 'partialFlg': None}
            forceSellListMV.append(planDict)

    return forceSellListMV

# 计算总市值
def add_sum_mv(x):
    return x.get(planDictMV)

# planBuyListMV: 计划买入
# planSellListMV：计划卖出
def get_actual_buy_sell_list(planBuyList, planSellList, forceSellList, actualBuyList, actualSellList, capitalEntity):

    usableCash = capitalEntity.get_usable_cash()

    # 1.计划买入总市值
    mvList2 = map(add_sum_mv, planBuyList)
    totalPlanBuyMV = sum(list(mvList2))

    # 2.计划卖出总市值
    mvList3 = map(add_sum_mv, planSellList)
    totalPlanSellMV = sum(list(mvList3))

    # 3.强制卖出总市值
    totalForceSellMV=0
    if len(forceSellList) > 0:
        l4 = map(add_sum_mv, forceSellList)
        totalForceSellMV = sum(list(l4))

    # 总卖出额度 （包含强制卖出）
    totalPlanSellMV += totalForceSellMV

    # 可用资产 = 可用现金 + 总卖出额度
    usableAsset = usableCash + totalPlanSellMV

    # 4.资金多，买少
    # 计划卖出 > 计划买入 => 实际卖出，实际买入
    # 卖出直到卖出额度toSellMV为0为止
    if usableAsset > totalPlanBuyMV:
        # totalPlanSellMV = totalPlanBuyMV
        # 卖出额度 （现金优先买一部分，然后再用卖出额度）
        usableSellMV = totalPlanBuyMV - usableCash

        # 优先处理强制卖出
        if len(forceSellList) > 0:
            actualSellList.extend(forceSellList)
            usableSellMV = usableSellMV - totalForceSellMV

        # 从下往上卖
        planSellList.reverse()
        for planDict in planSellList:
            # 计划卖出已处理完(当有强制卖出时/有可用现金时: 该值有可能小于0)
            if usableSellMV <= 0:
                break

            innerCode = planDict.get(StockConst.INNERCODE)
            sellMV = planDict.get(planDictMV)

            # 单股卖出全部份额
            if usableSellMV >= sellMV:
                usableSellMV = usableSellMV - sellMV

                # planDict.setdefault('partialFlg', None)
                actualSellList.append(planDict)

            # 单股卖出部分份额
            elif usableSellMV < sellMV:
                newPlanDict = planDict.copy()
                # newPlanDict = {StockConst.INNERCODE: innerCode, planDictMV: usableSellMV, planDictPrice: planDict.get(planDictPrice)}
                # newPlanDict.setdefault('partialFlg', 1)
                newPlanDict['partialFlg'] = 1
                newPlanDict[planDictMV] = usableSellMV
                actualSellList.append(newPlanDict)
                usableSellMV = 0

        # 计划买入的全部
        actualBuyList.extend(planBuyList)

    # 5.买多，资金少
    # 计划卖出 < 计划买入 => 实际卖出，实际买入
    # 买入直到总买入额度为0为止
    elif usableAsset <= totalPlanBuyMV:
        # 买入额度
        usableBuyMV = usableAsset

        # 从上往下买
        for planDict in planBuyList:
            # 计划买入已处理完
            if usableBuyMV == 0:
                break

            innerCode = planDict.get(StockConst.INNERCODE)
            buyMV = planDict.get('MV')

            # 单股买入全部份额
            if usableBuyMV >= buyMV:
                usableBuyMV = usableBuyMV - buyMV

                # planDict = {StockConst.InnerCode: innerCode, 'MV': currMV}
                # planDict.setdefault('partialFlg',None)
                actualBuyList.append(planDict)

            # 单股买入部分份额
            elif usableBuyMV < buyMV:
                newPlanDict = planDict.copy()
                # newPlanDict = {StockConst.INNERCODE: innerCode, planDictMV: usableBuyMV, planDictPrice: planDict.get(planDictPrice)}
                # newPlanDict.setdefault('partialFlg', 1)
                newPlanDict['partialFlg'] = 1
                newPlanDict[planDictMV] = usableBuyMV
                actualBuyList.append(newPlanDict)
                usableBuyMV = 0

        # 强制卖出的全部
        if len(forceSellList) > 0:
            actualSellList.extend(forceSellList)
        # 计划卖出的全部
        actualSellList.extend(planSellList)

#planSellList: 排序卖出列表
#tech: 排序字段
def sort_by_tech(planSellList, signalData, tradingDay, tech):
    techDict = {}
    for innerCode in planSellList:
        signalEntity = SourceDataDao.select_signal_by_date_and_inner_code(signalData, tradingDay, innerCode)
        techDict.setdefault(innerCode, signalEntity[tech])  # TODO

    dict = sorted(techDict.items(), key=lambda d: d[1], reverse=True)
    # print(dict)
    planSellList2 = []
    for x in dict: planSellList2.append(x[0])
    return planSellList2

#弃用
#卖出列表中实际卖出的股票（去停牌，去一字跌停，去保留股）
#排序：Mom降序
#分成2部分
#toKeepInSellList: 需要保留的股票(包括停牌和一字跌停和为了满足当日持仓个数保留的股票)
#toSellInSellList: 要卖出的股票(剩下的)
#cannotSellList: 停牌和一字跌停不能卖出
#返回:toSellInSellList
def get_actual_sell_list(planSellList, tradingDay, signalData, dailyQuote, numOfToKeepInSellList, cannotSellList):
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
    # # sortedSellDf = sortedSellDf.groupby(level=0).apply(setMom,tradingDay,signalData)#tradingDay,signalData
    # # print(sortedSellDf)
    #
    # for index, row in sortedSellDf.iterrows():
    #     innerCode = index
    #     signalEntity = SourceDataDao.selectSignalByDateAndInnerCode2(signalData, tradingDay, innerCode, StockConst.Mom)
    #     # sortedSellDf.loc[index, [StockConst.Mom]] = signalEntity[StockConst.Mom]
    #     sortedSellDf.loc[index, [StockConst.Mom]] = signalEntity

    planSellList = sort_by_tech(planSellList, signalData, tradingDay, StockConst.MOM)

    #print(sortedSellList)
    #从信号数据中获取Mom用于排序
    # for innerCode in planSellList:
    #     # signalEntity = SourceDataDao.selectSignalByDateAndInnerCode(signalData, tradingDay, innerCode)
    #     #entity = signalData.ix[(tradingDay, innerCode)]
    #     sortedSellDf.loc[(sortedSellDf[StockConst.InnerCode] == innerCode), [StockConst.Mom]] = 1 # signalEntity[StockConst.Mom]

    # sortedSellDf = signalData[(signalData.index.get_level_values(0) == tradingDay) & (signalData.index.get_level_values(1).isin(planSellList))]

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
        isCannotSell = SourceDataDao.check_if_cannot_sell(dailyQuote, tradingDay, innerCode)
        # isCannotSell = False
        #except:
             #print('getToSellInSellList '+DateUtil.datetime2Str(tradingDay)+' '+str(innerCode))
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
def handle_buy_list(tradingDay, dailyQuote, stockTradeList, currHoldSet, capitalEntity, actualBuyListMV):
    usableCash = capitalEntity.get_usable_cash()
    if usableCash == 0:
        return

    if len(actualBuyListMV) == 0:
        return

    # buyCash = usableCash/len(actualBuyList)

    #print('vol:'+vol)
    #partChangePCT = 0
    # buyList全部可以买入
    for actualDict in actualBuyListMV:
        innerCode = actualDict.get(StockConst.INNERCODE)
        buyCash = actualDict.get('MV')  # 实际买入现金
        buyPrice = actualDict.get('price')  # 实际买入价格
        isAdjust = actualDict.get('isAdjust')
        partialFlg = actualDict.get('partialFlg')  # 实际是否部分买入



        # dailyQuoteRow = SourceDataDao.selectByInnerCodeAndDate(dailyQuote,tradingDay,innerCode)
        #print('innerCode:'+str(innerCode))
        #print(dailyQuoteRow)
        #可买
        #if buyFlg != -1:
        #平均买入价（没有算佣金）
        # buyPrice = BackTestHelper.getVWap(dailyQuoteRow)
        #成本价（算佣金）
        cost = buyPrice*(1 + StockConst.BUY_COMMISSION / 100)
        #仓位（股）
        #vol = NumUtil.getRound(turnover/cost,StockConst.volScale)
        #佣金（元）
        commission = BackTestHelper.get_buy_commission(buyCash, StockConst.BUY_COMMISSION / 100)
        #买入市值
        buyMV = buyCash - commission
        #更新可用金额(减少)
        capitalEntity.reduce_usable_cash(buyCash)
        #changePCT = NumUtil.getChangePCT(cost, closePrice, 2)
        #realChangePCT = (changePCT - StockConst.buyCommission) * vol / 100.0
        #partChangePCT = partChangePCT + realChangePCT
        #
        #stockHold = StockHoldEntity.StockHoldEntity(tradingDay,innerCode,vol)
        #stockTrade = StockTradeEntity.StockTradeEntity(tradingDay, innerCode, 1, vol, cost, '', '')
        dateStr = DateUtil.datetime2_str(tradingDay)
        stockTradeDict = {'tradingDay':dateStr,'innerCode':innerCode,'type':1,
                          'price':buyPrice,'buyMV':buyMV,'sellMV':'','commission': commission,
                          'sellCash':'','buyCash':buyCash,'openDate':'','isAdjust':isAdjust,'partialFlg':partialFlg}
        stockTradeList.append(stockTradeDict)




        # #非调整买入
        # if partialFlg is None:
        if isAdjust is None:
            # 插入表
            # 当前持仓: a_innerCode,a_lastTradePrice,a_cost,a_openDate,a_lastTradeMV,a_originBuyPrice,a_originBuyMV,a_closePrice,a_closeMV
            stockHoldEntity = StockHoldEntity.StockHoldEntity(innerCode, buyPrice, cost,
                                                              DateUtil.datetime2_str(tradingDay), buyMV,
                                                              buyPrice, buyMV, None, None, None)
            currHoldSet.setdefault(innerCode, stockHoldEntity)
        # 部分买入 且是调整买入（更新持仓）
        # elif (partialFlg == 1) & (isAdjust == 1):
        elif isAdjust == 1:
            stockHoldEntity = currHoldSet.get(innerCode)
            # 当前市值
            currMV = BackTestHelper.get_sell_mv(stockHoldEntity.closePrice, stockHoldEntity.closeMV, buyPrice)
            # 当前市值=当前市值+买入市值
            currMV = currMV + buyMV
            # 更新持仓信息
            stockHoldEntity.set_last_trade_price(buyPrice)
            stockHoldEntity.set_last_trade_mv(currMV)
            stockHoldEntity.cost = cost
            stockHoldEntity.set_change_date(tradingDay)

        """
        if (DateUtil.datetime2Str(tradingDay) == '2014-12-08') | (DateUtil.datetime2Str(tradingDay) == '2014-12-09'):
            print('-----handleBuyList-----')
            print(DateUtil.datetime2Str(tradingDay))
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
def handle_sell_list(tradingDay, dailyQuote, stockTradeList, currHoldSet, capitalEntity, actualSellListMV):
    #partChangePCT = 0
    dateStr = DateUtil.datetime2_str(tradingDay)

    if len(actualSellListMV) == 0:
        return

    #sellList全部可以卖出
    for actualDict in actualSellListMV:
        innerCode = actualDict.get(StockConst.INNERCODE)
        sellMV = actualDict.get('MV') #实际卖出市值
        sellPrice = actualDict.get('price') #实际卖出价格
        isAdjust = actualDict.get('isAdjust')
        partialFlg = actualDict.get('partialFlg') #实际是否部分卖出

        #print('innerCode:' + str(innerCode))
        #try:
        # dailyQuoteRow = SourceDataDao.selectByInnerCodeAndDate(dailyQuote, tradingDay, innerCode)
        #except:
            #退市的股票: 查询不到行情,取最后一个交易日
            #dailyQuoteRow = SourceDataDao.selectByLastDay(dailyQuote,innerCode)
        # print(dailyQuoteSingle)

        #可卖
        #if sellFlg != -1:
        #actualSellList.append(innerCode)

        #全部卖出
        if partialFlg is None:
            stockHoldEntity = currHoldSet.pop(innerCode)
        #部分卖出（更新持仓）
        elif partialFlg == 1:
            stockHoldEntity = currHoldSet.get(innerCode)
            #当前市值
            currMV = BackTestHelper.get_sell_mv(stockHoldEntity.closePrice, stockHoldEntity.closeMV, sellPrice) #stockHoldEntity.buyPrice, stockHoldEntity.buyMV
            #卖掉部分后的市值
            currMV = currMV - sellMV
            #更新持仓(价格，仓位，变更日)
            stockHoldEntity.set_last_trade_price(sellPrice)
            stockHoldEntity.set_last_trade_mv(currMV)
            stockHoldEntity.set_change_date(tradingDay)

        #vol = stockHoldEntity.vol
        # sellPrice = BackTestHelper.getVWap(dailyQuoteRow)
        #卖出市值（没有扣佣金）
        #turnover = sellPrice * vol
        # sellMV = BackTestHelper.getSellMV(stockHoldEntity.buyPrice, stockHoldEntity.buyMV, sellPrice)
        #佣金（元）
        commission = BackTestHelper.get_sell_commission(sellMV, StockConst.SELL_COMMISSION / 100)
        #卖出后所得资金(扣掉佣金后所得金额)
        sellCash = sellMV - commission
        # 更新可用金额(增加)
        capitalEntity.increase_usable_cash(sellCash)
        # 开仓日
        openDate = stockHoldEntity.openDate
        # 加入交易表
        stockTradeDict = {'tradingDay': dateStr, 'innerCode': innerCode, 'type': -1, 'price': sellPrice,
                          'buyMV': '', 'sellMV': sellMV, 'commission': commission,
                          'sellCash': sellCash,'buyCash':'','openDate':openDate,'isAdjust':isAdjust,'partialFlg':partialFlg}
        stockTradeList.append(stockTradeDict)


#今日选股和昨日选股的差集
#currSelectStock: dataFrame
#currHoldSet: dict
#return: innerCode list
#currList - lastList
def get_difference(currSelectStock, currHoldSet, typ):
    currList = []
    lastList = []

    if len(currSelectStock) != 0:
        #for index, row in currSelectStock.iterrows():
            #currList.append(index[1])
        # currList = list(currSelectStock.index.get_level_values(1))
        currList = list(currSelectStock.index)

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
#currSelectStock: dataFrame
#currHoldSet: dict
#return: innerCode list
#currList 交集 lastList
def get_intersection(currSelectStock, currHoldSet):
    currList = []
    lastList = []

    if len(currSelectStock) != 0:
        #for index, row in currSelectStock.iterrows():
            #currList.append(index[1])
        # currList = list(currSelectStock.index.get_level_values(1))
        currList = list(currSelectStock.index)

    if len(currHoldSet) != 0:
        #for innerCode in currHoldSet:
            #lastList.append(innerCode)
        lastList = list(currHoldSet.keys())
        lastList.sort()

    returnList = SetUtil.intersection(currList, lastList)
    return returnList

#买入列表（改成全部当日选股）
def get_plan_buy_list(currSelectStock, currHoldSet):
    # return get_difference(currSelectStock, currHoldSet, 1)

    currList = []
    if len(currSelectStock) != 0:
        currList = list(currSelectStock.index)
    return currList

#卖出列表（改成全部昨日持仓）
def get_plan_sell_list(currSelectStock, currHoldSet):
    # return get_difference(currSelectStock, currHoldSet, -1)

    lastList = []
    if len(currHoldSet) != 0:
        lastList = list(currHoldSet.keys())
        lastList.sort()
    return lastList

#昨日持有列表
def get_prev_hold_list(currSelectStock, currHoldSet):
    return get_intersection(currSelectStock, currHoldSet)

#计算当日总市值:股票市值+可用资金
#closePrice mv放入持仓表
def calculate_daily_mv(currHoldSet, capitalEntity, dailyQuote, tradingDay, stockHoldDailyList, initialCash):
    usableCash = capitalEntity.get_usable_cash()
    stockMV = 0
    for innerCode in currHoldSet:
        #try:
        dailyQuoteRow = SourceDataDao.select_by_inner_code_and_date(dailyQuote, tradingDay, innerCode)
        #except:
            #缺少数据,取最近一个交易日的数据
            #dailyQuoteRow = SourceDataDao.selectByPrevTradingDay(dailyQuote, tradingDay, innerCode)
            #print('calculateDailyMV '+DateUtil.datetime2Str(tradingDay)+' '+str(innerCode))

        stockHoldEntity = currHoldSet[innerCode]
        #vol = stockHoldEntity.vol
        # print('innerCode:' + str(innerCode))
        closePrice = BackTestHelper.get_close_price(dailyQuoteRow)
        #mv = vol * closePrice
        #收盘市值
        closeMV = BackTestHelper.get_sell_mv(stockHoldEntity.lastTradePrice, stockHoldEntity.lastTradeMV, closePrice) #stockHoldEntity.buyPrice, stockHoldEntity.buyMV
        #
        stockHoldEntity.set_close_price(closePrice)
        stockHoldEntity.set_close_mv(closeMV)
        #每日市值
        stockMV += closeMV
        #该股收益(已扣佣金)(仅用于查看) TODO(部分卖出时的算法)
        profit = (closeMV - stockHoldEntity.lastTradeMV) * (1 - StockConst.BUY_COMMISSION / 100)

        holdDict = {'tradingDay': tradingDay,
                'innerCode': innerCode,
                'lastTradePrice': stockHoldEntity.lastTradePrice,
                'lastTradeMV': stockHoldEntity.lastTradeMV,
                'cost': stockHoldEntity.cost,
                'closePrice': closePrice,
                'closeMV': closeMV,
                'profit': profit,
                'openDate': stockHoldEntity.openDate,
                'profitPCT': NumUtil.get_round(profit / initialCash * 100, 5),
                'changeDate': stockHoldEntity.changeDate
        }

        stockHoldDailyList.append(holdDict)
    #print('dailyMV:' + str(dailyMV))
    #print('usableCash:' + str(usableCash))

    #总资产=股票市值+现金
    totalAsset = stockMV + usableCash
    capitalEntity.set_total_asset(totalAsset)
    #股票市值
    capitalEntity.set_stock_mv(stockMV)
    # return dailyMV

#主程序
# @TimeUtil.checkConsumedTime6
def main(read_func,select_stock_func,trade_func,techList,sliceDict,signalDataAddr = '', dailyQuoteAddr = '', indexQuoteAddr='', benchmark='',
         startDate = '2004-01-01', endDate = '2005-12-31', doPlot=True, databaseDict=None, signalColumnDict=None):
    start = time.clock()

    # signalData = SourceDataDao.loadSignalData(signalDataAddr)
    # dailyQuote = SourceDataDao.loadNewDailyQuote(dailyQuoteAddr)
    # indexQuote = SourceDataDao.loadH5(indexQuoteAddr) #StockConst.root + StockConst.fakeIndexQuoteH5

    # signalData = SourceDataDao.read_file_set_index(signalDataAddr)
    signalData = read_func(signalDataAddr, databaseDict, signalColumnDict)

    dailyQuote = SourceDataDao.read_file(dailyQuoteAddr) #read_file_set_index
    indexQuote = SourceDataDao.read_file(indexQuoteAddr) #read_file_set_index

    if signalDataAddr is not None:
        maxSignalDate = SourceDataDao.get_max_date(signalDataAddr,signalColumnDict)
        minSignalDate = SourceDataDao.get_min_date(signalDataAddr,signalColumnDict)
    else:
        maxSignalDate = SignalDataMSSQLDao.select_max_data(databaseDict,signalColumnDict)
        minSignalDate = SignalDataMSSQLDao.select_min_data(databaseDict,signalColumnDict)
        # print('print')
        # print(maxSignalDate)
        # print(minSignalDate)

    maxDailyQuoteDate = SourceDataDao.get_max_date(dailyQuoteAddr,None)
    minDailyQuoteDate = SourceDataDao.get_min_date(dailyQuoteAddr,None)

    maxIndexQuoteDate = SourceDataDao.get_max_date(indexQuoteAddr,None)
    minIndexQuoteDate = SourceDataDao.get_min_date(indexQuoteAddr,None)

    # print('minSignalDate:' + minSignalDate)
    # print('maxSignalDate:' + maxSignalDate)
    #
    # print('minDailyQuoteDate:' + minDailyQuoteDate)
    # print('maxDailyQuoteDate:' + maxDailyQuoteDate)
    #
    # print('minIndexQuoteDate:' + minIndexQuoteDate)
    # print('maxIndexQuoteDate:' + maxIndexQuoteDate)

    #
    if minSignalDate < minDailyQuoteDate:
        startDate = minDailyQuoteDate
    else:
        startDate = minSignalDate

    if maxSignalDate > maxDailyQuoteDate:
        endDate = maxDailyQuoteDate
    else:
        endDate = maxSignalDate

    #
    if startDate < minIndexQuoteDate:
        startDate = minIndexQuoteDate
    else:
        pass

    if endDate > maxIndexQuoteDate:
        endDate = maxIndexQuoteDate
    else:
        pass


    print('startDate:'+startDate)
    print('endDate:' + endDate)

    #TODO 暂时不需要
    # dailyQuotePn = SourceDataDao.loadNewDailyQuoteToPn(dailyQuoteAddr)
    dailyQuotePn = None

    #参数
    #初始资金
    initialCash = 1000000 #1000000

    #选股结果（外部传入）
    #select top 5 group by TradingDay order by Mom desc
    allSelectStock = select_stock_func(signalData,techList,sliceDict)
    print('allSelectStock:'+str(len(allSelectStock)))
    # print(allSelectStock)
    if len(allSelectStock) == 0:
        return

    #当前持仓
    currHoldSet = {}
    #资金情况
    capitalEntity = CapitalEntity.CapitalEntity(initialCash, 0, initialCash)
    lastCapitalEntity = copy.copy(capitalEntity)
    #初始化每日统计表
    stockStatDailyDf = pd.DataFrame(index=pd.date_range(startDate, endDate),
                columns=['netValue','changePCT','buyCnt','sellCnt','prevHoldCnt','currHoldCnt','cannotSellCnt','cannotBuyCnt',
                         'usableCash','totalAsset','indexChangePCT','relativeChangePCT','relativeNetValue'])
    #初始化每日持仓表
    stockHoldDailyList = []
    stockTradeList = []
    actualBuyListAll = []
    actualSellListAll = []

    #从信号表中取得唯一性日期
    dateList = SourceDataDao.select_date_from_signal(dailyQuote, startDate, endDate) #signalData dailyQuote
    # print(dateList)

    # lastTradingDay = None
    # lastTradingDayStr = None
    lastRelativeNetValue = 1 #昨日相对净值

    start_loop = time.clock()
    for index, item in enumerate(dateList):
    #for date in dateList:
        #print('index:'+str(index)+' len:'+str(len(dateList)))
        # start_inloop0 = time.clock()

        #信号日
        signalDay = dateList[index]
        # 非最后一天
        if index < (len(dateList) - 1):
            #交易日
            tradingDay = dateList[index + 1]
            tradingDayStr = DateUtil.datetime2_str(tradingDay)
            # tradingDayTsp = pd.Timestamp(tradingDayStr)
            # print(tradingDay)
            # print(tradingDayStr)
            # print(tradingDayTsp)
            # print(type(tradingDay))
            # print(type(tradingDayStr))
            # print(type(tradingDayTsp))
            #print('dateStr:'+dateStr)
        # 最后一天
        else:
            break

        # dailyQuote1day = dailyQuote[dailyQuote.index.get_level_values(0) == tradingDay]

        #TODO
        # start_slice = time.clock()
        # print(str(len(dailyQuote)))
        # print(type(tradingDay))

        #交易日行情
        dailyQuote1day = dailyQuote.xs(tradingDay)
        # print('dailyQuote1day:'+str(len(dailyQuote1day)))
        # end_slice = time.clock()
        # print("切片花费时间：%f s" % (end_slice - start_slice))
        # dailyQuote1day = None

        #print(dateStr)

        #信号日选股
        currSelectStock = allSelectStock.xs(signalDay)  #.xs(signalDay)
        # print('currSelectStock:'+str(len(currSelectStock)))



        # if StockConst.isDebug:
        # print('tradingDayStr:'+tradingDayStr+' currSignalData:'+str(len(currSignalData)))
            #print(currSignalData)

        # end_inloop0 = time.clock()
        # print("inloop0花费时间：%f s" % (end_inloop0 - start_inloop0))

        #交易方法（外部传入）
        # start_inloop1 = time.clock()
        dict = trade_func(currSelectStock, currHoldSet, dailyQuote, tradingDay, signalData, capitalEntity, dailyQuotePn, dailyQuote1day, lastCapitalEntity)
        # end_inloop1 = time.clock()
        # print("trade_func花费时间：%f s" % (end_inloop1 - start_inloop1))

        actualBuyList = dict['actualBuyList']
        actualSellList = dict['actualSellList']
        prevHoldList = dict['prevHoldList']
        cannotBuyList = dict['cannotBuyList']
        cannotSellList = dict['cannotSellList']
        stockTradeListDaily = dict['stockTradeList']
        # plan_buy_list = dict['plan_buy_list']
        # plan_sell_list = dict['plan_sell_list']

        # plan_buy_list = []


        if len(actualBuyList) > 0:
            actualBuyListAll.extend(actualBuyList)

        if len(actualSellList) > 0:
            actualSellListAll.extend(actualSellList)

        if len(stockTradeListDaily) > 0 :
            stockTradeList.extend(stockTradeListDaily)

        # print(currHoldSet)

        #3.计算当日市值
        # start_inloop2 = time.clock()
        calculate_daily_mv(currHoldSet, capitalEntity, dailyQuote, tradingDay, stockHoldDailyList, initialCash)
        totalAsset = capitalEntity.get_total_asset()

        # end_inloop2 = time.clock()
        # print("calculateDailyMV花费时间：%f s" % (end_inloop2 - start_inloop2))


        # start_inloop3 = time.clock()
        #4.个数
        buyCnt = len(actualBuyList)
        sellCnt = len(actualSellList)
        prevHoldCnt = len(prevHoldList)
        currHoldCnt = len(currHoldSet)
        cannotSellCnt = len(cannotSellList)
        cannotBuyCnt = len(cannotBuyList)

        # print(currMV)

        #if StockConst.isDebug:
            #print("dateStr:" + dateStr + " changePCTBuy:" + str(changePCTBuy) + " changePCTSell:" + str(changePCTSell) +
                  #" changePCTHold:" + str(changePCTHold))

        #当日净值
        netValue = totalAsset / initialCash
        # print("tradingDayStr:" + tradingDayStr + " netValue:" + str(netValue))
        if netValue <= 0:
            break

        #当日收益(%)
        dailyChangePCT = NumUtil.get_change_pct(lastCapitalEntity.get_total_asset(), totalAsset, 5)
        #当日可用现金
        usableCash = capitalEntity.get_usable_cash()

        # 当日的指数
        indexQuote1day = None
        indexChangePCT = 0
        if indexQuote is not None:
            indexQuote1day = indexQuote.ix[(tradingDay, benchmark)]
            indexChangePCT = indexQuote1day['ChangePCT']
        #相对收益=每日收益-指数收益 (%)
        relativeChangePCT = dailyChangePCT - indexChangePCT
        #相对净值=昨日相对净值*（1+相对收益/100）
        relativeNetValue = lastRelativeNetValue*(1+relativeChangePCT/100)

        #统计表
        stockStatDailyDf.ix[tradingDayStr] = netValue,dailyChangePCT,buyCnt,sellCnt,prevHoldCnt,currHoldCnt,cannotSellCnt,cannotBuyCnt,usableCash,totalAsset,indexChangePCT,relativeChangePCT,relativeNetValue
        #昨日资产
        lastCapitalEntity = copy.copy(capitalEntity)
        #昨日相对净值
        lastRelativeNetValue = relativeNetValue

        # lastTradingDay = tradingDay
        # lastTradingDayStr = tradingDayStr
        # end_inloop3 = time.clock()
        # print("inloop3花费时间：%f s" % (end_inloop3 - start_inloop3))


    end_loop = time.clock()
    print("for循环花费时间：%f s" % (end_loop - start_loop))

    result = ''

    start_stat = time.clock()
    # 信号数据
    #allSelectStock.to_csv(StockConst.root + '\export\allSelectStock.csv')

    #check
    if len(stockStatDailyDf) == 0:
        return None

    print('stockStatDailyDf:' + str(len(stockStatDailyDf)))


    if is_export:
        actualBuyListAllDf = pd.DataFrame(actualBuyListAll)
        # actualBuyListAllDf.sort_values(by=[StockConst.TRADINGDAY], ascending=True)
        actualBuyListAllDf.to_csv(StockConst.ROOT + '\\export\\actualBuyListAllDf.csv')

    if is_export:
        actualSellListAllDf = pd.DataFrame(actualSellListAll)
        # actualSellListAllDf.sort_values(by=[StockConst.TRADINGDAY], ascending=True)
        actualSellListAllDf.to_csv(StockConst.ROOT + '\\export\\actualSellListAllDf.csv')


    # 每日交易
    # print('每日交易:')
    # print(stockTradeList)
    if is_export:
        stockTradeDailyDf = pd.DataFrame(stockTradeList)
        # stockTradeDailyDf.sort_values(by=['tradingDay'], ascending=True)
        stockTradeDailyDf.to_csv(StockConst.ROOT + '\export\stockTradeDaily.csv')

    # 每日持仓
    #print('每日持仓:')
    if is_export:
        stockHoldDailyDf = pd.DataFrame(stockHoldDailyList)
        # stockHoldDailyDf.sort_values(by=['tradingDay'],ascending=True)
        stockHoldDailyDf.to_csv(StockConst.ROOT + '\export\stockHoldDaily.csv')

    start_stat_1 = time.clock()
    #每日统计(收益，净值，买入数，卖出数，持有数)
    stockStatDailyDf = stockStatDailyDf.dropna(how='all')
    result += '--' * 70 + '\n'
    result += '每日统计:' + '\n'
    result += stockStatDailyDf.to_string() + '\n'
    if is_export:
        stockStatDailyDf.to_csv(StockConst.ROOT + '\export\stockStatDaily.csv')
    end_stat_1 = time.clock()
    print("统计1花费时间：%f s" % (end_stat_1 - start_stat_1))

    start_stat_2 = time.clock()
    # 每年统计
    result += '--' * 70 + '\n'
    yearDf = StockYearService.main(stockStatDailyDf)
    result += '每年统计:' + '\n'
    result += yearDf.to_string() + '\n'
    end_stat_2 = time.clock()
    print("统计2花费时间：%f s" % (end_stat_2 - start_stat_2))

    start_stat_3 = time.clock()
    # 最大回撤
    result += '--' * 70 + '\n'
    maxdrop = StockMaxDropNewService.get_max_drop(stockStatDailyDf)
    result += '最大回撤:' + '\n'
    result += SetUtil.dict_to_string(maxdrop) + '\n'
    # #每年的最大回撤
    # maxdropDf = StockMaxDropNewService.getMaxDropForEachYear(stockStatDailyDf)
    # maxdropDf.sort_values(by=["year"])
    # result += '每年的最大回撤:' + '\n'
    # result += maxdropDf.to_string() + '\n'
    end_stat_3 = time.clock()
    print("统计3花费时间：%f s" % (end_stat_3 - start_stat_3))

    start_stat_4 = time.clock()
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
    end_stat_4 = time.clock()
    print("统计4花费时间：%f s" % (end_stat_4 - start_stat_4))

    end_stat = time.clock()
    print("统计花费时间：%f s" % (end_stat - start_stat))

    # result += '回测完成'
    end = time.clock()
    print("main花费时间：%f s" % (end - start))

    if doPlot:
        # 净值曲线图
        # stockStatDailyDf['netValue'].plot()
        # plt.show()
        #
        # # # 相对净值曲线图
        # stockStatDailyDf['relativeNetValue'].plot()
        # plt.show()
        pass

    #
    resultDic={
        'stockStatDailyDf': stockStatDailyDf,
        'result': result,
        'sharpRatio': sharpRatio
    }

    print(result)
    return resultDic


#sliceTotalNum: 切片数
#numOfDailySignal：每天选多少只
def processBySlice(select_stock_func,trade_func,techList,sliceTotalNum,numOfDailySignal,signalDataAddr = '', dailyQuoteAddr = '',
                   startDate = '2004-01-01', endDate = '2005-12-31', doPlot=True):
    sliceToSharpDf = pd.DataFrame({'sliceIdx':range(0, sliceTotalNum),'sharpRatio':None})
    sliceToSharpDf = sliceToSharpDf.set_index(['sliceIdx'])
    for index, row in sliceToSharpDf.iterrows():
        sliceIdx = index
        sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
        resultDic = main(select_stock_func, trade_func, techList, sliceDict, signalDataAddr, dailyQuoteAddr, startDate, endDate)

        sharpRatio = resultDic.get('sharpRatio')
        # print('sharpRatio:'+str(sharpRatio))

        sliceToSharpDf.ix[index, ['sharpRatio']] = sharpRatio

    print(sliceToSharpDf)

    if doPlot:
        # sliceToSharpDf['sharpRatio'].plot()
        # plt.show()
        pass


#选股方法1:
#按Mom倒序选前N只
#signalData: 信号数据
#numOfDailySignal：每天选股个数
@TimeUtil.check_consumed_time7
def select_stock_func1(signalData,techList,sliceDict):
    print('select_stock_func1')

    numOfDailySignal = sliceDict.get('numOfDailySignal')

    allSelectStock = signalData.groupby(level=StockConst.TRADINGDAY).apply(SelectUtil.top, numOfDailySignal, techList[0], False) #False True
    return allSelectStock

#选股方法2:
#按Mom正序选前N只
#signalData: 信号数据
#numOfDailySignal：每天选股个数
@TimeUtil.check_consumed_time7
def select_stock_func2(signalData,techList,sliceDict):
    print('select_stock_func2')

    numOfDailySignal = sliceDict.get('numOfDailySignal')

    allSelectStock = signalData.groupby(level=StockConst.TRADINGDAY).apply(SelectUtil.top, numOfDailySignal, techList[0], True) #False True
    return allSelectStock


#暂时用假数据Momp
#选股方法3:
#2因子加权重取前N
@TimeUtil.check_consumed_time7
def select_stock_func3(signalData,techList,sliceDict):
    print('select_stock_func3')

    numOfDailySignal = sliceDict.get('numOfDailySignal')

    data = {'Momp': np.random.randint(0, 101, size=len(signalData)) }
    randDf = DataFrame(data, index=signalData.index)

    signalData['Momp'] = randDf['Momp']
    allSelectStock = signalData.groupby(level=StockConst.TRADINGDAY).apply(SelectUtil.top_with_weight, numOfDailySignal, techList, False, SelectUtil.handle_na1) #False True  StockConst.Mom,'Momp'
    allSelectStock.to_csv(StockConst.ROOT + '\export\select_stock_func3.csv')
    return allSelectStock

#
#选股方法4:
@TimeUtil.check_consumed_time7
def select_stock_func4(signalData,techList,sliceDict):
    print('select_stock_func4')
    # numOfDailySignal = 4
    allSelectStock = signalData.groupby(level=StockConst.TRADINGDAY).apply(SelectUtil.top_with_slice, sliceDict, techList[0], False) #False True
    # print(allSelectStock)
    return allSelectStock

#
#选股方法5:仓位权重
@TimeUtil.check_consumed_time7
def select_stock_func5(signal_data, tech_list, slice_dict):
    print('select_stock_func5')

    num_of_daily_signal = slice_dict.get('numOfDailySignal')
    frm_gb = signal_data.groupby(level=StockConst.TRADINGDAY)

    all_select_stock = frm_gb.apply(SelectUtil.top_with_vol_weight, num_of_daily_signal, tech_list[0], False) #False True

    return all_select_stock


#交易方法1
#numOfDailySignal,
#算出实际买入和卖出的股票
def trade_func1(curr_select_stock, curr_hold_set, daily_quote, trading_day, signal_data, capital_entity, daily_quote_pn, daily_quote1day, last_capital_entity):
    # 计划买入列表
    t1 = time.time()
    plan_buy_list = get_plan_buy_list(curr_select_stock, curr_hold_set)
    # 计划卖出列表
    t2 = time.time()

    plan_sell_list = get_plan_sell_list(curr_select_stock, curr_hold_set)
    # 昨日持仓部分（在今日持仓中）
    t3 = time.time()

    prev_hold_list = get_prev_hold_list(curr_select_stock, curr_hold_set)
    # dailyChangePCT = 0
    t4 = time.time()

    cannot_sell_list = []
    cannot_buy_list = []

    #计算计划买入卖出仓位（去掉停牌）
    plan_buy_list_mv = get_plan_buy_list_mv(plan_buy_list, daily_quote, trading_day, cannot_buy_list, daily_quote_pn, daily_quote1day, last_capital_entity, curr_select_stock, prev_hold_list, curr_hold_set)
    t5 = time.time()
    plan_sell_list_mv = get_plan_sell_list_mv(plan_sell_list, trading_day, signal_data, daily_quote, cannot_sell_list, daily_quote1day, curr_hold_set, prev_hold_list, curr_select_stock, last_capital_entity)
    t6 = time.time()
    force_sell_list_mv = get_force_sell_list_mv(prev_hold_list, trading_day, signal_data, daily_quote, daily_quote1day, curr_hold_set)
    t7 = time.time()

    # 计算实际买入卖出（考虑部分买入，部分卖出的情况）
    actual_buy_list = []
    actual_sell_list = []
    get_actual_buy_sell_list(plan_buy_list_mv, plan_sell_list_mv, force_sell_list_mv, actual_buy_list, actual_sell_list, capital_entity)

    # print("dateStr:" + DateUtil.datetime2_str(trading_day) + " planBuyList:" + str(len(plan_buy_list)) + " planSellList:" + str(len(plan_sell_list)) +
    #       " prevHoldList:" + str(len(prev_hold_list)) + " planBuyListMV:" + str(len(plan_buy_list_mv))  + " planSellListMV:" + str(len(plan_sell_list_mv))  +
    #       " forceSellListMV:" + str(len(force_sell_list_mv))  +
    #       " actualBuyList:" + str(len(actual_buy_list)) + " actualSellList:" + str(len(actual_sell_list)) +
    #       " cannot_buy_list:" + str(len(cannot_buy_list)) + " cannot_sell_list:" + str(len(cannot_sell_list)) +
    #       " usableCash:" + str(capital_entity.get_usable_cash()) + " stockMV:" + str(capital_entity.get_stock_mv()) + " totalAsset:" + str(capital_entity.get_total_asset())
    # )


    # # 实际买入列表
    # actualBuyList = getActualBuyList(planBuyList, dailyQuote, tradingDay, cannotBuyList, dailyQuotePn, dailyQuote1day)
    # t5 = time.time()
    #
    # # "卖出列表"中要保留的股票数
    # numOfToKeepInSellList = len(cannotBuyList)
    # t6 = time.time()
    #
    # # 实际卖出列表
    # actualSellList = getActualSellList(planSellList, tradingDay, signalData, dailyQuote, numOfToKeepInSellList, cannotSellList)



    stock_trade_list = []
    t8 = time.time()

    # 1.处理实际卖出
    handle_sell_list(trading_day, daily_quote, stock_trade_list, curr_hold_set, capital_entity, actual_sell_list)
    t9 = time.time()

    # 2.处理实际买入
    handle_buy_list(trading_day, daily_quote, stock_trade_list, curr_hold_set, capital_entity, actual_buy_list)
    t10 = time.time()


    # print(stockTradeList)

    #
    dict = {'actualBuyList':actual_buy_list,'actualSellList':actual_sell_list,'prevHoldList':prev_hold_list,
            'cannotBuyList':cannot_buy_list,'cannotSellList':cannot_sell_list,'stockTradeList':stock_trade_list,
            'plan_buy_list': plan_buy_list, 'plan_sell_list': plan_sell_list,
            'plan_buy_list_mv': plan_buy_list_mv, 'plan_sell_list_mv': plan_sell_list_mv
            }
    t11 = time.time()

    # if StockConst.isDebug:
    # import numpy as np
    # print(np.array([t2,t3,t4,t5,t6,t7,t8,t9,t10,t11] - np.array([t1,t2,t3,t4,t5,t6,t7,t8,t9,t10] )))

    return dict

def read_func1(signalDataAddr, databaseDict, signalColumnDict):
    if signalDataAddr is not None:
        signalData = SourceDataDao.read_file_set_index(signalDataAddr, signalColumnDict)
    elif databaseDict is not None:
        signalData = SignalDataMSSQLDao.select_signal_data(databaseDict, signalColumnDict)
    else:
        raise ValueError('signal data address and table name is unknown!')
    # print('signalData')
    # print(signalData)
    return signalData

# df = read_func1(StockConst.ROOT + '/Data.xls', None)
# df = read_func1(None, 'SignalDataTable')
# print(df)


def test1(arg1,reta):
    print('test1:' + arg1)
    print(reta)
    return '11111111'

def test2(arg2,retb):
    print('test2:' + arg2)
    print(retb)
    return '22222222'

def test3(args3,retc):
    print('test3:' + args3)
    print(retc)
    return '33333333'


