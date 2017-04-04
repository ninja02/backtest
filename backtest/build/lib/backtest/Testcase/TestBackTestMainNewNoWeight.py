import unittest
from backtestData.Dao import SourceDataDao
from backtest.Constance import StockConst
import backtest.Main.BackTestMainNewNoWeight as BackTestMainNew
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


    def testBackTestMain(self):
        techList = [StockConst.MOM]
        signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
        dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
        sliceIdx = None
        numOfDailySignal = 4
        sliceTotalNum = None
        sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
        resultDic = BackTestMainNew.main(BackTestMainNew.select_stock_func1, BackTestMainNew.trade_func1,
                                         techList, sliceDict,signalDataAddr, dailyQuoteAddr, '2005-01-01', '2005-12-31')

    def testBackTestMainVolWeight(self):
        techList = [StockConst.MOM]
        signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
        dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
        sliceIdx = None
        numOfDailySignal = 4
        sliceTotalNum = None
        sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
        resultDic = BackTestMainNew.main(BackTestMainNew.select_stock_func5, BackTestMainNew.trade_func1,
                                         techList, sliceDict,signalDataAddr, dailyQuoteAddr, '2004-01-01', '2005-12-31')

    def testBackTestMainVolWeight(self):
        techList = [StockConst.MOM]
        signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
        dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
        sliceIdx = None
        numOfDailySignal = 4
        sliceTotalNum = None
        sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
        resultDic = BackTestMainNew.main(BackTestMainNew.select_stock_func5, BackTestMainNew.trade_func1,
                                         techList, sliceDict,signalDataAddr, dailyQuoteAddr, '2004-01-01', '2005-12-31')

    #单个切片
    def testBackTestMainSingleSlice(self):
        techList = [StockConst.MOM]
        signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
        dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
        sliceIdx = 98
        numOfDailySignal = 4
        sliceTotalNum = 100
        sliceDict={'sliceIdx':sliceIdx,'numOfDailySignal':numOfDailySignal,'sliceTotalNum':sliceTotalNum}
        resultDic = BackTestMainNew.main(BackTestMainNew.select_stock_func4, BackTestMainNew.trade_func1,
                                         techList, sliceDict, signalDataAddr, dailyQuoteAddr, '2004-01-01', '2005-12-31')

    #全部切片
    def testBackTestMainAllSlice(self):
        techList = [StockConst.MOM]
        signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
        dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
        numOfDailySignal = 4
        sliceTotalNum = 10
        resultDic = BackTestMainNew.processBySlice(BackTestMainNew.select_stock_func4, BackTestMainNew.trade_func1,
                                         techList, sliceTotalNum, numOfDailySignal, signalDataAddr, dailyQuoteAddr, '2004-01-01', '2005-12-31')

    # # 用apply的版本
    # # 回测主函数
    # def testBackTestMain(self):
    #     techList = [StockConst.Mom]
    #     signalDataAddr = StockConst.root + StockConst.signalDataH5
    #     dailyQuoteAddr = StockConst.root + StockConst.newDailyQuoteH5
    #     sliceIdx = None
    #     numOfDailySignal = 3
    #     sliceTotalNum = None
    #     sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
    #     resultDic = BackTestMainNew.main(BackTestMainNew.select_stock_1day_func1, BackTestMainNew.trade_1day_func1,
    #                                   techList, sliceDict, signalDataAddr, dailyQuoteAddr, '2004-01-01', '2005-12-31')

    # 加权
    # 回测主函数
    def testBackTestMainWeight(self):
        techList = [StockConst.MOM, 'Momp']
        signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
        dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
        sliceIdx = None
        numOfDailySignal = 5
        sliceTotalNum = None
        sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal,'sliceTotalNum': sliceTotalNum}
        resultDic = BackTestMainNew.main(BackTestMainNew.select_stock_func3, BackTestMainNew.trade_func1,
                                         techList, sliceDict, signalDataAddr, dailyQuoteAddr, '2004-01-01', '2005-12-31')

    # 回测主函数
    def testBackTestMainHill(self):
        techList = [StockConst.MOM]
        signalDataAddr = StockConst.ROOT + '/export/SignalDataHill.h5'
        dailyQuoteAddr = StockConst.ROOT + '/export/DailyQuoteHill.h5'
        sliceIdx = None
        numOfDailySignal = 5
        sliceTotalNum = None
        sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal,'sliceTotalNum': sliceTotalNum}
        resultDic = BackTestMainNew.main(BackTestMainNew.select_stock_func1, BackTestMainNew.trade_func1,
                                         techList, sliceDict, signalDataAddr, dailyQuoteAddr,'2004-01-01','2005-12-31')
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

    def testSelect_stock_func3(self):
        signalData = SourceDataDao.load_signal_data('')
        techList=[StockConst.MOM, 'Momp']
        BackTestMainNew.select_stock_func3(signalData, techList)

    def testSelect_stock_func1(self):
        signalData = SourceDataDao.load_signal_data('')
        techList=[StockConst.MOM]
        sliceIdx = None
        numOfDailySignal = 5
        sliceTotalNum = None
        sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
        groupedSignalData = BackTestMainNew.select_stock_func1(signalData, techList, sliceDict)
        currSignalData = groupedSignalData.xs('2005-01-05').xs('2005-01-05')
        entity=currSignalData.ix['000950.SZ']
        print(entity)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    # suite.addTest(TestBackTestMainNew("testSelectByInnerCodeAndDate"))
    # suite.addTest(TestBackTestMainNew("testPrintByInnerCode"))
    # suite.addTest(TestBackTestMainNew("testAddBuySellFlgAndExport"))
    suite.addTest(TestBackTestMainNew("testBackTestMain"))
    # suite.addTest(TestBackTestMainNew("testBackTestMainVolWeight"))
    # suite.addTest(TestBackTestMainNew("testBackTestMainSingleSlice"))
    # suite.addTest(TestBackTestMainNew("testBackTestMainAllSlice"))
    # suite.addTest(TestBackTestMainNew("testBackTestMainWeight"))
    # suite.addTest(TestBackTestMainNew("testBackTestMainHill"))
    # suite.addTest(TestBackTestMainNew("testSelect_stock_func3"))
    # suite.addTest(TestBackTestMainNew("testSelect_stock_func1"))

    runner = unittest.TextTestRunner()
    runner.run(suite)