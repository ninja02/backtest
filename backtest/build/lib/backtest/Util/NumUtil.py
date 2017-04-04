import math

def get_round(val, scale):
    return round(float(val), scale)

#涨幅
def get_change_pct(value1, value2, scale):
    v = (value2 - value1) / value1 * 100
    #print(v)
    return round(float(v), scale)

#print(getChangePCT(10,11.1116,2))

#本函数弃用,请用python自带函数
def avg(profit_series):
    if (len(profit_series) > 0):
        ave = 0.0;
        sum = 0.0;
        for profit in profit_series:
            sum = sum + profit;

        ave = sum / len(profit_series);
        return ave

#本函数弃用,请用python自带函数
def var(profit_series):
    if (len(profit_series) > 0):
        ave = 0.0;
        sum = 0.0;
        ret = 0.0;
        for profit in profit_series:
            sum = sum + profit

        ave = sum / len(profit_series)

        for profit in profit_series:
            ret = ret + (ave - profit) * (ave - profit)

        ret = ret / len(profit_series)
        return ret

#本函数弃用,请用python自带函数
def std(profit_series):
    var_value = var(profit_series);
    std = math.sqrt(var_value * len(profit_series) / (len(profit_series) - 1))
    return std