from tkinter import *
import time

class CustomText(Text):
    '''A text widget with a new method, highlight_pattern()
    
    example:
    
    text = CustomText()
    text.tag_configure("red", foreground="#ff0000")
    text.highlight_pattern("this should be red", "red")
    
    The highlight_pattern method is a simplified python
    version of the tcl code at http://wiki.tcl.tk/3246
    '''
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)

    def addColorTag(self, name, foreground):
        log.tag_config(name, foreground=foreground)    
    
    def highlightPattern(self, pattern, tag, start="1.0", end="end",
                          regexp=False):
        '''Apply the given tag to all text that matches the given pattern
    
        If 'regexp' is set to True, pattern will be treated as a regular
        expression.
        '''
    
        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)
    
        count = IntVar()
        while True:
            index = self.search(pattern, "matchEnd","searchLimit",
                                count=count, regexp=regexp)
            if index == "": break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")

def setStatus(text):
    statusbar.config(text=str(text))
    
def addToLog(text):
    log.insert(END, str(text) + "\n")

def update():
    time.sleep(1 / 20)
    root.update()   

def getText(*args):
    text = message_field.get()
    message_field.delete(0, END)
    return text

root = Tk()

menubar = Menu(root)

# Setting menu

filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Exit", command=root.destroy)

commandsmenu = Menu(menubar, tearoff=0)

menubar.add_cascade(label="File", menu=filemenu)
menubar.add_cascade(label="Commands", menu=commandsmenu)

root.config(menu=menubar)

WIDTH = 15  # Divisible by 15.

log = CustomText(root)
log.grid(row=0, column=0, columnspan=WIDTH // 15 * 14, padx=1, pady=1)

users = Listbox(root)
users.grid(row=0, column=WIDTH // 15 * 14, columnspan=WIDTH // 15, 
                                                sticky=N+S+W+E, padx=1, pady=1)

message_field = Entry(root)
message_field.grid(row=1, sticky=N+S+E+W, padx=1, pady=2, 
                                                   columnspan=WIDTH // 15 * 14)

message_button = Button(root, text="Send")
message_button.grid(row=1, sticky=E+W+S+N, padx=1, pady=2, 
                               columnspan=WIDTH // 15, column=WIDTH // 15 * 14)

statusbar = Label(root, text="Nothing happened", border=1, 
                                                        relief=RIDGE, anchor=W)
statusbar.grid(sticky=E+W, columnspan=WIDTH, pady=(2, 0))