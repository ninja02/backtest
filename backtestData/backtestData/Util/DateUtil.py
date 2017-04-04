#coding:utf-8
import time
from datetime import datetime
from pandas import Series, DataFrame
import pandas as pd

#当前时间
def get_current_time():
     t = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
     return t

#当前时间
def get_current_time2():
     t2 = time.strftime("%Y-%m-%d",time.localtime(time.time()))
     return t2

#字符串转dateTime
def str2_datetime(str):
    a=time.strptime(str,'%Y-%m-%d'); # %Y%m%d
    a_datetime=datetime(*a[:3]);
    return a_datetime

def str2_datetime_format(str, format):
    a=time.strptime(str,format); # %Y%m%d
    a_datetime=datetime(*a[:3]);
    return a_datetime

#dateTime转字符串
def datetime2_str(dt):
    return dt.strftime("%Y-%m-%d")

def datetime2_str_format(dt, format):
    return dt.strftime(format)

def datetime64_2_str(tradingDay):
    ts = pd.to_datetime(str(tradingDay))
    d = ts.strftime('%Y-%m-%d')
    return d

#dateTime转年份
def datetime2_year_str(dt):
    return dt.strftime("%Y")

#日期列表
def get_date_list(startDate, len):
    dateList = Series(index=pd.date_range(startDate, periods=len))
    return dateList

#日期列表
def get_date_list2(startDate, endDate):
    dateList = Series(index=pd.date_range(startDate, endDate))
    return dateList




#print(b_datetime-a_datetime);
"""
def string2timestamp(strValue):
    try:
        d = datetime.strptime(strValue, "%Y-%m-%d %H:%M:%S.%f")
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        timeStamp = float(str(timeStamp) + str("%06d" % d.microsecond))/1000000
        #print(timeStamp)
        return timeStamp
    except ValueError as e:
        print(e)
        d = datetime.strptime(strValue, "%Y-%m-%d %H:%M:%S")
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        timeStamp = float(str(timeStamp) + str("%06d" % d.microsecond))/1000000
        print(timeStamp)
        return timeStamp
"""
#s = string2timestamp('2001-01-02 00:00:00.00');
