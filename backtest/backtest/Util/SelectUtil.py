from pandas import Series, DataFrame
import pandas as pd
import random
import numpy as np
import math

#创建相同数的列表，比如num=2，则列表是[0.5,0.5]
def createSameValueList(num):
    val = 1/num
    retList = []
    for i in range(num):
        retList.append(val)
    # print(retList)
    return retList

def insertVolWeight(n, df2):
    l1 = createSameValueList(n)
    # print(l1)
    s = Series(l1,index=df2.index)
    # print(s)
    df2.insert(len(df2.columns),'volWeight',s)
    # print(df2)

# def getTopN(n, df2):
#     if len(df2) < n:
#         n = len(df2)
#
#     df2 = df2[0:n]
#     return df2

def getTopNAndInsertVolWeight(n, df2):
    if len(df2) < n:
        n = len(df2)

    df2 = df2[0:n]

    l1 = createSameValueList(n)
    s = Series(l1, index=df2.index)
    df2.insert(len(df2.columns), 'volWeight', s)

    return df2

#select top N
#asc True正序 False倒序
# def top(df, n=0, column='', asc=True):
#     return df.sort_index(by=column, ascending=asc)[0:n]
    # return df[0:n]

def top(df, n=0, column='', asc=True):
    # return df.sort_index(by=column, ascending=asc)[0:n]
    df.reset_index(level=0, drop=True, inplace=True)
    # print(df)
    df2 = df.sort_index(by=column, ascending=asc)

    df2 = getTopNAndInsertVolWeight(n, df2)

    return df2

#仓位权重
def top_with_vol_weight(df, n=0, column='', asc=True):
    # print(df)
    df.reset_index( level = 0, drop = True, inplace= True)
    # print(df)
    df2 = df.sort_index(by=column, ascending=asc)

    #get top N, n必须要变
    if len(df2) < n:
        n = len(df2)

    df2 = df2[0:n]

    if n==2:
        insertVolWeight(n, df2)
        return df2
    elif n==3:
        #[0.5,0.3,0.2]
        #l1 = [0.5,0.3,0.2]
        l1 = [0.5, 0.3, 0.2]
        s = Series(l1,index=df2.index)
        df2.insert(len(df2.columns),'volWeight',s)
        return df2
    elif n==4:
        # print(df2)
        insertVolWeight(n, df2)
        # print(df2)
        return df2
    elif n==5:
        insertVolWeight(n, df2)
        return df2
    else:
        pass


#切片后选前N
#选X% --> X% + n
#sliceIdx = 0-99
def top_with_slice(df, slice_dict, column='', asc=True):
    df.reset_index(level=0, drop=True, inplace=True)

    total = len(df)

    slice_total_num = slice_dict.get('sliceTotalNum')
    slice_idx = slice_dict.get('sliceIdx')
    n = slice_dict.get('numOfDailySignal')

    start = get_slice(total, slice_idx, slice_total_num)
    end = start + n

    df2 = df.sort_index(by=column, ascending=asc)[start:end]

    n2 = len(df2)

    insertVolWeight(n2, df2)

    return df2

#total：总行数
#sliceIdx：切片号
#sliceTotalNum：切片总数
#numPerSlice：每块切片的行数
#start：开始行号
#end：结束行号
#return start, end
def get_slice(total, slice_idx, slice_total_num):
    # sliceTotalNum = 100
    num_per_slice = total / slice_total_num
    start = num_per_slice * slice_idx
    # end = numPerSlice * (sliceIdx + 1) - 1
    start = math.ceil(start)
    # end = math.ceil(end)
    # print(start)
    # print(end)
    # return [start,end]
    return start
#
# getSlice(1001,0,10)
# getSlice(1001,1,10)

#处理NA
def handle_na1(df):
    return df.dropna()

#处理NA
def handle_na2(df):
    return df.fillna(df.mean())

#加权重，取前N
def top_with_weight(df, n=0, tech_list=[], asc=True, handle_na_func=handle_na1):
    df.reset_index(level=0, drop=True, inplace=True)
    #
    column1 = tech_list[0]
    column2 = tech_list[1]

    df = handle_na_func(df)

    # 先归一化指标的值
    normalize(df, column1, 'score1')
    normalize(df, column2, 'score2')

    # 随机权重(0, 0.5, 1)
    data = {'weight1': np.random.randint(0, 3, size=len(df)) / 2}
    randDf = DataFrame(data, index=df.index)
    randDf['weight2'] = 1 - randDf['weight1']

    # 总分
    df['totalScore'] = df['score1'] * randDf['weight1'] + df['score2'] * randDf['weight2']
    # 用于debug
    # df['weight1'] = randDf['weight1']
    # df['weight2'] = randDf['weight2']

    df2 = df.sort_index(by='totalScore', ascending=asc) #[0:n]

    df2 = getTopNAndInsertVolWeight(n, df2)

    # insertVolWeight(n, df2)

    return df2

#tech:被归一化的字段,归一化后的分数(100-0)
def normalize(df, tech, score):
    cnt = len(df)
    df[score] = 100.0 - (100.0 / (cnt - 1)) * (df[tech].rank(ascending=False,method='first') - 1)

"""
df = pd.DataFrame(
    {'AAA' : [4,5,6,7],
     'BBB' : [10,20,30,40],
     'CCC' : [100,50,-30,-50]
    },
    index=['a','b','c','d']
);
normalize(df,'AAA','score1')
normalize(df,'CCC','score2')

data={'weight1':np.random.randint(0,3,size=len(df)) / 2}
df2=DataFrame(data, index=df.index)
df2['weight2'] = 1-df2['weight1']
# df.sort_values(by='AAA', inplace=True, ascending=False)
# df['score1'] = df['AAA'].rank(ascending=False)
print(df2)

df['totalWeight'] = df['AAA'] * df2['weight1'] + df['BBB'] * df2['weight2']
print(df)
"""

"""
df = pd.DataFrame(
    {'AAA' : [4,5,6,7],
     'BBB' : [10,20,30,40],
     'CCC' : [100,50,-30,-50]
    },
    index=['a','b','c','d']
);
# df.insert(len(df.columns),'rownum',Series())
# df = df.drop_duplicates(subset='rownum', keep='last')

df['score1'] = df['AAA'].rank(ascending=False,method='first')
print(df)
"""
