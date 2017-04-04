from backtest.Util import NumUtil
from backtest.Constance import StockConst

class CapitalEntity:
    """ 当前资金情况。
    :ivar usable_cach: 可用现金
    :ivar stock_mv: 股票市值
    :ivar total_asset: 总资产
    """
    def __init__(self, a_usable_cach, a_stock_mv, a_total_asset):
        self.usable_cach = a_usable_cach
        self.stock_mv = a_stock_mv
        self.total_asset = a_total_asset

    def increase_usable_cash(self, a_cach):
        self.usable_cach += a_cach
        self.usable_cach = NumUtil.get_round(self.usable_cach, StockConst.USABLE_CASH_SCALE)

    def reduce_usable_cash(self, a_cach):
        self.usable_cach -= a_cach
        self.usable_cach = NumUtil.get_round(self.usable_cach, StockConst.USABLE_CASH_SCALE)

    def get_usable_cash(self):
        return self.usable_cach

    def get_total_asset(self):
        return self.total_asset

    def set_total_asset(self, a_total_asset):
        self.total_asset = a_total_asset

    def get_stock_mv(self):
        return self.stock_mv

    def set_stock_mv(self, a_stock_mv):
        self.stock_mv = a_stock_mv