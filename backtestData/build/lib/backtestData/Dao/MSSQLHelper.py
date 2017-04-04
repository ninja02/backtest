from backtestData.Dao import MSSQL
import pandas as pd
from backtestData.Constance import StockConst

def get_mssql_instance_default():
    ms = MSSQL.MSSQL(host="192.168.1.4", user="jydb", pwd="jydb", db="FishDB")
    return ms

def get_mssql_instance(host,user,pwd,db):
    ms = MSSQL.MSSQL(host=host, user=user, pwd=pwd, db=db)
    return ms

def get_mssql_instance_by_dict(databaseDict):
    ip = databaseDict.get(StockConst.IP)
    account = databaseDict.get(StockConst.ACCOUNT)
    password = databaseDict.get(StockConst.PASSWORD)
    database = databaseDict.get(StockConst.DATABASE)
    # tablename = databaseDict.get(StockConst.TABLENAME)

    ms = MSSQL.MSSQL(host=ip, user=account, pwd=password, db=database)
    return ms
