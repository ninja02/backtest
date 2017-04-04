from backtestData.Dao import MSSQL
from backtestData.Dao import MSSQLHelper
import pandas as pd
from backtestData.Constance import StockConst
from backtestData.Dao import SourceDataDao
from backtestData.Util import DateUtil

#查询表字段名（用于前端）
def get_table_columns(ip,account,password,database,tablename):

    ms = MSSQLHelper.get_mssql_instance(ip, account, password, database)

    # 连接
    sqlserverCon = ms.get_connect()

    sql = 'select name from syscolumns ' + \
          'where id=(select max(id) from sysobjects where xtype=:p1 and name=:p2) '
    sql=sql.replace(':p1','\'u\'')
    sql =sql.replace(':p2', '\''+tablename+'\'')

    data = pd.read_sql(sql, con=sqlserverCon)

    return data['name'].tolist()

#读信号数据
#查询信号数据表的全部数据
def select_signal_data(databaseDict,signalColumnDict):

    ## ms = MSSQL(host="localhost",user="sa",pwd="123456",db="PythonWeiboStatistics")
    ## #返回的是一个包含tuple的list，list的元素是记录行，tuple的元素是每行记录的字段
    ## ms.ExecNonQuery("insert into WeiBoUser values('2','3')")

    signaltablename = databaseDict.get(StockConst.SIGNAL_TABLENAME)

    tradingDayName = signalColumnDict.get(StockConst.TRADING_DAY_NAME)
    windCodeName = signalColumnDict.get(StockConst.WIND_CODE_NAME)
    techName = signalColumnDict.get(StockConst.TECH_NAME)

    # ms = MSSQLHelper.get_mssql_instance("192.168.1.4","jydb","jydb","FishDB")
    ms = MSSQLHelper.get_mssql_instance_by_dict(databaseDict)

    #连接
    sqlserverCon = ms.get_connect()
    sql = 'select '+tradingDayName+' TradingDay,'+windCodeName+' WindCode,Mom from ' + signaltablename #SignalDataTable

    # resList = ms.ExecQuery(sql)
    # for (NatureDay,WindCode,IfTradingDay) in resList:
    #     print(str(NatureDay) + ' ' + str(WindCode) + ' ' + str(IfTradingDay))

    #sqlserrver转成h5
    data = pd.read_sql(sql, con=sqlserverCon)
    # print('df:')
    # print(df)
    # exportToHDFStore(df, StockConst.root + '/' + targetAddr + '.h5')
    # SourceDataDao.export_to_hdfstore(df, StockConst.ROOT + StockConst.HS300H5)
    #
    # sqlserverCon.close()

    data = data.set_index([StockConst.TRADINGDAY, StockConst.INNERCODE])

    return data

#查询最大日期
def select_max_data(databaseDict,signalColumnDict):
    tradingDayName = signalColumnDict.get(StockConst.TRADING_DAY_NAME)
    windCodeName = signalColumnDict.get(StockConst.WIND_CODE_NAME)
    techName = signalColumnDict.get(StockConst.TECH_NAME)

    signaltablename = databaseDict.get(StockConst.SIGNAL_TABLENAME)

    ms = MSSQLHelper.get_mssql_instance_by_dict(databaseDict)
    # 连接
    sqlserverCon = ms.get_connect()
    sql = 'select max('+tradingDayName+') TradingDay from ' + signaltablename  # SignalDataTable
    data = pd.read_sql(sql, con=sqlserverCon)

    tradingDay = data['TradingDay'].values[0]
    tradingDayStr = DateUtil.datetime64_2_str(tradingDay)

    # print(tradingDayStr)
    return tradingDayStr

#查询最小日期
def select_min_data(databaseDict,signalColumnDict):
    tradingDayName = signalColumnDict.get(StockConst.TRADING_DAY_NAME)
    windCodeName = signalColumnDict.get(StockConst.WIND_CODE_NAME)
    techName = signalColumnDict.get(StockConst.TECH_NAME)

    signaltablename = databaseDict.get(StockConst.SIGNAL_TABLENAME)

    ms = MSSQLHelper.get_mssql_instance_by_dict(databaseDict)
    # 连接
    sqlserverCon = ms.get_connect()
    sql = 'select min('+tradingDayName+') TradingDay from ' + signaltablename  # SignalDataTable
    data = pd.read_sql(sql, con=sqlserverCon)

    tradingDay = data['TradingDay'].values[0]
    tradingDayStr = DateUtil.datetime64_2_str(tradingDay)

    # print(tradingDayStr)
    return tradingDayStr


# def print_h5():
#     df = SourceDataDao.load_h5(StockConst.ROOT + StockConst.HS300H5)
#     print(df)

if __name__ == '__main__':
    # create_h5()
    # print_h5()
    # tradingDay = select_max_data('SignalDataTable')
    # print(tradingDay)

    columns = get_table_columns("192.168.1.4", "jydb", "jydb", "FishDB", "SignalDataTable")
    print(columns)

    pass