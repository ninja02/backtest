from tkinter import *
root=Tk()
root.title('Bit Exraction')
root.geometry('800x600')
cv_frameindex=['CV_F0','CV_F1','CV_F2','CV_F3','CV_F4','CV_F5','CV_F6','CV_F7','CV_F8','CV_F9','CV_F10','CV_F11','CV_F12','CV_F13','CV_F14','CV_F15','CV_F16','CV_F17','CV_F18','CV_F19',\
'CV_F20','CV_F21','CV_F22','CV_F23','CV_F24','CV_F25','CV_F26','CV_F27','CV_F28','CV_F29','CV_F30','CV_F31','CV_F32','CV_F33','CV_F34','CV_F35','CV_F36','CV_F37','CV_F38','CV_F39',\
'CV_F40','CV_F41','CV_F42','CV_F43','CV_F44','CV_F45','CV_F46','CV_F47','CV_F48','CV_F49','CV_F50','CV_F51','CV_F52','CV_F53','CV_F54','CV_F55','CV_F56','CV_F57','CV_F58','CV_F59',\
'CV_F60','CV_F61','CV_F62','CV_F63','CV_F64','CV_F65','CV_F66','CV_F67','CV_F68','CV_F69','CV_F70','CV_F71','CV_F72','CV_F73','CV_F74','CV_F75','CV_F76','CV_F77','CV_F78','CV_F79'
]

GPIO_index=['GPIO-0','GPIO-1','GPIO-2','GPIO-3','GPIO-4','GPIO-5','GPIO-6','GPIO-7','GPIO-8','GPIO-9','GPIO-10','GPIO-11','GPIO-12','GPIO-13','GPIO-14','GPIO-15','GPIO-16','GPIO-17','GPIO-18','GPIO-19',\
'GPIO-20','GPIO-21','GPIO-22','GPIO-23','GPIO-24','GPIO-25','GPIO-26','GPIO-27','GPIO-28','GPIO-29','GPIO-30','GPIO-31','GPIO-32','GPIO-33','GPIO-34','GPIO-35','GPIO-36','GPIO-37','GPIO-38','GPIO-39',\
'GPIO-40','GPIO-41','GPIO-42','GPIO-43','GPIO-44','GPIO-45','GPIO-46','GPIO-47','GPIO-48','GPIO-49','GPIO-50','GPIO-51','GPIO-52','GPIO-53','GPIO-54','GPIO-55','GPIO-56','GPIO-57','GPIO-58','GPIO-59',\
'GPIO-60','GPIO-61','GPIO-62','GPIO-63','GPIO-64','GPIO-65','GPIO-66','GPIO-67','GPIO-68','GPIO-69','GPIO-70','GPIO-71','GPIO-72','GPIO-73','GPIO-74','GPIO-75','GPIO-76','GPIO-77','GPIO-78','GPIO-79'
]

bak_index=['bak0','bak1','bak2','bak3','bak4','bak5','bak6','bak7','bak8','bak9','bak10','bak11','bak12','bak13','bak14','bak15','bak16','bak17','bak18','bak19',\
'bak20','bak21','bak22','bak23','bak24','bak25','bak26','bak27','bak28','bak29','bak30','bak31','bak32','bak33','bak34','bak35','bak36','bak37','bak38','bak39',\
'bak40','bak41','bak42','bak43','bak44','bak45','bak46','bak47','bak48','bak49','bak50','bak51','bak52','bak53','bak54','bak55','bak56','bak57','bak58','bak59',\
'bak60','bak61','bak62','bak63','bak64','bak65','bak66','bak67','bak68','bak69','bak70','bak71','bak72','bak73','bak74','bak75','bak76','bak77','bak78','bak79'
]
for i in range(80):
    bak_index[i]=[]

t1=Frame(root,height=1,width=300)
Label(t1,text='Use: 1-GPIO O-Native\n',anchor='w',height=2,width=300).pack(side=LEFT, fill=Y)
t1.pack(side=TOP,fill=Y)

t2=Frame(root,height=1,width=300)
Label(t2,text='I/O: 1-Output O-Input\n',anchor='w',height=2,width=300).pack(side=LEFT, fill=Y)
t2.pack(side=TOP,fill=Y)

t3=Frame(root,height=1,width=300)
Label(t3,text='H/L: 1-High O-Low\n',anchor='w',height=2,width=300).pack(side=LEFT, fill=Y)
t3.pack(side=TOP,fill=Y)

t4=Frame(root,height=1,width=300)
Label(t4,text='INV: 1-Invert Input Value\n',anchor='w',height=2,width=300).pack(side=LEFT, fill=Y)
t4.pack(side=TOP,fill=Y)

t5=Frame(root,height=1,width=300)
Label(t5,text='Pin Default Set As Native Function\n',anchor='w',height=2,width=300).pack(side=LEFT, fill=Y)
t5.pack(side=TOP,fill=Y)

t6=Frame(root,height=0,width=300)
Label(t6,text='--'*90,anchor='w',height=1,width=300).pack(side=LEFT, fill=Y)
t6.pack(side=TOP,fill=Y)

t7=Frame(root,height=5,width=300)
tt=Frame(t7,height=1,width=300)
lb1=Label(tt, text='PIN',height=1,width=20,anchor=W).pack(side=LEFT, fill=Y)
lb2=Label(tt, text=' USE',height=1,width=20,anchor=W).pack(side=LEFT, fill=Y)
lb3=Label(tt, text=' I/O',height=1,width=20,anchor=W).pack(side=LEFT, fill=Y)
lb4=Label(tt, text=' H/L',height=1,width=20,anchor=W).pack(side=LEFT, fill=Y)
lb4=Label(tt, text=' INV',height=1,width=20,anchor=CENTER).pack(side=LEFT,fill=Y)
tt.pack(side=TOP, fill=Y)
tt1=Frame(t7,height=1,width=300)
Label(tt1,text='--'*90,anchor='w',height=1,width=300).pack(side=LEFT, fill=Y)
tt1.pack(side=TOP,fill=Y)
t7.pack(side=TOP,fill=Y)

cv=Canvas(root,height=30,width=30, scrollregion=(0,0,40,800),bg='red')

S1=Scrollbar(cv,orient='vertical',command=cv.yview)
cv['yscrollcommand']=S1.set
S1.pack(side=RIGHT, fill=Y)

cv.pack(side=TOP, fill=Y, expand=True)

for j in range(80):
    cv_frameindex[j]=Frame(cv, height=10, width=10)
    bak_index[j].append(Label(cv_frameindex[j], text=GPIO_index[j], height=1, width=13, anchor=CENTER))
    bak_index[j].append(Label(cv_frameindex[j], text=' '*20, height=1, width=10, anchor=CENTER))
    bak_index[j].append(Checkbutton(cv_frameindex[j], text='0', state='active'))
    bak_index[j].append(Checkbutton(cv_frameindex[j], text='1', state='active'))
    bak_index[j].append(Label(cv_frameindex[j], text=' '*20, height=1, width=13, anchor=CENTER))
    bak_index[j].append(Checkbutton(cv_frameindex[j], text='0', state='active'))
    bak_index[j].append(Checkbutton(cv_frameindex[j], text='1', state='active'))
    bak_index[j].append(Label(cv_frameindex[j], text=' '*20, height=1, width=13, anchor=CENTER))
    bak_index[j].append(Checkbutton(cv_frameindex[j], text='0', state='active'))
    bak_index[j].append(Checkbutton(cv_frameindex[j], text='1', state='active'))
    bak_index[j].append(Label(cv_frameindex[j], text=' '*20, height=1, width=13, anchor=CENTER))
    bak_index[j].append(Checkbutton(cv_frameindex[j], text='0', state='active'))
    bak_index[j].append(Checkbutton(cv_frameindex[j], text='1', state='active'))
    bak_index[j].append(Label(cv_frameindex[j], text=' '*20, height=1, width=13, anchor=CENTER))
for k in bak_index:
    for i in range(len(k)):
        k[i].pack(side=LEFT,fill=Y)
        for L in cv_frameindex:
            L.pack(side=TOP, fill=Y)

t8=Frame(cv, height=5, width=300)
Button(t8, text='Generate').pack(fill=Y)
t8.pack(side=TOP, fill=Y)

t9=Frame(cv, height=5, width=300)
Button(t9, text='Generate').pack(fill=Y)
t9.pack(side=TOP, fill=Y)

root.mainloop()