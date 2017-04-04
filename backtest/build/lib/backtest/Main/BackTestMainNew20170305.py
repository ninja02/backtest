from backtestData.Dao import SourceDataDao
from backtest.Util import SelectUtil
from backtest.Util import DateUtil
from backtest.Util import SetUtil
from backtest.Util import NumUtil
from backtest.Entity import StockHoldEntity
from backtest.Entity import StockTradeEntityBak
from backtest.Entity import CapitalEntity
from backtest.Constance import StockConst
from backtest.Service import StockMaxDropService
from backtest.Service import StockMaxDropNewService
from backtest.Service import SharpRatioService
from backtest.Service import SharpRatioNewService
from backtest.Service import StockYearService
from backtest.Service import BackTestHelper
from backtest.Util import TimeUtil
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from datetime import datetime
import math

def main():
    signalData = SourceDataDao.getSignalData()
    #dailyQuote = SourceDataDao.getDailyQuote()
    dailyQuote = SourceDataDao.getNewDailyQuote()



main()




