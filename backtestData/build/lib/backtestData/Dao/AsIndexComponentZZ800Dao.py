from backtestData.Dao import MSSQL
from backtestData.Dao import MSSQLHelper
import pandas as pd
from backtestData.Constance import StockConst
from backtestData.Dao import SourceDataDao

def create_h5():

    ## ms = MSSQL(host="localhost",user="sa",pwd="123456",db="PythonWeiboStatistics")
    ## #返回的是一个包含tuple的list，list的元素是记录行，tuple的元素是每行记录的字段
    ## ms.ExecNonQuery("insert into WeiBoUser values('2','3')")

    # ms = MSSQLHelper.getMSSQLInstance()
    #
    # #连接
    # sqlserverCon = ms.getConnect()
    # sql = 'SELECT NatureDay,WindCode,IfTradingDay FROM AsIndexComponentZZ500 order by NatureDay,WindCode'
    #
    # # resList = ms.ExecQuery(sql)
    # # for (NatureDay,WindCode,IfTradingDay) in resList:
    # #     print(str(NatureDay) + ' ' + str(WindCode) + ' ' + str(IfTradingDay))
    #
    # #sqlserrver转成h5
    # df = pd.read_sql(sql, con=sqlserverCon)
    # print('df:')
    # print(df)
    # exportToHDFStore(df, StockConst.root + '/' + targetAddr + '.h5')

    hs300df = SourceDataDao.load_h5(StockConst.ROOT + StockConst.HS300H5)
    zz500df = SourceDataDao.load_h5(StockConst.ROOT + StockConst.ZZ500H5)
    zz800df = hs300df.append(zz500df)
    zz800df = zz800df.sort_values(by=['NatureDay','WindCode'],ascending=True)

    SourceDataDao.export_to_hdfstore(zz800df, StockConst.ROOT + StockConst.ZZ800H5)

    # sqlserverCon.close()

def print_h5():
    df = SourceDataDao.load_h5(StockConst.ROOT + StockConst.ZZ800H5)
    print(df)

if __name__ == '__main__':
    create_h5()