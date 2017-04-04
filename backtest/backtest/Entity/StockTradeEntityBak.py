
class StockTradeEntity(object):
    """ 每日调仓信息。
    :ivar tradingDate: 日期。
    :ivar innerCode: 股票内部代码。
    :ivar tradeType: 买卖类型:1买入 -1卖出 0持有。
    :ivar vol: 仓位。
    :ivar price: 成交价格。
    :ivar changePCT: 当日该笔交易的理论收益(没有算仓位)。
    :ivar realChangePCT: 当日该笔交易的实际收益(算仓位)。
    """
    def __init__(self, tradingDate, innerCode, tradeType, vol, price, changePCT, realChangePCT):
        self.tradingDate = tradingDate
        self.innerCode = innerCode
        self.tradeType = tradeType
        self.vol = vol
        self.price = price
        self.changePCT = changePCT
        self.realChangePCT = realChangePCT