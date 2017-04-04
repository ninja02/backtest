from pyspark import SparkConf,SparkContext
from pyspark.sql import HiveContext,Row
from backtestData.Dao import SourceDataDao
from backtest.Constance import StockConst
import backtest.Main.BackTestMainNew as BackTestMainNew
from backtest.Util import SelectUtil

def test_back_test_main_vol_weight():
    techList = [StockConst.MOM]
    # signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
    signalDataAddr = 'D:\\0_Data\\Mom_basedon_HS300.h5'

    # signalDataAddr = StockConst.ROOT + '/signalDataCsv.csv';
    # signalDataAddr = StockConst.ROOT + '/Data.xls';
    # signalDataAddr = StockConst.ROOT + '/DataCsv.csv';
    table_name = None
    # signalDataAddr = None # read file
    # table_name = 'SignalDataTable' # read mssql

    dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
    indexQuoteAddr = StockConst.ROOT + StockConst.FAKE_INDEX_QUOTE_H5_2  # 基准（算相对收益）
    benchmark = StockConst.HS300_CODE  # 基准（算相对收益）
    sliceIdx = None
    numOfDailySignal = 4
    sliceTotalNum = None
    doPlot = True
    sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
    resultDic = BackTestMainNew.main(BackTestMainNew.read_func1, select_func_6,
                                     BackTestMainNew.trade_func1,
                                     techList, sliceDict, signalDataAddr, dailyQuoteAddr, indexQuoteAddr, benchmark,
                                     '2005-01-04', '2006-01-10', doPlot, table_name)


def main():
    signalDataDf = SourceDataDao.read_file_set_index('D:\\0_Data\\Mom_basedon_HS300.h5')

    techList = [StockConst.MOM]

    sliceIdx = None
    numOfDailySignal = 4
    sliceTotalNum = None
    sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}

    allSelectStockDf = select_func_6(signalDataDf,techList,sliceDict)

def select_func_6(signalDataDf,techList,sliceDict):

    numOfDailySignal = sliceDict.get('numOfDailySignal')

    conf = SparkConf().setAppName("spark_infer_schema")

    sc = SparkContext(conf=conf)

    hc = HiveContext(sc)

    # 读入数据

    signalDataDf = signalDataDf.reset_index(drop=False)
    signalDataDf.rename(columns={'level_0':'TradingDay', 'level_1':'WindCode'},inplace=True)
    signalDataDf['TradingDay'] = signalDataDf['TradingDay'].astype('str')
    # print(signalDataDf)

    # 转成spark dataframe
    signalDataSpDf = hc.createDataFrame(signalDataDf)
    # print('signalDataSpDf')
    # signalDataSpDf.printSchema()
    # print(signalDataSpDf)

    signalDataSpDf.registerTempTable("signalData")

    # 分组排序
    sql="select TradingDay,WindCode,Mom from ( " + \
	    "select TradingDay,WindCode,Mom,row_number() OVER (PARTITION BY TradingDay ORDER BY Mom DESC) rank from signalData" + \
	    ") tmp where rank<=" + str(numOfDailySignal)
    allSelectStockSpDf = hc.sql(sql)
    # print('allSelectStockSpDf')
    # allSelectStockSpDf.printSchema()
    # allSelectStockSpDf.show()

    # 转成pandas dataframe
    allSelectStockDf = allSelectStockSpDf.toPandas()
    allSelectStockDf['TradingDay'] = allSelectStockDf['TradingDay'].astype('datetime64')
    allSelectStockDf = allSelectStockDf.set_index([StockConst.TRADINGDAY,StockConst.INNERCODE])
    # print('allSelectStockDf')
    # print(allSelectStockDf)

    # allSelectStockDf = SelectUtil.getTopNAndInsertVolWeight(numOfDailySignal, allSelectStockDf)
    volWeight = 1/numOfDailySignal
    allSelectStockDf.insert(len(allSelectStockDf.columns), 'volWeight', volWeight)
    print(allSelectStockDf)

    return allSelectStockDf






if __name__ == '__main__':
    test_back_test_main_vol_weight()

# #仓位权重
# def test_back_test_main_vol_weight(self):
#     techList = [StockConst.MOM]
#     signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
#     # signalDataAddr = StockConst.ROOT + '/signalDataCsv.csv';
#     # signalDataAddr = StockConst.ROOT + '/Data.xls';
#     # signalDataAddr = StockConst.ROOT + '/DataCsv.csv';
#     table_name = None
#     # signalDataAddr = None # read file
#     # table_name = 'SignalDataTable' # read mssql
#
#     dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
#     indexQuoteAddr = StockConst.ROOT + StockConst.FAKE_INDEX_QUOTE_H5_2 # 基准（算相对收益）
#     benchmark = StockConst.HS300_CODE # 基准（算相对收益）
#     sliceIdx = None
#     numOfDailySignal = 4
#     sliceTotalNum = None
#     doPlot = True
#     sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
#     resultDic = BackTestMainNew.main(BackTestMainNew.read_func1, BackTestMainNew.select_stock_func5, BackTestMainNew.trade_func1,
#                                      techList, sliceDict,signalDataAddr, dailyQuoteAddr, indexQuoteAddr, benchmark, '2005-01-04', '2006-01-10', doPlot, table_name)