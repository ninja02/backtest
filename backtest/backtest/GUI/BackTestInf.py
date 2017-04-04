import sys
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import backtest.Main.BackTestMainNew as BackTestMainNew
from backtest.Constance import StockConst
from backtestData.Dao import SourceDataDao
import matplotlib.pyplot as plt
from backtest.Util import DateUtil

# signalDataDf = SourceDataDao.loadSignalData(signalDataAddr)
# list(signalDataDf.columns)

# def createCheckboxFrame():
#     bottomframe.destroy()
#     bottomframe = Frame(myApp)
#     bottomframe.pack(side=BOTTOM)
#     return bottomframe

# techCheckVarArr = []
# techCheckVarArr.append(IntVar())
# C1 = Checkbutton(bottomframe, text=item, variable=techCheckVarArr[index], onvalue=1, offvalue=0, height=1, width=10).pack()

#技术指标列表，来自信号数据signalData
techList = []

def select_tech_radio():
    # techRadioIndex = techRadioVar.get()
    # tech = techList[techRadioIndex]
    pass

#选择信号数据文件
def select_signal_data():
    signalDataAddrFile = filedialog.askopenfile()
    signalDataAddr = signalDataAddrFile.name
    init_signal_data_info(signalDataAddr)

#界面初始值
def init_signal_data_info(signalDataAddr):
    # 取得技术指标
    techListOrigin = SourceDataDao.get_colums_from_h5(signalDataAddr)
    techList.clear()
    for x in techListOrigin:
        techList.append(x)

    # 删除已有指标控件
    for widget in techframe.winfo_children():
        widget.destroy()
    # 新增指标控件
    for index, item in enumerate(techListOrigin):
        R1 = Radiobutton(techframe, text=item, variable=techRadioVar, value=index, command=select_tech_radio)
        R1.pack(anchor=W)

    # 信号文件地址
    signalDataAddrVal.set(signalDataAddr)

    #
    originStartDate = SourceDataDao.get_first_record_from_h5(signalDataAddr).index[0][0]
    originEndDate = SourceDataDao.get_last_record_from_h5(signalDataAddr).index[0][0]
    originStartDate = DateUtil.datetime2_str(originStartDate)
    originEndDate = DateUtil.datetime2_str(originEndDate)
    originStartDateVar.set(originStartDate)
    originEndDateVar.set(originEndDate)

    #开始时间 结束时间
    startDateVal.set(originStartDate)
    endDateVal.set(originEndDate)



def check():
    messageVar.set('')
    startDate = startDateVal.get()
    endDate = endDateVal.get()
    # print('endDate:'+endDate)
    # print('originEndDate:' + originEndDateVar.get())

    if startDate < originStartDateVar.get():
        print('开始时间不能小于'+originStartDateVar.get())
        message = '开始时间不能小于'+originStartDateVar.get()
        messageVar.set(message)
        return False

    if endDate > originEndDateVar.get():
        print('结束时间不能大于'+originEndDateVar.get())
        message = '结束时间不能大于'+originEndDateVar.get()
        messageVar.set(message)
        return False
    return True

#
def back_test_command():
    #校验结果
    checkResult = check()
    if not checkResult:
        return

    # 删除结果
    for widget in resultframe.winfo_children():
        widget.destroy()

    #选中的技术指标
    tech = techList[techRadioVar.get()]
    #信号数据地址
    signalDataAddr = signalDataAddrVal.get()
    #

    techListForMain = [tech]

    sliceIdx = None
    numOfDailySignal = 3
    dailyQuoteAddr = StockConst.ROOT + StockConst.NEW_DAILY_QUOTE_H5
    # print(techListForMain)
    resultDic = BackTestMainNew.main(BackTestMainNew.select_stock_func1, BackTestMainNew.trade_func1,
                                     techListForMain,sliceIdx, numOfDailySignal,signalDataAddr,dailyQuoteAddr,startDateVal.get(),endDateVal.get())


    stockStatDailyDf = resultDic.get('stockStatDailyDf')
    result = resultDic.get('result')

    resultLabel = Label(resultframe, text=result).pack(side=LEFT, fill=Y)
    stockStatDailyDf['netValue'].plot()
    plt.show()

top = Tk()
top.geometry('800x700+100+100')
top.title('回测Demo')

myApp=Frame(top)


startDateVal = StringVar()
endDateVal = StringVar()
signalDataAddrVal = StringVar()
# resultVal = StringVar()
# startDateVal.set('2004-01-01')
# endDateVal.set('2004-01-20')
# signalDataAddrVal.set(StockConst.root + StockConst.fakeSignalDataH5)
techRadioVar = IntVar()

originStartDateVar = StringVar()
originEndDateVar = StringVar()
messageVar = StringVar()

#0
gridRow=0
messageLabel=Label(myApp,textvariable=messageVar,underline=0)
messageLabel.grid(row=gridRow,column=0,columnspan=2,sticky=NW,pady=3,padx=3)
# messageVar.set('111')
#1
gridRow += 1
startDateLabel=Label(myApp,text="开始时间:",underline=0)
startDateLabel.grid(row=gridRow,column=0,sticky=NW,pady=3,padx=3)
startDateEntry = Entry(myApp,textvariable=startDateVal)
startDateEntry.grid(row=gridRow,column=1,sticky=NW,pady=3,padx=3)

#2
gridRow += 1
endDateLabel=Label(myApp,text="结束时间:",underline=0)
endDateLabel.grid(row=gridRow,column=0,sticky=NW,pady=3,padx=3)
endDateEntry = Entry(myApp,textvariable=endDateVal)
endDateEntry.grid(row=gridRow,column=1,sticky=NW,pady=3,padx=3)

#3
gridRow += 1
signalDataAddrLabel=Label(myApp,text="信号数据地址:",underline=0)
signalDataAddrLabel.grid(row=gridRow,column=0,sticky=NW,pady=3,padx=3)
signalDataAddrEntry = Entry(myApp,textvariable=signalDataAddrVal)
signalDataAddrEntry.grid(row=gridRow,column=1,sticky=NW,pady=3,padx=3)

#4
gridRow += 1
selectSignalDataLabel=Label(myApp,text="选择信号文件:",underline=0)
selectSignalDataLabel.grid(row=gridRow,column=0,sticky=NW,pady=3,padx=3)
selectSignalDataButton = Button(myApp, text ='选择信号文件', command = select_signal_data)
selectSignalDataButton.grid(row=gridRow,column=1,sticky=NW,pady=3,padx=3)

#5
gridRow += 1
runBackTestButton = Button(myApp, text ='运行回测', command = back_test_command)
runBackTestButton.grid(row=gridRow,column=1,sticky=NW,pady=3,padx=3)

#6
gridRow += 1
techframe = Frame(myApp)
techframe.grid(row=gridRow,column=1,sticky=NW,pady=3,padx=3)

#7
gridRow += 1
resultframe = Frame(myApp,height=300, width=800)
resultframe.grid(row=gridRow,column=0,columnspan=2,sticky=NW,pady=3,padx=3)



init_signal_data_info(StockConst.ROOT + StockConst.FAKE_SIGNAL_DATA_H5)

myApp.pack(side=LEFT, fill=Y)

myApp.mainloop()
