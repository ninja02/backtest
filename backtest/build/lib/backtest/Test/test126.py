import pandas as pd

def select_stk(pre_pf,func, **kwargs):
    pre_df = func(pre_pf,**kwargs)
    print(pre_df)

def select_top(pre_df, df, name):
    def add(a,b):
        return a+b

    pre_df.sort_values(by=name,inplace = True)
    df.sort_values(by=name,inplace = True)
    pre_df.iloc[0,:] = df.iloc[-1,:]
    pre_df.index.values[0] = df.index.values[-1]
    #print(pre_df)
    return pre_df

pre_df = pd.DataFrame(index=[1,3,4], columns=['Mom'], data= [1,2,3])
df = pd.DataFrame(index=[5,6,7], columns=['Mom'], data= [3,2,1])
# print(select_top(pre_df,df, 'Mom'))


select_stk(pre_df, select_top,df=df,name = 'Mom')