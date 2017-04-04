class MVEntity:

    """ 每日持仓信息。
    :ivar innerCode: 股票内部代码。
    :ivar MV: 仓位。
    """

    def __init__(self, a_innerCode,a_MV):
        self.innerCode = a_innerCode
        self.MV = a_MV