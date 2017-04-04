
class StockHoldEntity:

    """ 每日持仓信息。
    :ivar innerCode: 股票内部代码。
    :ivar vol: 仓位。(删除)
    :ivar buyPrice: 买入价。
    :ivar cost: 成本价。(忽略)
    :ivar openDate: 买入日期。(参考)
    :ivar buyMV: 买入市值。
    :ivar closePrice: 收盘价
    :ivar closeMV: 收盘市值
    """
    def __init__(self, a_innerCode,a_lastTradePrice,a_cost,a_openDate,a_lastTradeMV,a_originBuyPrice,a_originBuyMV,a_closePrice,a_closeMV,a_changeDate):
        self.innerCode = a_innerCode
        self.lastTradePrice = a_lastTradePrice
        self.cost = a_cost
        self.openDate = a_openDate
        self.lastTradeMV = a_lastTradeMV
        self.originBuyPrice = a_originBuyPrice
        self.originBuyMV = a_originBuyMV
        self.closePrice = a_closePrice
        self.closeMV = a_closeMV
        self.changeDate = a_changeDate

    def set_buy_price(self, a_lastTradePrice):
        self.lastTradePrice = a_lastTradePrice

    def set_buy_mv(self, a_lastTradeMV):
        self.lastTradeMV = a_lastTradeMV

    def set_change_date(self, a_changeDate):
        self.changeDate = a_changeDate

    def set_close_price(self, a_closePrice):
        self.closePrice = a_closePrice

    def set_close_mv(self, a_closeMV):
        self.closeMV = a_closeMV

    def set_last_trade_price(self, a_lastTradePrice):
        self.lastTradePrice = a_lastTradePrice

    def set_last_trade_mv(self, a_lastTradeMV):
        self.lastTradeMV = a_lastTradeMV

    """
    #弃用
    def __init__(self, a_tradingDate, a_innerCode, a_vol, a_closePrice, a_mv):
        self.tradingDate = a_tradingDate
        self.innerCode = a_innerCode
        self.vol = a_vol
        self.closePrice = a_closePrice
        self.mv = a_mv

    # 弃用
    def __init__(self, a_tradingDate, a_innerCode, a_vol):
        self.tradingDate = a_tradingDate
        self.innerCode = a_innerCode
        self.vol = a_vol
    """


""" """



