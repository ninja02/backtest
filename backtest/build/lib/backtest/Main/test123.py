import  pandas as pd
class trade1day():
    def __init__(self):
        self.pre_position = []
    def deal(self,today_frm):
        tradingDay = today_frm.index.get_level_values(0).unique()
        rec_list = today_frm.index.get_level_values(1)
        buy_list = set(rec_list) - set(self.pre_position)
        self.pre_position = set(rec_list)
        print('tradingDay:')
        print(tradingDay)
        print('buy_list:')
        print(buy_list)
        print('pre_position:')
        print(self.pre_position)




mi_index = pd.MultiIndex.from_product([pd.date_range(start='2010-01-01',end='2010-01-02'),[1,3,4]], names = ['TradingDay','Top'])
top_frm = pd.DataFrame(index= mi_index, columns=['Weight'])
top_frm['Weight'] = 0.2
frm_gb = top_frm.groupby(level = 'TradingDay')
# t1d = trade1day()
res = frm_gb.apply(trade1day().deal)