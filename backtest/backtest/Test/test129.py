import pandas as pd
import numpy as np
from pandas.io.pytables import Term
from Service import BackTestHelper
from pandas import Series, DataFrame
from Constance import StockConst
from Util import DateUtil
from Util import TimeUtil
from Util import SelectUtil
import datetime
import calendar,time

#直接从h5文件取得列名
def getColumsFromH5(addr):
    aa = pd.HDFStore(StockConst.root+StockConst.fakeSignalDataH5)
    return aa