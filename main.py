from tkinter import *
from tkinter import messagebox
import datetime
import time
from multiprocessing.dummy import Pool

def setStatus(text):
    statusbar.config(text=str(text))

def update():
    time.sleep(1 / 60)
    root.update()

def on_closing():
    global WINDOW_EXISTS
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        WINDOW_EXISTS = False  # Для корректного завершения приложения.

def receiveMessage():
    global start
    start = time.time()

def sendMessage(*args):
    return

pool = Pool(15)

root = Tk()
root.wm_title("Python Chat")
root.protocol("WM_DELETE_WINDOW", on_closing)

WIDTH = 15  # Кратен 15. Обязательно.

log = Text(root)
log.insert(END, '''Welcome to Fullmetal Chat v0.0!''')  # Многострочная переменная для того, чтобы можно было впилить сюда приветствие.
log.grid(row=0, column=0, columnspan=WIDTH // 15 * 14, padx=1, pady=1)

users = Listbox(root)
users.grid(row=0, column=WIDTH // 15 * 14, columnspan=WIDTH // 15, sticky=N+S+W+E, padx=1, pady=1)
for i in range(5):
    users.insert(END, "User №" + str(i))

message_entry = Entry(root)
message_entry.bind("<Return>", sendMessage)
message_entry.grid(row=1, sticky=N+S+E+W, padx=1, pady=2, columnspan=WIDTH // 15 * 14)

message_button = Button(root, command=sendMessage, text="Отправить")
message_button.grid(row=1, sticky=E+W+S+N, padx=1, pady=2, columnspan=WIDTH // 15, column=WIDTH // 15 * 14)

statusbar = Label(root, text="Nothing happened", border=1, relief=RIDGE, anchor=W)
statusbar.grid(sticky=E+W, columnspan=WIDTH, pady=(2, 0))

start = time.time()
WINDOW_EXISTS = True  # Для корректного завершения приложения.
while WINDOW_EXISTS:  # Основной цикл.
    setStatus("С момента получения сообщений прошло " + str(int(time.time() - start)) + " секунд.")
    update()

# root.mainloop() не катит, приходится постоянно вручную прорисовывать окно с помощью root.update().