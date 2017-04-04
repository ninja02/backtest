#集合的操作

#交集
def intersection(a,b):
    return list(set(a).intersection(set(b)))

#获取两个list 的并集
def union(a,b):
    return list(set(a).union(set(b)))

#获取两个 list 的差集
def difference(a,b):
    return list(set(a).difference(set(b))) # a中有而b中没有的

def dict_to_string(dict):
    result = ''
    for key, value in dict.items():
        result += "\"%s\":\"%s\"" % (key, value)
    return result

"""
#用merge对df取交集的方法
    if currSourceData == None | lastSourceData == None:
        return None
    if len(currSourceData) == 0 | len(currSourceData) == 0:
        return None
    pd.merge(currSourceData, lastSourceData, on=['AAA', 'BBB'], how='inner')
"""
