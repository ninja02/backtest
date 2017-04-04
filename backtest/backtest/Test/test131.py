from tkinter import *
root = Tk()
i=0
b={}

win1 = Frame(root, height=100, width=100,bg='yellow')
win1.grid_propagate(False)
win1.grid()
Frame1 = LabelFrame(root,height = 400, width=400)
Frame1.grid(sticky=S)
s = Scrollbar(Frame1, orient = VERTICAL)
s.grid(row = 6, column = 1, sticky = NS)
can = Canvas(Frame1, width =400, height = 400, yscrollcommand=s.set,bg='red')
can.grid(row = 6, column = 0, sticky = NSEW)
win = Frame(can)
can.create_window(0,0, window = win,anchor = W)
s.config(command = can.yview)

Entry(win, width=15).grid(row=0, column=0)
#for i in range(100):
# lbl = Entry(win, text = str(i))
# lbl.grid()
def zhidu():
    global b
    global i
    i=i+1
    b['v'+str(i)]= StringVar()
    Entry(win, width=15,textvariable=b['v'+str(i)]).grid(row=i, column=0)
    win.update_idletasks()
    can.configure(scrollregion = (1,1,win.winfo_width(),win.winfo_height()))
    #win.update_idletasks()
    #can.configure(scrollregion = (1,1,win.winfo_width(),win.winfo_height()))

Button(win1, text="添加", fg="blue",bd=2,width=28,command=zhidu).pack(side=LEFT)

root.mainloop()