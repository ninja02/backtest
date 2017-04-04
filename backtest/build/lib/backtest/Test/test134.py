from tkinter import *

def onclick():
   pass

root = Tk()

lfc_field_1_t_sv = Scrollbar(root, orient=VERTICAL)  # 文本框-竖向滚动条
lfc_field_1_t_sh = Scrollbar(root, orient=HORIZONTAL)  # 文本框-横向滚动条

lfc_field_1_t = Text(root, height=15,width=50, yscrollcommand=lfc_field_1_t_sv.set,
                                  xscrollcommand=lfc_field_1_t_sh.set, wrap='none')  # 设置滚动条-不换行

df = pd.DataFrame(
    {'AAA' : [4,5,6,7],
     'BBB' : [10,20,30,40],
     'CCC' : [100,50,-30,-50]
    },
    index=['a','b','c','d']
);

lfc_field_1_t.insert(1.0, '---------------------------')
lfc_field_1_t.pack()

root.mainloop()