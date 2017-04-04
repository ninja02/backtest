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

root.mainloop()