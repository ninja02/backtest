import pandas as pd
# import MyFunc
import time
import numpy as np

tradingday = pd.Timestamp('2005-01-05')
windcode = '000001.SZ'

def read_method(method):
    store = pd.HDFStore('D:\\New_BRPrice_0302.h5')
    # print(store)
    signalData = store.select('Data'
                              # [
                              # Term('InnerCode', '=', 3),
                              # Term('TradingDay', '>=', startDate),
                              # Term('TradingDay', '<=', endDate),
                              # Term('columns', '=', 'Mom')
                              # ]
                              );

    time_list = [time.time()]
    entity = signalData.ix[(tradingday, windcode)]
    time_list.append(time.time())
    print(np.array(time_list[1:len(time_list)]) - np.array(time_list[0:len(time_list) - 1]))

if __name__ == '__main__':
    read_method(3)