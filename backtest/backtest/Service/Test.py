from backtestData.Dao import SourceDataDao
from backtest.Util import SelectUtil
from backtest.Util import DateUtil
from backtest.Util import SetUtil
from backtest.Entity import StockHoldEntity
from backtest.Entity import StockTradeEntityBak
from backtest.Util import NumUtil

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from datetime import datetime

def main():


    df1 = pd.DataFrame(
        {'AAA': [4, 5, 6, 7],
         'BBB': [10, 20, 30, 40],
         'CCC': [100, 50, -30, -50]
         },
        index=[['a', 'b', 'c', 'd'],['0', '1', '2', '3']]
    );

    df2 = pd.DataFrame(
        {'AAA': [4, 5, 9, 9],
         'BBB': [10, 20, 30, 40],
         'DDD': [1, 1, 1, 1]
         },
        index=[['a', 'b', 'e', 'f'],['0', '1', '4', '5']]
    );

    df3 = pd.DataFrame(
        {'AAA': [4, 5, 9, 9],
         'BBB': [50, 50, 30, 40],
         'DDD': [1, 1, 1, 1]
         },
        index=['a', 'b', 'e', 'f']
    );

    df3.plo

    print('0')
main()



