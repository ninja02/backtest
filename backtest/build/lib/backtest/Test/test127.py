
def main(select_stock,**kwargs):
    signalData=[]
    signalData=select_stock(signalData)
    print('main')

def select_stock1(signalData):
    print('select_stock1')
    return signalData

main(select_stock1)