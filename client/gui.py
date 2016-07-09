from tkinter import *
import time


def setStatus(text):
    statusbar.config(text=str(text))
    
def addToLog(text):
    log.insert(END, str(text) + "\n")

def update():
    time.sleep(1 / 60)
    root.update()   

def getText(*args):
    text = message_field.get()
    message_field.delete(0, END)
    return text

root = Tk()

WIDTH = 15  # Divisible by 15.

log = Text(root)
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