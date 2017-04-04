import pandas as pd
# import MyFunc
import time
import numpy as np

tradingday = pd.Timestamp('2005-01-05')
windcode = '000001.SZ'

# @MyFunc.perf_monitor
def read_method(method):
    if method == 1:
        a = pd.read_hdf(r'F:\Python_3\MyPython_3\0_Data\Pub\BRPrice.h5')
        time_list = [time.time()]
        # cost  0.30s
        res = a.loc[pd.IndexSlice[tradingday,windcode],:]
        time_list.append(time.time())
        print(np.array(time_list[1:len(time_list)]) - np.array(time_list[0:len(time_list) - 1]))
        # use idx
    elif method == 2:
        a = pd.HDFStore(r'F:\Python_3\MyPython_3\0_Data\Pub\BRPrice.h5')
        time_list = [time.time()]
        # cost  0.05s
        res = a.select(key='Data', where=pd.Term("(TradingDay = tradingday)&(WindCode = windcode)"))
        time_list.append(time.time())
        print(np.array(time_list[1:len(time_list)]) - np.array(time_list[0:len(time_list) - 1]))
    elif method == 3:
        a = pd.read_hdf(r'F:\Python_3\MyPython_3\0_Data\Pub\BRPrice.h5')
        pn = a.to_panel()
        time_list = [time.time()]
        # cost  0.001s
        res = pn.loc[:,tradingday, windcode]
        time_list.append(time.time())
        print(np.array(time_list[1:len(time_list)]) - np.array(time_list[0:len(time_list) - 1]))
    elif method == 4:
        # this method is very slow!!
        a = pd.read_hdf(r'F:\Python_3\MyPython_3\0_Data\Pub\BRPrice.h5')
        dict_frm = a.to_dict(orient = 'index')
        res = dict_frm[tradingday]

if __name__ == '__main__':
    read_method(3)




