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
import os

@TimeUtil.check_consumed_time4
def read_file(fp):
    print('read_file:' + fp)
    # print(fp)
    base_name = os.path.basename(fp)
    # print(base_name)
    [tbl_name, suffix] = base_name.split('.')
    # print(tbl_name)
    # print(suffix)
    if suffix in ('h5','hdf'):
        # print('is h5')
        data = pd.read_hdf(fp)
    elif suffix == 'csv':
        data = pd.read_csv(fp,encoding = 'gbk')
    elif suffix == 'xlsx':
        data = pd.read_excel(fp)
    else:
        raise ValueError('%s is unknown!'%suffix)
    if len(data) == 0:
        raise ValueError('%s has not data!'%fp)
    return data

#更新csv的日期的类型,转成datetime类型，格式必须是%Y/%m/%d
def upd_row_for_tradingday(row,field):
    row[field] = DateUtil.str2_datetime_format(row[field], '%Y/%m/%d')
    return row

@TimeUtil.check_consumed_time8
def read_file_set_index(fp,signalColumnDict):
    print('read_file_set_index:' + fp)

    tradingDayName = signalColumnDict.get(StockConst.TRADING_DAY_NAME)
    windCodeName = signalColumnDict.get(StockConst.WIND_CODE_NAME)
    techName = signalColumnDict.get(StockConst.TECH_NAME)

    # print(fp)
    base_name = os.path.basename(fp)
    # print(base_name)
    [tbl_name, suffix] = base_name.split('.')
    # print(tbl_name)
    # print(suffix)
    if suffix in ('h5','hdf'):
        # print('is h5')
        data = pd.read_hdf(fp)
    elif suffix == 'csv':
        print('is csv')

        data = read_csv(fp, signalColumnDict)
        # 选择某几列
        # print(data)
        data = data[[StockConst.TRADINGDAY, StockConst.INNERCODE, techName]]
        # print(data)

        data = data.apply(upd_row_for_tradingday, field=StockConst.TRADINGDAY, axis=1)

        # print(data)
        #设置索引
        data = data.set_index([StockConst.TRADINGDAY, StockConst.INNERCODE])
    # elif suffix == 'xlsx':
    elif suffix in ('xlsx', 'xls'):
        print('is '+suffix)

        data = read_excel(fp, signalColumnDict)
        # 选择某几列
        # print(data)
        data = data[[StockConst.TRADINGDAY, StockConst.INNERCODE, techName]]
        # print(data)

        #设置索引
        data = data.set_index([StockConst.TRADINGDAY, StockConst.INNERCODE])
    else:
        raise ValueError('%s is unknown!'%suffix)
    if len(data) == 0:
        raise ValueError('%s has not data!'%fp)
    return data

def get_max_date(fp,signalColumnDict):
    return get_specific_line_date(fp,-1,signalColumnDict)

def get_min_date(fp,signalColumnDict):
    return get_specific_line_date(fp,0,signalColumnDict)



#读csv，且指定日期和代码字段，所以要改成TRADINGDAY,INNERCODE
def read_csv(fp,signalColumnDict):
    tradingDayName = signalColumnDict.get(StockConst.TRADING_DAY_NAME)
    windCodeName = signalColumnDict.get(StockConst.WIND_CODE_NAME)
    # techName = signalColumnDict.get(StockConst.TECH_NAME)
    signalData = pd.read_csv(fp, encoding='gbk')
    # 改名
    signalData.rename(columns={tradingDayName: StockConst.TRADINGDAY, windCodeName: StockConst.INNERCODE}, inplace=True)
    return signalData

#读excel，且指定日期和代码字段，所以要改成TRADINGDAY,INNERCODE
def read_excel(fp,signalColumnDict):
    tradingDayName = signalColumnDict.get(StockConst.TRADING_DAY_NAME)
    windCodeName = signalColumnDict.get(StockConst.WIND_CODE_NAME)
    # techName = signalColumnDict.get(StockConst.TECH_NAME)
    signalData = pd.read_excel(fp)
    # 改名
    signalData.rename(columns={tradingDayName: StockConst.TRADINGDAY, windCodeName: StockConst.INNERCODE}, inplace=True)
    return signalData

#TODO 没有数据的时候
def get_specific_line_date(fp, idx, signalColumnDict):
    print('getSpecificLineDate:' + fp)
    # print(fp)
    base_name = os.path.basename(fp)
    # print(base_name)
    [tbl_name, suffix] = base_name.split('.')
    # print(tbl_name)
    # print(suffix)
    if suffix in ('h5', 'hdf'):
        # print('is h5')
        if idx == 0:
            lastRecord = get_first_record_from_h5(fp)
            return DateUtil.datetime2_str(lastRecord.index[0][0])
        elif idx == -1:
            lastRecord = get_last_record_from_h5(fp)
            return DateUtil.datetime2_str(lastRecord.index[0][0])
        # lastRecord
    elif suffix == 'csv':
        print('is csv')
        signalData = read_csv(fp, signalColumnDict)
        dateList = list(signalData[StockConst.TRADINGDAY])
        return DateUtil.datetime2_str(DateUtil.str2_datetime_format(dateList[idx], '%Y/%m/%d'))
    # elif suffix == 'xlsx':
    elif suffix in ('xlsx', 'xls'):
        print('is ' + suffix)
        signalData = read_excel(fp, signalColumnDict)
        dateList = list(signalData[StockConst.TRADINGDAY])
        return DateUtil.datetime2_str_format(dateList[idx], '%Y-%m-%d')
    else:
        raise ValueError('%s is unknown!' % suffix)
    # if len(data) == 0:
    #     raise ValueError('%s has not data!' % fp)
    # return data

##################################################################
#读csv的列名
def read_csv_column(fp):
    signalData = pd.read_csv(fp, encoding='gbk')
    columnList = signalData.columns.tolist()
    return columnList

#读excel的列名
def read_excel_column(fp):
    signalData = pd.read_excel(fp)
    columnList = signalData.columns.tolist()
    return columnList

#获取列名，用于前端上传excel文件后显示列名
def get_file_columns(fp):
    print('get_columns:' + fp)
    # print(fp)
    base_name = os.path.basename(fp)
    # print(base_name)
    [tbl_name, suffix] = base_name.split('.')

    if suffix in ('h5', 'hdf'):
        # return get_colums_from_h5(fp)
        return get_colums_include_index_from_h5(fp)
    elif suffix == 'csv':
        print('is ' + suffix)
        return read_csv_column(fp)
        # signalData = pd.read_csv(fp, encoding='gbk')
    elif suffix in ('xlsx', 'xls'):
        print('is ' + suffix)
        return read_excel_column(fp)
        # signalData = pd.read_excel(fp)
    else:
        raise ValueError('%s is unknown!' % suffix)
##################################################################



#获取信号数据
#Mom_5_D.h5:
#    index: TradingDay InnerCode
#    columns: Mom
#Mom_5_0302.h5:
#    TradingDay,WindCode,Mom
#load_signal_data
@TimeUtil.check_consumed_time4
def load_signal_data(signalDataAddr=''):
    if signalDataAddr == '':
        # signalDataAddr = (StockConst.root + StockConst.signalDataH5)
        return None
    print('loadSignalData:'+signalDataAddr)
    #Mom_5_D.h5
    method = 1
    if method == 1:
        store = pd.HDFStore(signalDataAddr)
        #print(store)
        signalData = store.select('Data'
            #[
            # Term('InnerCode', '=', 3),
            # Term('TradingDay', '>=', startDate),
            # Term('TradingDay', '<=', endDate),
            #Term('columns', '=', 'Mom')
            #]
        )
        store.close()
    elif method == 2:
        signalData = pd.read_hdf(signalDataAddr)
    #print(signalData.columns)
    #print(signalData)
    return signalData



# def loadSignalDataToPn(signalDataAddr=''):
#     print('loadSignalDataToPn')
#     if signalDataAddr == '':
#         # signalDataAddr = (StockConst.root + StockConst.signalDataH5)
#         return None
#     print(signalDataAddr)
#
#     a = pd.read_hdf(signalDataAddr)
#     pn = a.to_panel()
#     return pn





# def loadSignalDataToDic(signalDataAddr=''):
#     signalData = loadSignalData(signalDataAddr)
#     tradingDayDic={}
#     for index, row in signalData.iterrows():
#         tradingDay = index[0]
#         innerCode = index[1]
#         tradingDayStr = DateUtil.datetime2Str(tradingDay)
#         if tradingDayStr not in tradingDayDic:
#             innerCodeDic={}
#             tradingDayDic.setdefault(tradingDayStr,innerCodeDic)
#         else:
#             innerCodeDic = tradingDayDic.get(tradingDayStr)
#         innerCodeDic.setdefault(innerCode,row)
#
#     return tradingDayDic

# dict = loadSignalDataToDic()
# print(dict.get('2004-01-12'))


@TimeUtil.check_consumed_time3
def load_signal_data_by_date(startDate, endDate, addr=''):
    print('loadSignalDataByDate')
    if addr == '':
        # addr = StockConst.root + StockConst.signalDataH5
        return None
    #Mom_5_D.h5
    store = pd.HDFStore(addr)
    #print(store)
    t1 = pd.Timestamp(startDate)
    t2 = pd.Timestamp(endDate)
    signalData = store.select('Data',
        where = [
                'TradingDay>=Timestamp("'+startDate+'")',
                'TradingDay<=Timestamp("'+endDate+'")'
                ]
        # [
        # # Term('InnerCode', '=', 3),
        # # Term('TradingDay', '>=', startDate),
        # # Term('TradingDay', '<=', endDate)
        # pd.Term('Mom', '>=', '5')
        # ]
    );
    store.close()
    #print(signalData.columns)
    #print(signalData)
    return signalData

#直接从h5文件取得列名
def get_colums_from_h5(addr):
    store = pd.HDFStore(addr)
    c = store.select(key = 'Data', stop = 0)
    # print(c)
    # print(c.columns.tolist())
    store.close()
    return c.columns.tolist()

def get_colums_include_index_from_h5(addr):
    store = pd.HDFStore(addr)
    c = store.select(key = 'Data')
    # print(c)
    # print(c.columns.tolist())
    store.close()

    column2=c.columns.tolist()

    column1=c.index.names

    # print(column2)
    # print(column1)

    ret = []
    ret.extend(column1)
    ret.extend(column2)
    return ret

#最后1条记录
def get_last_record_from_h5(addr):
    store = pd.HDFStore(addr)
    c = store.select(key = 'Data', start = -1)
    store.close()
    return c
    # return c.index[0][0]
    # print(c)
    # print(c.columns.tolist())
    # return c.columns.tolist()

#第1条记录
def get_first_record_from_h5(addr):
    store = pd.HDFStore(addr)
    c = store.select(key = 'Data', stop = 1)
    store.close()
    return c

#获取行情数据
#DailyQuote_Mi.h5
#    index: TradingDay InnerCode
#    columns:
#    'PrevClosePrice', 'OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice',
#    'TurnoverVolume', 'TurnoverValue', 'TurnoverDeals'
#BRPrice_0302.h5:
#    TradingDay,WindCode,DlyRet,VWAP,TurnoverVolume,Adj,CumAdj,BROpenPrice,BRHighPrice,BRLowPrice,BRClosePrice
@TimeUtil.check_consumed_time4
def load_daily_quote(addr=''):
    print('loadDailyQuote')
    if addr == '':
        # addr = StockConst.root + StockConst.dailyQuoteH5
        return None
    #DailyQuote_Mi.h5
    store = pd.HDFStore(addr)
    dailyQuote = store.select('Data')
    #print(store)
    #print(dailyQuote.columns)
    #print(dailyQuote)
    store.close()
    return dailyQuote

def load_h5(addr):
    print('loadH5')
    if addr == '':
        return None
    #DailyQuote_Mi.h5
    store = pd.HDFStore(addr)
    df = store.select('Data')
    store.close()
    return df



#在DailyQuote_Mi的基础上加了buyFlg和sellFlg
@TimeUtil.check_consumed_time4
def load_new_daily_quote(addr=''):
    print('loadNewDailyQuote')
    if addr == '':
        # addr = StockConst.root + StockConst.newDailyQuoteH5
        return None
    #New_DailyQuote_Mi.h5
    store = pd.HDFStore(addr)
    dailyQuote = store.select('Data')
    #print(store)
    #print(dailyQuote)
    store.close()
    return dailyQuote

# signalData = loadSignalData('')
# dailyQuote = loadNewDailyQuote('')

# start_loop = time.clock()
# # signalData = pd.read_hdf(StockConst.root+StockConst.signalDataH5)
# signalData = loadSignalData('')
# end_loop = time.clock()
# print("for循环花费时间：%f s" % (end_loop - start_loop))
#
# start_loop = time.clock()
# # newDailyQuoteH5 = pd.read_hdf(StockConst.root+StockConst.newDailyQuoteH5)
# dailyQuote = loadNewDailyQuote('')
# end_loop = time.clock()
# print("for循环花费时间：%f s" % (end_loop - start_loop))


# def loadNewDailyQuoteToPn(addr=''):
#     if addr == '':
#         # addr = StockConst.root + StockConst.newDailyQuoteH5
#         return None
#     print('loadNewDailyQuoteToPn：'+addr)
#
#     a = pd.read_hdf(addr)
#     pn = a.to_panel()
#     return pn



@TimeUtil.check_consumed_time3
def load_new_daily_quote_by_date(startDate, endDate, addr=''):
    print('loadNewDailyQuoteByDate')
    if addr == '':
        # addr = StockConst.root + StockConst.newDailyQuoteH5
        return None
    #Mom_5_D.h5
    store = pd.HDFStore(addr)
    #print(store)
    t1 = pd.Timestamp(startDate)
    t2 = pd.Timestamp(endDate)
    dailyQuote = store.select('Data',
        where = [
                'TradingDay>=Timestamp("'+startDate+'")',
                'TradingDay<=Timestamp("'+endDate+'")'
                ]
    )
    #print(dailyQuote.columns)
    #print(dailyQuote)
    store.close()
    return dailyQuote

# signalData = loadNewDailyQuoteByDate('20040112','20040115','')
# print(signalData)

#把一个df导出到h5
def export_to_hdfstore(df, addr):
    store = pd.HDFStore(addr)
    #data_columns=['ComplaintType', 'Descriptor', 'Agency']
    store.append('Data', df)


#按TradingDay InnerCode查询
#停牌取最近一个交易日
#dailyQuote: dataFrame
def select_by_inner_code_and_date(dailyQuote, tradingDate, innerCode):
    #找不到数据(停牌): 取最近一个交易日
    if (tradingDate, innerCode) not in dailyQuote.index:
        #entity = {StockConst.sellFlg: -1, StockConst.buyFlg: -1}]
        df = select_by_prev_tradingday(dailyQuote, tradingDate, innerCode)
        lastTradingDay = df.index[0][0] #为了格式和else中的一致
        entity = df.ix[(lastTradingDay, innerCode)] #为了格式和else中的一致
    else:
        entity = dailyQuote.ix[(tradingDate, innerCode)]
    return entity

#TODO 最近一个交易日也没有数据的情况
def select_signal_by_date_and_inner_code(signalData, tradingDate, innerCode):
    # 找不到数据(停牌): 取最近一个交易日
    if (tradingDate, innerCode) not in signalData.index:
        # print('selectSignalByDateAndInnerCode-stop')
        # entity = {StockConst.sellFlg: -1, StockConst.buyFlg: -1}]
        # print(tradingDate)
        # print(innerCode)
        df = select_signal_by_prev_tradingday(signalData, tradingDate, innerCode)
        lastTradingDay = df.index[0][0]
        entity = df.ix[(lastTradingDay, innerCode)]
    else:
        # print('selectSignalByDateAndInnerCode-none')
        entity = signalData.ix[(tradingDate, innerCode)]
    return entity

#test
def select_signal_by_date_and_inner_code2(signalData, tradingDate, innerCode, field):
    # 找不到数据(停牌): 取最近一个交易日
    if (tradingDate, innerCode) not in signalData.index:
        # print('selectSignalByDateAndInnerCode-stop')
        # entity = {StockConst.sellFlg: -1, StockConst.buyFlg: -1}]
        # print(tradingDate)
        # print(innerCode)
        df = select_signal_by_prev_tradingday(signalData, tradingDate, innerCode)
        lastTradingDay = df.index[0][0]
        entity = df.ix[(lastTradingDay, innerCode)]
    else:
        # print('selectSignalByDateAndInnerCode-none')
        entity = signalData.ix[(tradingDate, innerCode)]
    return entity[field]

#是否因为停牌和一字涨停不能买入
def check_if_cannot_buy(dailyQuote, tradingDate, innerCode):
    # 找不到数据: 停牌
    if (tradingDate, innerCode) not in dailyQuote.index:
        # print('checkIfCannotBuy-stop')
        return True
    else:
        entity = dailyQuote.ix[(tradingDate, innerCode)]
        #一字涨停
        if entity[StockConst.BUY_FLG] == -1:
            # print('checkIfCannotBuy-yzzt')
            return True
        else:
            pass
            # print('checkIfCannotBuy-none')
    return False

#是否因为停牌和一字涨停不能买入
def check_if_cannot_buy_1day(dailyQuote1day, innerCode):
    # 找不到数据: 停牌
    if innerCode not in dailyQuote1day.index:
        # print('checkIfCannotBuy-stop')
        return True
    else:
        entity = dailyQuote1day.ix[innerCode]
        #一字涨停
        if entity[StockConst.BUY_FLG] == -1:
            # print('checkIfCannotBuy-yzzt')
            return True
        else:
            pass
            # print('checkIfCannotBuy-none')
    return False


# def checkIfCannotBuyPn(dailyQuotePn, tradingDate, innerCode):
#     # 找不到数据: 停牌
#     if (tradingDate, innerCode) not in dailyQuotePn.index:
#         # print('isstop')
#         return True
#     else:
#         # entity = dailyQuote.ix[(tradingDate, innerCode)]
#         entity = dailyQuotePn.loc[:, tradingDate, innerCode]
#         # 一字涨停
#         if entity[StockConst.buyFlg] == -1:
#             # print('isyizizhangting')
#             return True
#     return False

def check_if_cannot_buy_pn(dailyQuotePn, tradingDate, innerCode):
    try:
        # entity = dailyQuote.ix[(tradingDate, innerCode)]
        entity = dailyQuotePn.loc[:, tradingDate, innerCode]
        # 一字涨停
        if entity[StockConst.BUY_FLG] == -1:
            # print('checkIfCannotBuy-yzzt')
            return True
        else:
            pass
            # print('checkIfCannotBuy-none')
    # 找不到数据: 停牌
    except:
        # print('checkIfCannotBuy-stop')
        return True

    return False


# dailyQuotePn = loadNewDailyQuoteToPn('')
# time_list = [time.time()]
# ret = checkIfCannotBuyPn(dailyQuotePn, pd.Timestamp('2005-01-05'), '000001.SZ')
# print(ret)
# time_list.append(time.time())
# print(np.array(time_list[1:len(time_list)]) - np.array(time_list[0:len(time_list) - 1]))
# print(ret)

# a = pd.read_hdf('D:\\New_BRPrice_0302.h5')
# pn = a.to_panel()
# time_list = [time.time()]
#
# res = pn.loc[:,'2005-01-05', '000001.SZ']
# # print(res)
# time_list.append(time.time())
# print(np.array(time_list[1:len(time_list)]) - np.array(time_list[0:len(time_list) - 1]))



#是否因为停牌和一字涨停不能卖出
def check_if_cannot_sell(dailyQuote, tradingDate, innerCode):
    # 找不到数据: 停牌
    if (tradingDate, innerCode) not in dailyQuote.index:
        # print('tradingDate:'+DateUtil.datetime2Str(tradingDate))
        # print('innerCode:' + str(innerCode))
        # print('checkIfCannotSell-stop')
        return True
    else:
        entity = dailyQuote.ix[(tradingDate, innerCode)]
        #一字跌停
        if entity[StockConst.SELL_FLG] == -1:
            # print('checkIfCannotSell-yzdt')
            return True
        else:
            # print('checkIfCannotSell-none')
            pass
    return False

def check_if_cannot_sell_1day(dailyQuote1day, innerCode):
    # 找不到数据: 停牌
    if innerCode not in dailyQuote1day.index:
        # print('checkIfCannotBuy-stop')
        return True
    else:
        entity = dailyQuote1day.ix[innerCode]
        #一字跌停
        if entity[StockConst.SELL_FLG] == -1:
            # print('checkIfCannotBuy-yzzt')
            return True
        else:
            pass
            # print('checkIfCannotBuy-none')
    return False


"""暂时不用
#退市的股票，取最后一个交易日
def selectByLastDay(dailyQuote,innerCode):
    #dailyQuote = loadNewDailyQuote()
    dailyQuote2 = selectByInnerCode(dailyQuote, innerCode)
    dailyQuote2 = dailyQuote2[(dailyQuote2[StockConst.TurnoverVolume] != float(0)) & (dailyQuote2[StockConst.ClosePrice] != 0)]
    dailyQuote2 = dailyQuote2.sort_index(ascending=False)
    #closePrice = dailyQuote2['ClosePrice']
    #print(closePrice)
    return dailyQuote2[0:1]
"""
#tradingDate前最后一个交易日
def select_by_prev_tradingday(dailyQuote, tradingDate, innerCode):
    dailyQuote = select_by_inner_code(dailyQuote, innerCode)
    t2 = pd.Timestamp(tradingDate)
    dailyQuote = dailyQuote.loc[:t2, :]
    dailyQuote = dailyQuote.sort_index(ascending=False)
    return dailyQuote[0:1]

#tradingDate前最后一个交易日
def select_signal_by_prev_tradingday(signalData, tradingDate, innerCode):
    signalData = select_signal_by_inner_code(signalData, innerCode)
    t2 = pd.Timestamp(tradingDate)
    signalData = signalData.loc[:t2, :]
    signalData = signalData.sort_index(ascending=False)
    return signalData[0:1]

#按日期查询 ok
def select_by_date(dailyQuote, startDate, endDate):
    #dailyQuote2 = dailyQuote[(dailyQuote['TradingDay'] >= startDate) & (dailyQuote['TradingDay'] <= endDate)]
    #dailyQuote2 = dailyQuote.ix[startDate:endDate] 这种方法有报错的风险
    t1 = pd.Timestamp(startDate)
    t2 = pd.Timestamp(endDate)
    dailyQuote2 = dailyQuote.loc[t1:t2, :]
    return dailyQuote2

def select_signal_by_date(signalData, startDate, endDate):
    #dailyQuote2 = dailyQuote[(dailyQuote['TradingDay'] >= startDate) & (dailyQuote['TradingDay'] <= endDate)]
    #dailyQuote2 = dailyQuote.ix[startDate:endDate] 这种方法有报错的风险
    t1 = pd.Timestamp(startDate)
    t2 = pd.Timestamp(endDate)
    signalData2 = signalData.loc[t1:t2, :]
    return signalData2

"""
#弃用
#按innerCode查询
def selectByInnerCodeOld(dailyQuote,innerCode):
    dailyQuote[StockConst.InnerCode] = dailyQuote.index.get_level_values(1)
    dailyQuote2 = dailyQuote[(dailyQuote[StockConst.InnerCode] == innerCode)]
    return dailyQuote2
"""

#按innerCode查询
def select_by_inner_code(dailyQuote, innerCode):
    dailyQuote = dailyQuote[dailyQuote.index.get_level_values(1) == innerCode]
    return dailyQuote


#按innerCode查询
def select_signal_by_inner_code(signalData, innerCode):
    signalData = signalData[signalData.index.get_level_values(1) == innerCode]
    return signalData


#'2016-01-01':'2016-01-31'
#用信号数据取得唯一性日期
#筛选,取得索引,去重
#返回:列表
@TimeUtil.check_consumed_time5
def select_date_from_signal(signalData, startDate='', endDate=''):
    print('selectDateFromSignal')
    #筛选
    df2 = signalData
    if startDate:
        if endDate:
            t1 = pd.Timestamp(startDate)
            t2 = pd.Timestamp(endDate)
            df2 = signalData.loc[t1:t2,:]
    #print(df2)
    #取得索引,去重
    #l2 = getIndexAndDistinct(df2)
    l2 = list(df2.index.get_level_values(StockConst.TRADINGDAY).unique())
    return l2


# addBuySellFlgAndExport(StockConst.root+StockConst.dailyQuoteH5)

# addDelistFlgAndExport(StockConst.root+'/New_Daily_Bars.h5','New_Daily_Bars2')


# dailyQuote = loadDailyQuote(StockConst.root+'/New_Daily_Bars2.h5') #BRPrice_0310.h5
# dailyQuote = selectByInnerCode(dailyQuote,'600000.SH')
# print(dailyQuote)
# # dailyQuote.to_csv(StockConst.root + '\export\Daily_Bars.csv')
# # df=dailyQuote.iloc[0:1]
# # date=df.index[0][0]
# # print(date)
# # print(type(date))
# t=pd.Timestamp('2005-01-05')
# df=dailyQuote.xs(t)
# print(t)
# print(df)






# dailyQuote = loadNewDailyQuote('')
# start = time.clock()
# entity = dailyQuote.loc[('2004-01-12', '000049.SZ')]
# end = time.clock()
# print("main花费时间：%f s" % (end - start))
# print(entity)

# def mypow(a, times):
#     ret = 1
#     for x in range(times):
#         ret = ret * a
#     return ret

# createSignalDataHill()
# createDailyQuoteHill()

# exportSignal()

#loadNewDailyQuote()
#'2016-01-05':'2016-01-08'

#printByInnerCodeAndDate()

#printGroupedSingalData()

#printSingalDataByDate('2004-01-06')

# createFakeSignalData()

# getColumsFromH5('')

# print(getFirstRecordFromH5(StockConst.root+StockConst.fakeSignalDataH5).index[0][0])

# signalData = loadSignalData('')
# print(signalData)

# dailyQuote = loadNewDailyQuote(StockConst.root + '/export/DailyQuoteHill.h5')
# print(dailyQuote)

#测试 导出一个子集到h5文件
# addBuySellFlgAndExport()

"""
dailyQuote = loadNewDailyQuote()
df = selectByInnerCodeAndDate(dailyQuote,'2004-02-10','000521.SZ')
print(df)
"""

"""
#dailyQuote = selectDateFromSignal(dailyQuote)#'2016-01-01','2016-01-08'
dailyQuote = loadDailyQuote()
#signalData = loadSignalData()
#print(signalData)
dailyQuote = selectByDate(dailyQuote,'2004-01-05','2004-01-05')
print(dailyQuote)
"""

"""
dailyQuote = loadDailyQuote()
dailyQuote2 = dailyQuote.ix['2016', :]
print(dailyQuote2)
"""

"""
dailyQuote = loadDailyQuote()
df = selectByDate(dailyQuote,'2016-01-01','2016-01-05')
print(df)
"""

#print(dailyQuote2)
"""
signalData = loadSignalData()
ss = signalData.index.get_level_values(0)
l2 = list(set(ss))
#l2.sort(key=signalData.index)
l2.sort()
print(l2)
"""



"""
signalData = loadSignalData()
#ss = selectDateFromSignal(signalData,'2016-01-01','2016-01-31')
#print(ss)
t1 = pd.Timestamp('2016-01-01')
t2 = pd.Timestamp('2016-01-31')
df2 = signalData.loc[t1:t2,:]
#print(df2)
#取得索引,去重
#l2 = getIndexAndDistinct(df2)
#ss = df2.index.levels[0] # 已经去重,且保持原来的顺序
"""

"""
signalData = loadSignalData()
entity = signalData.ix[('2001-07-27',1880)]
print(entity)
"""

"""
import pandas as pd
import numpy as np
a = pd.DataFrame(data=np.random.randn([2,3]))
"""