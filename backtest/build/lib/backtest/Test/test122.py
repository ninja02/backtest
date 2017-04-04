import pandas as pd
import numpy as np
from pandas import Series, DataFrame
import sys

foo = [2, 18, 9, 22, 17, 24, 8, 12, 27]

df2 = filter(lambda x: x % 3 == 0, foo)
#print(df2)
#print (map(lambda x: x * 2 + 10, foo))
#print (reduce(lambda x, y: x + y, foo))

#print([x * 2 + 10 for x in foo])
#print([x for x in foo if x % 3 == 0])

df = pd.DataFrame({'animal': 'cat dog cat fish dog cat cat'.split(),
                       'size': list('SSMMMLL'),
                       'weight': [8, 10, 11, 1, 20, 12, 12],
                       'adult' : [False] * 5 + [True] * 2})

def func1(subf):
    return subf['weight'].idxmax()

def func2(subf):
    print(str(subf))
    #for i in subf:
        #print(str(i))
    #return subf.max()

def func3(subf):
    #subf2 = subf[0:2]
    #subf2 = subf2*2
    #return subf2
    #print(subf)
    return subf*2

df2 = df.groupby('animal').apply(func1)
df['weight2'] = df.weight.apply(func2)
#print(df)

#pdata = get_price(['000300.XSHG', '000001.XSHE'])

#for x in foo:
# print(x)

print(
    sys.version
    )

list2 = ['a']

if list2:
    print('not null')
else:
    print('null')




