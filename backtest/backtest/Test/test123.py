import pandas as pd
import numpy as np
from numpy import nan as NA
from backtest.Util import DateUtil
from backtest.Util import NumUtil
from pandas import Series, DataFrame
from backtest.Entity import CapitalEntity
from backtest.Constance import StockConst
import calendar,time
import random
import copy


arr = np.arange(10);
# print(arr[5:8]);

sdata = {'A': 111, 'B':222, 'C':333}
obj3 = Series(sdata)


#print(len(sdata));

# print(obj3.isnull());

df = pd.DataFrame(
    {'AAA' : [4,5,6,7],
     'BBB' : [10,20,30,40],
     'CCC' : [100,50,-30,-50],
     'DDD' : ['2015-01-01','2015-01-02','2015-01-03','2015-01-04']
    },
    index=['a','b','c','d']
);

df2 = pd.DataFrame(
    {'AAA' : [4,5,6,7],
     'BBB' : [10,20,30,40],
     'CCC' : [100,50,-30,-50]
    },
    index=['a','b','c','d']
);

ef = pd.DataFrame(
    {'AAA' : [4,5,6],
     'BBB' : [10,20,30],
     'CCC' : [444,555,666]
    }
);

ff = pd.DataFrame(
    {'AAA' : [4,5,6,7],
     'BBB' : [10,20,30,40],
     'CCC' : [100,50,-30,-50],
     'FFF' : [1,1,1,1]
    }
);

dg = pd.DataFrame(
    {'AAA' : [4,5,6,7],
     'BBB' : [10,20,30,40],
     'CCC' : [100,50,-30,-50]
    },
    index=[['a', 'b', 'c', 'd'],['0', '1', '2', '3']]
);

dh = pd.DataFrame(
    {'AAA' : [4,5,6,NA],
     'BBB' : [10,20,30,NA],
     'CCC' : [100,50,-30,-50]
    },
    index=['d','b','c','a']
);

# df3 = df.append(df2)
# df3=df3.sort_values(by=['AAA','BBB'],ascending=True)
# print(df3)

# def updRow(row,field):
#     # print(row['AAA'])
#     # row['DDD'] = DateUtil.str2Datetime(row['DDD'])
#     row[field] = DateUtil.str2_datetime(row[field])
#     return row
#
# uu = df.apply(updRow, field='DDD', axis=1)
# # uu = df
# line = uu.iloc[0:1]
# print(line['DDD'])

# list1 = ['a','b','c','d']
# print('a' not in list1)

# dic = {'a': 1, 'b': 2, 'c': 3}
# dic2=dic.copy()
# dic2['a']=4
# print(dic2)
# print(dic)


# print(df)
#
# # dg=dg.reset_index(drop = False)
# #
# # dg.rename(columns={'level_0': 'tradingDay', 'level_1': 'InnerCode'}, inplace=True)
# # print(dg)
#
# df['DDD'] = df['DDD'].astype('datetime64')
# print(df)
#
# print(type(df.iloc[0:1]['DDD'].values[0]))



# def createSameValueList(num):
#     val = 1/num
#     retList = []
#     for i in range(num):
#         retList.append(val)
#     print(retList)
#
# retList=createSameValueList(6)
# print(retList)

a = 123

aint = int(a)
print(type(aint))


#
# print(type(uu.iloc[0:1]['DDD'].values[0]))


# print(df['AAA'].values)

# print(list(df.index.get_level_values(0)))

# df['DDD'] = DateUtil.str2Datetime(df['DDD'])
# print(df)

# ff = ff.set_index(['AAA','BBB'])
# print(ff)

# dh = dh['AAA'].fillna(dh['AAA'].mean())
# print(dh)

# dh = dh.fillna(dh.mean())
# print(dh)

# uu=df[['AAA','CCC']]
# print(uu)

# data = [100, 94, 88, 82, 76, 70, 64, 58, 52, 46, 40, 34]
# print(data.index(76))

# aaa=list(dg.index.get_level_values(1))
# print(aaa)

# tg = pd.DataFrame({'sliceIdx':range(0, 100),'sharpRatio':None})
# tg = tg.set_index(['sliceIdx'])
# print(tg)
#
# for index, row in tg.iterrows():
#     tg.ix[index,['sharpRatio']] = index
#
# print(tg)



# def add100(x):
#     return x.get('a')
#
#
# hh = [{'a':2.1}, {'a':3}, {'a':4}]
# hh2=map(add100, hh)
# print(sum(list(hh2)))

# l2 = [2,3,4]
# l2.reverse()
# print(l2)

# print(df.iloc[0:1].index[0])

# a = sdata.get('A')
# if a is None:
#     print('None')
# else:
#     print('not None')

# capitalEntity = CapitalEntity.CapitalEntity(10,10,10)
# print(capitalEntity.getStockMV())
#
# capitalEntity2 = copy.copy(capitalEntity)
# capitalEntity2.setStockMV(20)
# print(capitalEntity2.getStockMV())





# df = df.sort_index(by='AAA', ascending=True)[4:5]
#
# print(df)

#dh=dh.sort_index(ascending=False)

#toKeepInSellList=['a']
#df = df[df.index.isin(toKeepInSellList)]
#dg = dg[dg.index.get_level_values(1)=='2']
#print(dg.ix['c',:])

# print(df.loc['a':'c'].AAA)
# print(df.iloc[0:3].AAA)
# print(df.ix['a':'c'].AAA)
# print(df[(df.index>='a') & (df.index<='c')].AAA)

# aaa='aaa\nbbb\n'
# aaa = aaa + df.to_string()
# print(aaa)


#print(dg.index)
#print(sdata['A'])

#print(('a','0') in dg.index)

#print(dg.index.get_level_values(1))



#for index, row in df.iterrows():
    #row['AAA'] = 1

#print(dg.index[0])

#a_list = [4,5,6,7]
#df32 = dg[~(dg.AAA.isin(a_list))].values
#print(len(df32))

#del dg['FFF']


#print(dg.get_value(('b','1'),'BBB'))

#print(list(ff.index))


#print(ff.loc[(ff['BBB'] >= 30) & (ff.index >= 3)].index[0])


#ff['EEE'] = Series([2,2,2,2])
ff.insert(4,'GGG',Series([2,2,2,2]))
#summer = ff.pop('FFF')
#print(summer)
#print(ff)
ff.columns = ['AAA', 'BBB', 'CCC', 'FFF', 'HHH']
#print(ff)


#dflow = df[df.AAA <= 5]

# newseries = df.loc[
#    (df['BBB'] < 25) & (df['CCC'] >= -40),
#    ['AAA','BBB','CCC']
# ];

# print(newseries);

df2 = pd.DataFrame(data=df,index=[0,1,2,3,4]);
# print(df2.ix[1:3]);
# print(df2);




# update N columns where conditions
df.loc[(df['AAA'] <= 5) & (df['BBB'] <= 10), ['BBB','CCC']] = 0.1,0.2
#print(df);

# select N columns where conditions
df3 = df.loc[(df['AAA'] <= 5) & (df['BBB'] <= 20), ['BBB','CCC']]
#print(df3);

# select all columns where conditions
df32 = df[df.AAA.isin([5, 6])]
#print(df32);
df33 = df[~(df.AAA.isin([5, 6]))]
#print(df33);

# select all column where conditions
df4 = df[~((df['AAA'] <= 5) & (df['BBB'] <= 20))]
#print(df4);

# select top 2 order by CCC desc
df5 = df.sort_values(by='CCC', ascending=False).head(2)
#print(df5);

# left join on N columns
df6 = pd.merge(df5,ef,on=['AAA','BBB'],how='left', suffixes=('_l','_r'))

# inner join on N columns
df7 = pd.merge(df5,ef,on=['AAA','BBB'],how='inner')

# new column
df['DDD'] = df['AAA'] * 2
#print(df);

#
#df8 = df.rename(index='',inplace=True)
#df8 = df.reindex(['a','b','c','d'])

#index.name
df.index.name = 'idx'
#print(df);

# group by ->mean sum count min max first last std var
df82 = df.groupby(['AAA','BBB'])['CCC'].mean()
#print(df82);

# concat
df83 = pd.concat([df,ff])
#print(df83);

def printHello():
    print('aaa')

# entity
def createRow(a,b,c,d):
    return dict(AAA=a, BBB=b, CCC=c, DDD=d)

#d = createRow(10, 10, 10, 10)
#print(d)

# insert rows
list1 = []
list1.append(createRow(10, 10, 10, 10))
list1.append(createRow(11, 11, 11, 11))
# list -> df
row1 = pd.DataFrame(list1)
# insert
df10 = df.append(row1, ignore_index=True)
#print(df10);


#delete
#df9 = df.drop(df['AAA'] <= 5)
#print(df9)

#deep copy
df11 = df[['AAA','CCC']].copy()
#print(df11);

# select topN
df12 = df11[0:2];
#print(df12);


#create by np.array (by line)
aa=np.array([[1,2,3],[4,5,6],[7,8,9]])
bb=pd.DataFrame(aa,index=[22,33,44],columns=['one','two','three'])

#print(bb);

# drop_duplicates
df8 = ff.drop_duplicates(['AAA'])
#print(ff);

#print(df['BBB'])
#print(df['BBB'].max())

#print(df.ix[:,[0,1]])   #选取第一列
#print(df.ix[:,[0,1]].max()['AAA'])


# t1 = time.time()
# a = pd.read_hdf(r'D:\BRPrice_0302.h5')
# t2 = time.time()
# print(t2 - t1)

# import pip
# from subprocess import call
#
# for dist in pip.get_installed_distributions():
#     call("pip install --upgrade " + dist.project_name, shell=True)