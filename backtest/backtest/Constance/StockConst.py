#买入佣金(百分之)
BUY_COMMISSION = 0.125
#卖出佣金(百分之)
SELL_COMMISSION = 0.225
#是否debug模式
IS_DEBUG = False #False True
#无风险收益
NONE_RISK_PROFIT_FOR_YEAR = 3.0
#可用现金精确到小数后几位
USABLE_CASH_SCALE = 5
#仓位精确到小数后几位
VOL_SCALE = 10
#盘符
ROOT = 'D:'
#
BUY_FLG= 'buyFlg'
SELL_FLG= 'sellFlg'

#仓位权重：范围：0-1
VOL_WEIGHT= 'volWeight'

#1:非复权数据
#2:复权数据
DATA_SOURCE_NO = 3

MOM = 'Mom'

TRADING_DAY_NAME = 'TradingDay'
WIND_CODE_NAME = 'WindCode'
TECH_NAME = 'Mom'

IP = 'ip'
ACCOUNT = 'account'
PASSWORD = 'password'
DATABASE = 'database'
SIGNAL_TABLENAME = 'signaltablename'


"""
#数据源
signalDataH5='/Mom_5_D.h5'
dailyQuoteH5='/DailyQuote_Mi.h5'
newDailyQuoteH5='/New_DailyQuote_Mi.h5'
Mom = 'Mom'
#数据源
TradingDay = 'TradingDay'
InnerCode = 'InnerCode'
ClosePrice = 'ClosePrice'
PrevClosePrice = 'PrevClosePrice'
HighPrice = 'HighPrice'
LowPrice = 'LowPrice'
OpenPrice = 'OpenPrice'
TurnoverValue = 'TurnoverValue'
TurnoverVolume = 'TurnoverVolume'
"""

"""
#数据源
signalDataH5='/Mom_5_0302.h5'
# signalDataH5='/export/SignalDataHill.h5'
dailyQuoteH5='/BRPrice_0302.h5'
newDailyQuoteH5='/New_BRPrice_0302.h5'
newDailyQuote0316H5='/New_BRPrice_0316.h5'
# newDailyQuoteH5='/export/DailyQuoteHill.h5'
fakeSignalDataH5='/Mom_5_fake.h5'
#数据源
TradingDay = 'TradingDay'
InnerCode = 'WindCode'
ClosePrice = 'BRClosePrice'
HighPrice = 'BRHighPrice'
LowPrice = 'BRLowPrice'
OpenPrice = 'BROpenPrice'
TurnoverVolume = 'TurnoverVolume'
DailyReturn = 'DlyRet'
VWAP = 'VWAP'
Adj = 'Adj'
CumAdj = 'CumAdj'
"""

#数据源
SIGNAL_DATA_H5= '/0_Data/Mom_5_0302.h5'
# signalDataH5='/export/SignalDataHill.h5'
DAILY_QUOTE_H5= '/0_Data/Daily_Bars.h5'
NEW_DAILY_QUOTE_H5= '/0_Data/New_Daily_Bars2.h5'
# newDailyQuote0316H5='/New_BRPrice_0316.h5'
# newDailyQuoteH5='/export/DailyQuoteHill.h5'
FAKE_SIGNAL_DATA_H5= '/0_Data/Mom_5_fake.h5'

HS300H5 = '/0_Data/AsIndexComponentHS300.h5'
ZZ500H5 = '/0_Data/AsIndexComponentZZ500.h5'
ZZ800H5 = '/0_Data/AsIndexComponentZZ800.h5'

SIGNAL_DATA_BASEDON_HS300= '/0_Data/Mom_basedon_HS300.h5'
SIGNAL_DATA_BASEDON_ZZ500= '/0_Data/Mom_basedon_ZZ500.h5'
SIGNAL_DATA_BASEDON_ZZ800= '/0_Data/Mom_basedon_ZZ800.h5'

HS300_CODE = '000300.SH'
ZZ500_CODE = '000905.SH'
ZZ800_CODE = '000906.SH'

FAKE_INDEX_QUOTE_H5 = '/0_Data/FakeIndexQuote.h5'
FAKE_INDEX_QUOTE_H5_2 = '/0_Data/FakeIndexQuote2.h5'

#数据源
TRADINGDAY = 'TradingDay'
INNERCODE = 'WindCode'
CLOSE_PRICE = 'ClosePrice'
HIGH_PRICE = 'HighPrice'
LOW_PRICE = 'LowPrice'
OPEN_PRICE = 'OpenPrice'
PREV_CLOSE_PRICE = 'PrevClosePrice'
TURNOVER_VALUE = 'Amount'
TURNOVER_VOLUME = 'Volume'
# PctChangeD = 'PctChangeD'
CUM_ADJ = 'AccuAdjustingFactor'
TRADE_FLAG = 'TradeFlag'
TOTAL_MKT_VALUE = 'TotalMktValue'
FLOAT_MKT_VALUE = 'FloatMktValue'

