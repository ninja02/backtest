
"""
def selectByMonth(dailyQuote,year,month):
    monthStr = str(year) + '-' + addZero(month)
    dailyQuote2 = dailyQuote.ix[monthStr]
    return dailyQuote2
"""

"""
#'2016-01-01':'2016-01-31'
#用信号数据取得唯一性日期
#去重,筛选,取得索引
#返回:列表
def selectDateFromSignalOld(signalData,startDate='',endDate=''):
    #print(dailyQuote.count(level='TradingDay'))
    #按日期分组求每日总数
    df = signalData.groupby(level=StockConst.TradingDay).size()
    if startDate:
        if endDate:
            df = df.ix[startDate:endDate]
    #else:

    #取得唯一性日期
    ss=list(df.index)
    #print(ss)
    return ss

#'2016-01-01':'2016-01-31'
#用信号数据取得唯一性日期
#取得索引,去重,筛选
#返回:列表
def selectDateFromSignalOld2(signalData,startDate='',endDate=''):
    # 取得索引,去重
    #l2 = getIndexAndDistinct(signalData)
    l2 = list(signalData.index.get_level_values(StockConst.TradingDay).unique())
    # 筛选
    if startDate:
        if endDate:
            l2 = [x for x in l2 if (DateUtil.datetime2Str(x) >= startDate) & (DateUtil.datetime2Str(x) <= endDate)]
    return l2
"""

"""
#取得索引,去重
#signalData: dataFrame
#return:list
def getIndexAndDistinct(signalData):
    #可以用索引名称,也可以用序号
    ss = signalData.index.get_level_values('TradingDay').unique()  # 日期索引 TradingDay InnerCode
    #ss = signalData.index.levels[0] # 不能用，有问题
    l2 = list(ss)
    #print(l2)
    #l2.sort()  # 排序后的日期索引
    return l2
"""


"""
#弃用
#新增buyFlg: 1代表不可买
#新增sellFlg: -1代表不可卖
def addBuySellFlgOld(dailyQuoteParam):
    dailyQuote = dailyQuoteParam.copy()
    #dailyQuote = loadDailyQuote()
    #插入新列
    dailyQuote.insert(8, StockConst.buyFlg, Series())
    dailyQuote.insert(9, StockConst.sellFlg, Series())
    for index,row in dailyQuote.iterrows():
        prevClosePrice = row[StockConst.PrevClosePrice]
        highPrice = row[StockConst.HighPrice]
        lowPrice = row[StockConst.LowPrice]
        closePrice = row[StockConst.ClosePrice]
        turnoverValue = row[StockConst.TurnoverValue]

        isYiZiDieTing = BackTestHelper.isYiZiDieTing(highPrice, lowPrice, prevClosePrice)
        isYiZiZhangTing = BackTestHelper.isYiZiZhangTing(highPrice, lowPrice, prevClosePrice)
        isStop = BackTestHelper.isStop(closePrice, turnoverValue)


        if(isYiZiZhangTing | isStop):
            dailyQuote.ix[index, [StockConst.buyFlg]] = -1

        if (isYiZiDieTing | isStop):
            dailyQuote.ix[index, [StockConst.sellFlg]] = -1

    #print(dailyQuote)
"""

"""
def addZero(val):
    if(val < 10):
        return '0'+str(val)
    else:
        return str(val)
"""


"""
#test
def select_stock_func3(signalData):
    numOfDailySignal = 5
    signalData['Momp'] = signalData['Mom']
    groupedSignalData = signalData.groupby(level=StockConst.TradingDay).apply(SelectUtil.weightTop,numOfDailySignal,StockConst.Mom,'Momp',False) #False True
    groupedSignalData.to_csv(StockConst.root + '\export\select_stock_func3.csv')
    return groupedSignalData

signalData = loadSignalData()
signalData = selectSignalByDate(signalData,'2004-01-01','2004-01-10')
select_stock_func3(signalData)
"""

"""
signalData = loadSignalData()
#ss = signalData.index.levels[0]
ss = signalData.index.get_level_values('TradingDay').unique()
l2 = list(ss)
l2 = [x for x in l2 if (DateUtil.datetime2Str(x) >= '2016-01-01') & (DateUtil.datetime2Str(x) <= '2016-01-31')]
print(l2)
#l2 = selectDateFromSignal(signalData,'2016-01-01','2016-01-31') #
#print(l2)
"""

