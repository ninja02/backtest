import backtest.Main.BackTestMainNew as func_pool
from backtest.Constance import StockConst


class BTWorkFlow():
    def __init__(self, flow, flow_to_funcno_mapping, func_args_mapping):
        '''
        :param flow: {'root':1, 1:[2], 2:[3]}
        :param flow_mapping: {1: '0', 2:'1',3:'3'}
        :param func_args: {1: {'top':5}, 2:{'percentage':'10'}}
        '''
        self.flow = flow
        self.flow_to_funcno_mapping = flow_to_funcno_mapping
        self.func_args_mapping = func_args_mapping
        #返回值用于下一步参数的参数名
        self.func_args_result = {'initial_func':'global_dict',
                                 'read_func':'global_dict',
                                 'select_stock_func':'global_dict',
                                 'get_start_end_date': 'global_dict',
                                 'trade_func_main': 'global_dict',
                                 'performance_func': 'global_dict',
                                 }
        #方法表
        # self.FUNC_MAPPING = {'a': func_pool.read_func1,'b': func_pool.select_stock_func1,'c': func_pool.select_stock_func2, 'd':func_pool.trade_func1,}
        self.FUNC_MAPPING = {'initial_func': func_pool.initial_func,
                             'read_func': func_pool.read_func1,
                             'select_stock_func': func_pool.select_stock_func5,
                             'get_start_end_date': func_pool.get_start_end_date,
                             'trade_func_main': func_pool.trade_func_main1,
                             'performance_func': func_pool.performance_func,
                             }

    def execute_flow(self):
        def execute(node_i, last_step_result):
            funcno = self.flow_to_funcno_mapping[node_i]
            # print('funcno:'+funcno)
            func = self.FUNC_MAPPING[funcno]
            #上一步的返回值，加入到参数列表
            if last_step_result is not None:
                #返回值用于下一步参数的参数名
                result_arg_name = self.func_args_result[funcno]
                #加入到参数列表中
                func_args = self.func_args_mapping[funcno]
                func_args[result_arg_name] = last_step_result
                # print('func_args_mapping')
                # print(list(func_args.keys()))
                # print(self.func_args_mapping[funcno])
            func_args = self.func_args_mapping[funcno]
            # if funcno == 'select_stock_func':
            #     print(func_args)
            return func(**func_args)


        # root_node = self.flow['root']
        # print('root_node:' + str(root_node))
        # current_res = execute(root_node, res= None)
        # node_i = root_node

        # key = None
        # print(list(self.flow.keys()))

        #不能为None
        current_res = {}
        for key in list(self.flow.keys()):
            print('key:' + str(key))
            node_i = self.flow[key][0]
            # print('node_i:'+str(node_i))
            current_res = execute(node_i, current_res)

        return current_res

if __name__ == '__main__':
    #####################################################################################
    techList = [StockConst.MOM]
    # signalDataAddr = StockConst.ROOT + StockConst.SIGNAL_DATA_H5
    # signalDataAddr = StockConst.ROOT + '/0_Data/DataCsv.csv';
    # databaseDict = None
    signalDataAddr = None  # read file
    databaseDict = {StockConst.IP: '192.168.1.4', StockConst.ACCOUNT: 'jydb', StockConst.PASSWORD: 'jydb',
                    StockConst.DATABASE: 'FishDB', StockConst.SIGNAL_TABLENAME: 'SignalDataTable'}

    dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
    indexQuoteAddr = StockConst.ROOT + StockConst.FAKE_INDEX_QUOTE_H5_2  # 基准（算相对收益）
    benchmark = StockConst.HS300_CODE  # 基准（算相对收益）
    sliceIdx = None
    numOfDailySignal = 4
    sliceTotalNum = None
    doPlot = True
    sliceDict = {'sliceIdx': sliceIdx, 'numOfDailySignal': numOfDailySignal, 'sliceTotalNum': sliceTotalNum}
    # signalColumnDict = {StockConst.TRADING_DAY_NAME: 'TradingDay1', StockConst.WIND_CODE_NAME: 'WindCode1', StockConst.TECH_NAME: 'Mom'}
    signalColumnDict = {StockConst.TRADING_DAY_NAME: 'TradingDay', StockConst.WIND_CODE_NAME: 'WindCode',
                        StockConst.TECH_NAME: 'Mom'}
    #####################################################################################


    flow = {0: [1], 1: [2], 2: [3], 3: [4], 4: [5], 5: [6]} #流程1,2,3..., 0是根节点不执行
    flow_to_funcno_mapping = {1: 'initial_func',
                              2: 'read_func',
                              3: 'select_stock_func',
                              4: 'get_start_end_date',
                              5: 'trade_func_main',
                              6: 'performance_func'
                              } #流程和方法号的对应关系
    func_args_mapping = {'initial_func':        {'dailyQuoteAddr': dailyQuoteAddr,'indexQuoteAddr': indexQuoteAddr,'benchmark': benchmark,'doPlot':doPlot},
                         'read_func':           {'signalDataAddr': signalDataAddr,'databaseDict': databaseDict,'signalColumnDict': signalColumnDict},
                         'select_stock_func':  {'tech_list': techList,'slice_dict': sliceDict},
                         'get_start_end_date': {},
                         'trade_func_main':    {},
                         'performance_func':   {}
                         } #方法号和方法参数的对应关系
    wf = BTWorkFlow(flow, flow_to_funcno_mapping, func_args_mapping)
    current_res = wf.execute_flow()

    #4.result
    stockStatDailyDf = current_res['stockStatDailyDf']
    tradingDayList = list(stockStatDailyDf.index.astype(str))
    netValueList = stockStatDailyDf['netValue'].tolist()

    print('tradingDayList:' + str(len(tradingDayList)))
    print('netValueList:' + str(len(netValueList)))
