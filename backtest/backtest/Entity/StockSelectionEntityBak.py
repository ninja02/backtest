
class StockSelectionEntity(object):
    """ 每日选股信息。
    :ivar tradingDate: 日期。
    :ivar innerCode: 股票内部代码。
    """
    def __init__(self, tradingDate, innerCode):
        self.tradingDate = tradingDate
        self.innerCode = innerCode