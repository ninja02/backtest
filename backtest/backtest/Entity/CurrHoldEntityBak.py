
class CurrHoldEntity:
    """ 当前持仓信息。
    :ivar innerCode: 股票内部代码。
    :ivar vol: 仓位。
    """
    def __init__(self, a_innerCode, a_vol):
        self.innerCode = a_innerCode
        self.vol = a_vol