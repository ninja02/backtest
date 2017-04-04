from backtest.Util import NumUtil
from backtest.Constance import StockConst

def get_vwap(daily_quote_row):
    if StockConst.DATA_SOURCE_NO == 1:
        # try:
        turnover_value = daily_quote_row[StockConst.TURNOVER_VALUE]
        # except:
        # print('tradingDate:'+dateStr)
        # print('innerCode:' + str(innerCode))
        # print(dailyQuoteRow)
        turnover_volume = daily_quote_row[StockConst.TURNOVER_VOLUME]
        vwap = turnover_value / turnover_volume
        return vwap
    # 数据源2的vwap需要乘复权因子
    elif StockConst.DATA_SOURCE_NO == 2:
        return daily_quote_row[StockConst.VWAP] * daily_quote_row[StockConst.CUM_ADJ]
    elif StockConst.DATA_SOURCE_NO == 3:
        turnover_value = daily_quote_row[StockConst.TURNOVER_VALUE]
        turnover_volume = daily_quote_row[StockConst.TURNOVER_VOLUME]
        cum_adj = daily_quote_row[StockConst.CUM_ADJ]
        vwap = turnover_value / turnover_volume * cum_adj
        return vwap

def get_close_price(daily_quote_row):
    if StockConst.DATA_SOURCE_NO == 1:
        return daily_quote_row[StockConst.CLOSE_PRICE]
    #数据源2的价格是后复权数据,无需乘复权因子
    elif StockConst.DATA_SOURCE_NO == 2:
        return daily_quote_row[StockConst.CLOSE_PRICE] # dailyQuoteRow[StockConst.CumAdj]
    elif StockConst.DATA_SOURCE_NO == 3:
        return daily_quote_row[StockConst.CLOSE_PRICE] * daily_quote_row[StockConst.CUM_ADJ]


#卖出市值
def get_sell_mv(buy_price, buy_mv, sell_price):
    return buy_mv / buy_price * sell_price

"""
#没有使用
#是否一字跌停
def isYiZiDieTing(highPrice,lowPrice,prevClosePrice):
    if( (lowPrice < prevClosePrice) & (highPrice == lowPrice) ):
        return True
    else:
        return False

# 没有使用
#是否一字涨停
def isYiZiZhangTing(highPrice,lowPrice,prevClosePrice):
    if( (highPrice > prevClosePrice) & (highPrice == lowPrice) ):
        return True
    else:
        return False

# 没有使用
#停牌
def isStop(closePrice, turnoverValue):
    if( (closePrice == 0) | (turnoverValue == float(0)) ):
        return True
    else:
        return False
"""

#turnover包含了commission
#turnover: 买入的金额
#commission: 佣金（已经除过100，单位没有百分号）
#返回的是金额
def get_buy_commission(turnover, commission):
    return turnover * commission / (commission + 1)

#turnover包含了commission
#turnover: 卖出后所得资金
#commission: 佣金（已经除过100，单位没有百分号）
#返回的是金额
def get_sell_commission(turnover, commission):
    return turnover * commission

"""
#是否一字跌停
def isYiZiDieTing(highPrice,prevClosePrice,closePrice):
    if NumUtil.getChangePCT(prevClosePrice, closePrice, 0) == -10 & (highPrice == closePrice):
        return True
    else:
        return False

#是否一字涨停
def isYiZiZhangTing(lowPrice, prevClosePrice, closePrice):
    if NumUtil.getChangePCT(prevClosePrice, closePrice, 0) == 10 & (lowPrice == closePrice):
        return True
    else:
        return False
"""