import pandas as pd
# import MyFunc
import time
import numpy as np
from backtestData.Dao import SourceDataDao

tradingday = pd.Timestamp('2005-01-05')
windcode = '000001.SZ'

# @MyFunc.perf_monitor
def read_method(method):
    if method == 1:
        a = pd.read_hdf(r'D:\BRPrice_0302.h5')
        time_list = [time.time()]
        # cost  0.30s
        res = a.loc[pd.IndexSlice[tradingday,windcode],:]
        time_list.append(time.time())
        print(np.array(time_list[1:len(time_list)]) - np.array(time_list[0:len(time_list) - 1]))
        # use idx
    elif method == 2:
        a = pd.HDFStore(r'D:\BRPrice_0302.h5')
        time_list = [time.time()]
        # cost  0.10s
        res = a.select(key= 'Data', where = pd.Term("(TradingDay = tradingday)&(WindCode = windcode)"))
        time_list.append(time.time())
        print(np.array(time_list[1:len(time_list)]) - np.array(time_list[0:len(time_list) - 1]))
    elif method == 3:
        a = pd.read_hdf('D:\\New_BRPrice_0302.h5')
        pn = a.to_panel()
        time_list = [time.time()]
        # cost  0.42s
        # print(pn)
        # if tradingday in pn.major_axis:
        #     print(tradingday)
        # if windcode in pn.minor_axis:
        #     print(windcode)
        # else:
        #     print('not exists')

        res = pn.loc[:,tradingday, windcode]
        # print(res)
        time_list.append(time.time())
        print(np.array(time_list[1:len(time_list)]) - np.array(time_list[0:len(time_list) - 1]))
    elif method == 4:
        # this method is very slow!!
        a = pd.read_hdf(r'D:\BRPrice_0302.h5')
        dict_frm = a.to_dict(orient = 'index')
        res = dict_frm[tradingday]

    #日期用str比Timestamp慢
    elif method == 5:
        a = pd.read_hdf('D:\\New_BRPrice_0302.h5')
        pn = a.to_panel()
        time_list = [time.time()]
        res = pn.loc[:, '2005-01-05', windcode]
        # print(res)
        time_list.append(time.time())
        print(np.array(time_list[1:len(time_list)]) - np.array(time_list[0:len(time_list) - 1]))

    #ix 很慢
    elif method == 6:
        time_list = [time.time()]
        dailyQuote = pd.read_hdf(r'D:\BRPrice.h5')
        # # print(store)
        # dailyQuote = store.select('Data'
        #   # [
        #   # Term('InnerCode', '=', 3),
        #   # Term('TradingDay', '>=', startDate),
        #   # Term('TradingDay', '<=', endDate),
        #   # Term('columns', '=', 'Mom')
        #   # ]
        #   );
        time_list.append(time.time())
        # dailyQuote = dailyQuote[dailyQuote.index.get_level_values(0) == tradingday]
        time_list.append(time.time())

        # dailyQuote.sort_index(inplace= True)
        for i in range(10000):
            dailyQuote2 = dailyQuote.xs(tradingday)
            # print(i)

            # dailyQuote2 = dailyQuote.loc[tradingday]
        time_list.append(time.time())
        # print(dailyQuote)
        print(np.array(time_list[1:len(time_list)]) - np.array(time_list[0:len(time_list) - 1]))

        print('-----')

        planBuyList=['000001.SZ','000002.SZ','000004.SZ','000007.SZ','000010.SZ']

        for innerCode in planBuyList:
            time_list = [time.time()]
            # entity = dailyQuote.ix[(tradingday,innerCode)]
            entity = dailyQuote2.ix[innerCode]
            # print(entity)
            time_list.append(time.time())
            print(np.array(time_list[1:len(time_list)]) - np.array(time_list[0:len(time_list) - 1]))

if __name__ == '__main__':
    read_method(6)




