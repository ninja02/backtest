from pandas import Series, DataFrame
import pandas as pd
import random
import numpy as np

#select top N
#asc True正序 False倒序
def top(df, n=0, column='', asc=True):
    return df.sort_index(by=column, ascending=asc)[0:n]
    # return df[0:n]

#加权重，取前N
def top_with_weight(df, n=0, tech_list=[], asc=True):
    #
    column1 = tech_list[0]
    column2 = tech_list[1]

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

    return df.sort_index(by='totalScore', ascending=asc)[0:n]

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
