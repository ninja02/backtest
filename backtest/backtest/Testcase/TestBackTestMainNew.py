import unittest
from backtestData.Dao import SourceDataDao
from backtest.Constance import StockConst
import backtest.Main.BackTestMainNew as BackTestMainNew #BackTestMainNew20170328  BackTestMainNew
import math
import pandas as pd
from backtest.Util import DateUtil

class TestBackTestMainNew(unittest.TestCase):
    # def sum(self, a, b):
    #     return a+b

    ##初始化工作
    def setUp(self):
        #self.tclass = myclass.myclass()  ##实例化了被测试模块中的类
        pass

    # 退出清理工作
    def tearDown(self):
        pass


    #弃用
    def test_back_test_main(self):
        techList = [StockConst.MOM]
        signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
        table_name = None
        dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
        indexQuoteAddr = StockConst.ROOT + StockConst.FAKE_INDEX_QUOTE_H5_2  # 基准（算相对收益）
        benchmark = StockConst.HS300_CODE  # 基准（算相对收益）
        sliceIdx = None
        numOfDailySignal = 3
        sliceTotalNum = None
        doPlot = True
        sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
        resultDic = BackTestMainNew.main(BackTestMainNew.read_func1, BackTestMainNew.select_stock_func1, BackTestMainNew.trade_func1,
                                         techList, sliceDict,signalDataAddr, dailyQuoteAddr, indexQuoteAddr, benchmark, '2005-01-04', '2005-12-31', doPlot, table_name)

    #沪深300成分股过滤后的信号
    def test_back_test_main_hs300(self):
        techList = [StockConst.MOM]
        signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_BASEDON_HS300 #和沪深300成分股合并后的信号
        databaseDict = None
        # signalDataAddr = StockConst.ROOT + StockConst.signalDataBasedOnZZ500
        # signalDataAddr = StockConst.ROOT + StockConst.signalDataBasedOnZZ800
        # signalDataAddr = None
        # databaseDict = {StockConst.IP: '192.168.1.4', StockConst.ACCOUNT: 'jydb', StockConst.PASSWORD: 'jydb',StockConst.DATABASE: 'FishDB', StockConst.SIGNAL_TABLENAME: 'SignalDataTable'}

        dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
        # indexQuoteAddr = ''#无沪深行情时指数涨幅默认0
        # benchmark = ''
        indexQuoteAddr = StockConst.ROOT + StockConst.FAKE_INDEX_QUOTE_H5_2  # 基准（算相对收益）
        benchmark = StockConst.HS300_CODE  # 基准（算相对收益）
        sliceIdx = None
        numOfDailySignal = 4
        sliceTotalNum = None
        doPlot = True
        sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
        signalColumnDict = {StockConst.TRADING_DAY_NAME: 'TradingDay', StockConst.WIND_CODE_NAME: 'WindCode',StockConst.TECH_NAME: 'Mom'}
        resultDic = BackTestMainNew.main(BackTestMainNew.read_func1, BackTestMainNew.select_stock_func5, BackTestMainNew.trade_func1,
                                         techList, sliceDict,signalDataAddr, dailyQuoteAddr, indexQuoteAddr, benchmark, '2005-04-08', '2005-12-31', doPlot, databaseDict, signalColumnDict)

    #仓位权重
    def test_back_test_main_vol_weight(self):
        techList = [StockConst.MOM]
        # signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
        # signalDataAddr = StockConst.ROOT + '/0_Data/DataCsv.csv';
        # databaseDict = None
        signalDataAddr = None # read file
        databaseDict = {StockConst.IP: '192.168.1.4', StockConst.ACCOUNT: 'jydb',StockConst.PASSWORD: 'jydb',StockConst.DATABASE: 'FishDB',StockConst.SIGNAL_TABLENAME: 'SignalDataTable'}

        dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
        indexQuoteAddr = StockConst.ROOT + StockConst.FAKE_INDEX_QUOTE_H5_2 # 基准（算相对收益）
        benchmark = StockConst.HS300_CODE # 基准（算相对收益）
        sliceIdx = None
        numOfDailySignal = 4
        sliceTotalNum = None
        doPlot = True
        sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
        # signalColumnDict = {StockConst.TRADING_DAY_NAME: 'TradingDay1', StockConst.WIND_CODE_NAME: 'WindCode1', StockConst.TECH_NAME: 'Mom'}
        signalColumnDict = {StockConst.TRADING_DAY_NAME: 'TradingDay', StockConst.WIND_CODE_NAME: 'WindCode',StockConst.TECH_NAME: 'Mom'}
        resultDic = BackTestMainNew.main(BackTestMainNew.read_func1, BackTestMainNew.select_stock_func5, BackTestMainNew.trade_func_main1,
                                         techList, sliceDict,signalDataAddr, dailyQuoteAddr, indexQuoteAddr, benchmark, '2005-01-04', '2006-01-10', doPlot, databaseDict, signalColumnDict)

    def test_back_test_main_flow(self):
        techList = [StockConst.MOM]
        # signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
        # signalDataAddr = StockConst.ROOT + '/0_Data/DataCsv.csv';
        # databaseDict = None
        signalDataAddr = None # read file
        databaseDict = {StockConst.IP: '192.168.1.4', StockConst.ACCOUNT: 'jydb',StockConst.PASSWORD: 'jydb',StockConst.DATABASE: 'FishDB',StockConst.SIGNAL_TABLENAME: 'SignalDataTable'}

        dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
        indexQuoteAddr = StockConst.ROOT + StockConst.FAKE_INDEX_QUOTE_H5_2 # 基准（算相对收益）
        benchmark = StockConst.HS300_CODE # 基准（算相对收益）
        sliceIdx = None
        numOfDailySignal = 4
        sliceTotalNum = None
        doPlot = True
        sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
        # signalColumnDict = {StockConst.TRADING_DAY_NAME: 'TradingDay1', StockConst.WIND_CODE_NAME: 'WindCode1', StockConst.TECH_NAME: 'Mom'}
        signalColumnDict = {StockConst.TRADING_DAY_NAME: 'TradingDay', StockConst.WIND_CODE_NAME: 'WindCode',StockConst.TECH_NAME: 'Mom'}
        resultDic = BackTestMainNew.main(BackTestMainNew.read_func1, BackTestMainNew.select_stock_func5, BackTestMainNew.trade_func_main1,
                                         techList, sliceDict,signalDataAddr, dailyQuoteAddr, indexQuoteAddr, benchmark, '2005-01-04', '2006-01-10', doPlot, databaseDict, signalColumnDict)

    #单个切片 TODO
    def test_back_test_main_single_slice(self):
        techList = [StockConst.MOM]
        # signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
        signalDataAddr = StockConst.ROOT + '/0_Data/Mom_basedon_HS300.h5'
        databaseDict = None
        # signalDataAddr = None  # read file
        # databaseDict = {StockConst.IP: '192.168.1.4', StockConst.ACCOUNT: 'jydb', StockConst.PASSWORD: 'jydb', StockConst.DATABASE: 'FishDB', StockConst.SIGNAL_TABLENAME: 'SignalDataTable'}

        dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
        indexQuoteAddr = StockConst.ROOT + StockConst.FAKE_INDEX_QUOTE_H5_2  # 基准（算相对收益）
        benchmark = StockConst.HS300_CODE  # 基准（算相对收益）
        sliceIdx = 2
        numOfDailySignal = 4
        sliceTotalNum = 100
        doPlot = True
        sliceDict={'sliceIdx':sliceIdx,'numOfDailySignal':numOfDailySignal,'sliceTotalNum':sliceTotalNum}
        signalColumnDict = {StockConst.TRADING_DAY_NAME: 'TradingDay', StockConst.WIND_CODE_NAME: 'WindCode',StockConst.TECH_NAME: 'Mom'}
        resultDic = BackTestMainNew.main(BackTestMainNew.read_func1, BackTestMainNew.select_stock_func4, BackTestMainNew.trade_func1,
                                         techList, sliceDict, signalDataAddr, dailyQuoteAddr, indexQuoteAddr, benchmark, '2005-01-04', '2005-12-31', doPlot, databaseDict, signalColumnDict)

    #全部切片
    def test_back_test_main_all_slice(self):
        techList = [StockConst.MOM]
        signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
        dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
        indexQuoteAddr = StockConst.ROOT + StockConst.FAKE_INDEX_QUOTE_H5_2  # 基准（算相对收益）
        benchmark = StockConst.HS300_CODE  # 基准（算相对收益）
        numOfDailySignal = 4
        sliceTotalNum = 10
        doPlot = True
        resultDic = BackTestMainNew.processBySlice(BackTestMainNew.select_stock_func4, BackTestMainNew.trade_func1,
                                         techList, sliceTotalNum, numOfDailySignal, signalDataAddr, dailyQuoteAddr, '2004-01-01', '2005-12-31',doPlot)

    # # 用apply的版本
    # # 回测主函数
    # def testBackTestMain(self):
    #     techList = [StockConst.Mom]
    #     signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
    #     dailyQuoteAddr = StockConst.ROOT + StockConst.newDailyQuoteH5
    #     sliceIdx = None
    #     numOfDailySignal = 3
    #     sliceTotalNum = None
    #     sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
    #     resultDic = BackTestMainNew.main(BackTestMainNew.select_stock_1day_func1, BackTestMainNew.trade_1day_func1,
    #                                   techList, sliceDict, signalDataAddr, dailyQuoteAddr, '2004-01-01', '2005-12-31')

    # 加权
    # 回测主函数
    def test_back_test_main_weight(self):
        techList = [StockConst.MOM, 'Momp']
        signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
        databaseDict = None
        # signalDataAddr = None  # read file
        # databaseDict = {StockConst.IP: '192.168.1.4', StockConst.ACCOUNT: 'jydb', StockConst.PASSWORD: 'jydb', StockConst.DATABASE: 'FishDB', StockConst.SIGNAL_TABLENAME: 'SignalDataTable'}

        dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
        indexQuoteAddr = StockConst.ROOT + StockConst.FAKE_INDEX_QUOTE_H5_2  # 基准（算相对收益）
        benchmark = StockConst.HS300_CODE  # 基准（算相对收益）
        sliceIdx = None
        numOfDailySignal = 5
        sliceTotalNum = None
        doPlot = True
        sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal,'sliceTotalNum': sliceTotalNum}
        signalColumnDict = {StockConst.TRADING_DAY_NAME: 'TradingDay', StockConst.WIND_CODE_NAME: 'WindCode',StockConst.TECH_NAME: 'Mom'}
        resultDic = BackTestMainNew.main(BackTestMainNew.read_func1, BackTestMainNew.select_stock_func3, BackTestMainNew.trade_func1,
                                         techList, sliceDict, signalDataAddr, dailyQuoteAddr, indexQuoteAddr, benchmark, '2004-01-01', '2005-12-31', doPlot, databaseDict, signalColumnDict)

    # 回测主函数
    def test_back_test_main_hill(self):
        techList = [StockConst.MOM]
        signalDataAddr = StockConst.ROOT + '/export/SignalDataHill.h5'
        databaseDict = None
        dailyQuoteAddr = StockConst.ROOT + '/export/DailyQuoteHill.h5'
        indexQuoteAddr = StockConst.ROOT + StockConst.FAKE_INDEX_QUOTE_H5_2  # 基准（算相对收益）
        benchmark = StockConst.HS300_CODE  # 基准（算相对收益）
        sliceIdx = None
        numOfDailySignal = 5
        sliceTotalNum = None
        doPlot = True
        sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal,'sliceTotalNum': sliceTotalNum}
        signalColumnDict = {StockConst.TRADING_DAY_NAME: 'TradingDay', StockConst.WIND_CODE_NAME: 'WindCode',StockConst.TECH_NAME: 'Mom'}
        resultDic = BackTestMainNew.main(BackTestMainNew.read_func1, BackTestMainNew.select_stock_func1, BackTestMainNew.trade_func1,
                                         techList, sliceDict, signalDataAddr, dailyQuoteAddr,indexQuoteAddr, benchmark, '2005-01-04','2005-12-31', doPlot, databaseDict, signalColumnDict)
        # result = resultDic['result']

        #校验结果（每日净值）
        stockStatDailyDf = resultDic['stockStatDailyDf']
        rowno = 1
        lastNetValue = 0
        for index, row in stockStatDailyDf.iterrows():
            netValue = row['netValue']
            tradeday = index
            if rowno > 1:
                if tradeday <= pd.Timestamp('2004-07-01'):
                    diff = lastNetValue * (1.001) - netValue
                    print(DateUtil.datetime2_str(tradeday) + ' ' + str(netValue) + ' ' + str(diff))
                    self.assertTrue(abs(diff) < 0.000000001)

                elif tradeday >= pd.Timestamp('2004-07-03'):
                    diff = lastNetValue * (0.999) - netValue
                    print(DateUtil.datetime2_str(tradeday) + ' ' + str(netValue) + ' ' + str(diff))
                    self.assertTrue(abs(diff) < 0.000000001)

                else:
                    print(DateUtil.datetime2_str(tradeday) + ' ' + str(netValue))

            lastNetValue = netValue
            rowno += 1

    def test_select_stock_func3(self):
        signalData = SourceDataDao.load_signal_data('')
        techList=[StockConst.MOM, 'Momp']
        BackTestMainNew.select_stock_func3(signalData, techList)

    def test_select_stock_func1(self):
        signalData = SourceDataDao.read_file_set_index(StockConst.ROOT + StockConst.SIGNAL_DATA_H5)
        techList=[StockConst.MOM]
        sliceIdx = None
        numOfDailySignal = 4
        sliceTotalNum = None
        sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
        groupedSignalData = BackTestMainNew.select_stock_func1(signalData, techList, sliceDict)
        currSignalData = groupedSignalData.xs('2005-01-05')
        entity=currSignalData.ix['000950.SZ']
        print(entity)

    # def test_

if __name__ == '__main__':
    suite = unittest.TestSuite()
    # suite.addTest(TestBackTestMainNew("testSelectByInnerCodeAndDate"))
    # suite.addTest(TestBackTestMainNew("testPrintByInnerCode"))
    # suite.addTest(TestBackTestMainNew("testAddBuySellFlgAndExport"))
    # suite.addTest(TestBackTestMainNew("test_back_test_main"))
    # suite.addTest(TestBackTestMainNew("testBackTestMainHS300"))
    suite.addTest(TestBackTestMainNew("test_back_test_main_vol_weight"))
    # suite.addTest(TestBackTestMainNew("test_back_test_main_single_slice"))
    # suite.addTest(TestBackTestMainNew("testBackTestMainAllSlice"))
    # suite.addTest(TestBackTestMainNew("test_back_test_main_weight"))
    # suite.addTest(TestBackTestMainNew("test_back_test_main_hill"))
    # suite.addTest(TestBackTestMainNew("testSelect_stock_func3"))
    # suite.addTest(TestBackTestMainNew("test_select_stock_func1"))

    runner = unittest.TextTestRunner()
    runner.run(suite)