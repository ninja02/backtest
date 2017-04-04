import datetime
import time

#装饰器，用于记录程序花费的时间
def check_consumed_time(fn):
    def process():
        starttime = datetime.datetime.now()
        a = fn()
        endtime = datetime.datetime.now()
        consumedTime = (endtime - starttime)
        consumedTimeSecond = consumedTime.seconds
        #consumedTimeMilli1 = consumedTime.microsecond
        consumedTimeMilli1 = ''
        consumedTimeMilli2 = consumedTime.microseconds
        print('花费时间：' + str(consumedTimeSecond) + '秒, (毫秒:'+str(consumedTimeMilli2)+')')
        return a
    return process

def check_consumed_time2(fn):
    def process():
        start = time.clock()
        a = fn()
        end = time.clock()
        print("花费时间：%f s" % (end - start))
        return a
    return process

def check_consumed_time3(fn):
    def process(startDate, endDate, addr):
        start = time.clock()
        a = fn(startDate, endDate, addr)
        end = time.clock()
        print("花费时间：%f s" % (end - start))
        return a
    return process

def check_consumed_time4(fn):
    def process(addr):
        start = time.clock()
        a = fn(addr)
        end = time.clock()
        print("花费时间：%f s" % (end - start))
        return a
    return process


#SourceDataDao.selectDateFromSignal
def check_consumed_time5(fn):
    def process(signalData,startDate,endDate):
        start = time.clock()
        a = fn(signalData,startDate,endDate)
        end = time.clock()
        print("花费时间：%f s" % (end - start))
        return a
    return process

#BackTestMainNew.main
def check_consumed_time6(fn):
    def process(select_stock_func,trade_func,techList,signalDataAddr, dailyQuoteAddr, startDate, endDate):
        start = time.clock()
        a = fn(select_stock_func,trade_func,techList,signalDataAddr, dailyQuoteAddr, startDate, endDate)
        end = time.clock()
        print("花费时间：%f s" % (end - start))
        return a
    return process

#select_stock_func1
def check_consumed_time7(fn):
    def process(tech_list, slice_dict, global_dict):
        start = time.clock()
        a = fn(tech_list, slice_dict, global_dict)
        end = time.clock()
        print("花费时间：%f s" % (end - start))
        return a
    return process

def check_consumed_time8(fn):
    def process(addr, signalColumnDict):
        start = time.clock()
        a = fn(addr,signalColumnDict)
        end = time.clock()
        print("花费时间：%f s" % (end - start))
        return a
    return process


