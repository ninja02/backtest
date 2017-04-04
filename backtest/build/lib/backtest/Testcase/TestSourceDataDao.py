import unittest
from backtestData.Dao import SourceDataDao

class TestSourceDataDao(unittest.TestCase):
    # def sum(self, a, b):
    #     return a+b

    ##初始化工作
    def setUp(self):
        #self.tclass = myclass.myclass()  ##实例化了被测试模块中的类
        pass

    # 退出清理工作
    def tearDown(self):
        pass

    def testLoadDailyQuote(self):
        dailyQuote = SourceDataDao.load_daily_quote('')
        # self.assertEqual(self.sum(1, 2), 3)
        print('dailyQuote:'+str(len(dailyQuote)))
        self.assertNotEqual(len(dailyQuote), 0)

    def testLoadSignalData(self):
        signalData = SourceDataDao.load_signal_data('')
        # self.assertEqual(self.sum(1, 2), 3)
        print('signalData:' + str(len(signalData)))
        self.assertNotEqual(len(signalData), 0)

    def testLoadSignalDataByDate(self):
        signalData = SourceDataDao.load_signal_data_by_date('2004-01-01', '2004-01-10', '')
        # self.assertEqual(self.sum(1, 2), 3)
        print('signalData:' + str(len(signalData)))
        print(signalData)
        self.assertNotEqual(len(signalData), 0)

    def testLoadNewDailyQuote(self):
        newDailyQuote = SourceDataDao.load_new_daily_quote('')
        # self.assertEqual(self.sum(1, 2), 3)
        print('newDailyQuote:'+str(len(newDailyQuote)))
        self.assertNotEqual(len(newDailyQuote), 0)

    def testSelectByInnerCodeAndDate(self):
        dailyQuote = SourceDataDao.load_new_daily_quote('')
        dailyQuote = SourceDataDao.select_by_inner_code_and_date(dailyQuote, '2004-09-14', '000049.SZ')
        # self.assertEqual(self.sum(1, 2), 3)
        print('dailyQuote:'+str(len(dailyQuote)))
        print(dailyQuote)
        self.assertNotEqual(len(dailyQuote), 0)

    def testSelectSignalByDateAndInnerCode(self):
        signalData = SourceDataDao.load_signal_data('')
        signalData = SourceDataDao.select_signal_by_date_and_inner_code(signalData, '2004-01-31', '000049.SZ')
        # self.assertEqual(self.sum(1, 2), 3)
        print('signalData:'+str(len(signalData)))
        #print(signalData)
        self.assertNotEqual(len(signalData), 0)

    def testCheckIfCannotBuy(self):
        dailyQuote = SourceDataDao.load_new_daily_quote('')

        #双休日
        checkResult = SourceDataDao.check_if_cannot_buy(dailyQuote, '2004-01-31', '000049.SZ')
        print('checkResult:'+str(checkResult))
        #print(signalData)
        self.assertTrue(checkResult)

        #双休日
        checkResult = SourceDataDao.check_if_cannot_buy(dailyQuote, '2004-02-01', '000049.SZ')
        print('checkResult:' + str(checkResult))
        # print(signalData)
        self.assertTrue(checkResult)

        #一字涨停
        checkResult = SourceDataDao.check_if_cannot_buy(dailyQuote, '2004-02-02', '000049.SZ')
        print('checkResult:' + str(checkResult))
        # print(signalData)
        self.assertTrue(checkResult)

        #正常
        checkResult = SourceDataDao.check_if_cannot_buy(dailyQuote, '2004-02-05', '000049.SZ')
        print('checkResult:' + str(checkResult))
        # print(signalData)
        self.assertFalse(checkResult)

    def testCheckIfCannotSell(self):
        dailyQuote = SourceDataDao.load_new_daily_quote('')

        #停牌
        checkResult = SourceDataDao.check_if_cannot_sell(dailyQuote, '2004-09-12', '000049.SZ')
        print('checkResult:'+str(checkResult))
        #print(signalData)
        self.assertTrue(checkResult)

        #一字跌停
        checkResult = SourceDataDao.check_if_cannot_sell(dailyQuote, '2004-09-13', '000049.SZ')
        print('checkResult:' + str(checkResult))
        # print(signalData)
        self.assertTrue(checkResult)

        #一字跌停
        checkResult = SourceDataDao.check_if_cannot_sell(dailyQuote, '2004-09-14', '000049.SZ')
        print('checkResult:' + str(checkResult))
        # print(signalData)
        self.assertTrue(checkResult)

        #一字跌停
        checkResult = SourceDataDao.check_if_cannot_sell(dailyQuote, '2004-09-15', '000049.SZ')
        print('checkResult:' + str(checkResult))
        # print(signalData)
        self.assertTrue(checkResult)

        #正常
        checkResult = SourceDataDao.check_if_cannot_sell(dailyQuote, '2004-09-16', '000049.SZ')
        print('checkResult:' + str(checkResult))
        # print(signalData)
        self.assertFalse(checkResult)

    # tradingDate前最后一个交易日
    def testSelectByPrevTradingDay(self):
        dailyQuote = SourceDataDao.load_new_daily_quote('')

        df = SourceDataDao.select_by_prev_tradingday(dailyQuote, '2004-09-12', '000049.SZ')
        print(df)
        #print(signalData)
        self.assertNotEqual(len(df), 0)


    #打印个股行情，导出到excel
    def testPrintByInnerCode(self):
        SourceDataDao.printByInnerCode('000049.SZ')

    #加BuyFlg SellFlg到行情数据, 导出到NewDailyQuote.h5
    def testAddBuySellFlgAndExport(self):
        SourceDataDao.addBuySellFlgAndExport('')

    #
    def testaddBuySellFlgToSignalData(self):
        SourceDataDao.addBuySellFlgToSignalData('')

    #
    def testaddBuySellFlgToSignalData2(self):
        SourceDataDao.addBuySellFlgToSignalData2('')

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestSourceDataDao("testSelectByInnerCodeAndDate"))
    # suite.addTest(TestSourceDataDao("testPrintByInnerCode"))
    # suite.addTest(TestSourceDataDao("testAddBuySellFlgAndExport"))
    # suite.addTest(TestSourceDataDao("testCheckIfCannotSell"))
    # suite.addTest(TestSourceDataDao("testSelectByPrevTradingDay"))
    # suite.addTest(TestSourceDataDao("testLoadSignalDataByDate"))
    # suite.addTest(TestSourceDataDao("testaddBuySellFlgToSignalData"))
    # suite.addTest(TestSourceDataDao("testaddBuySellFlgToSignalData2"))

    runner = unittest.TextTestRunner()
    runner.run(suite)

    # unittest.main()