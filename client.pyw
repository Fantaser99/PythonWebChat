from tkinter import *
import datetime
import time
import socket
import json
from gui import *


def setStatus(text):
    statusbar.config(text=str(text))

def addToLog(text):
    log.insert(END, str(text) + "\n")

def update():
    time.sleep(1 / 60)
    root.update()

def on_closing():
    global WINDOW_EXISTS
    if True or messagebox.askokcancel("Quit", "Do you want to quit?"):
        if is_connected: disconnect()
        root.destroy()
        WINDOW_EXISTS = False  # For the correct turn-off
        
def updateUsers(active_users):
    global users
    users.delete(0, END)
    for user in active_users: users.insert(END, user)

def updateData():
    global start
    global is_connected
    global last_idx
    start = time.time()
    if not is_connected:
        return
    try:
        conn = socket.socket()
        conn.connect((server_ip, server_port))
        conn.send(("2" + str(last_idx)).encode("utf-8"))
        data = json.loads(conn.recv(16384).decode("utf-8"))
        conn.close()
        new_messages = data[0]
        active_users = data[1]
        last_idx += len(new_messages)
        for msg in new_messages: addToLog(msg)       
        updateUsers(active_users)        
    except:
        is_connected = False
        addToLog("System> You were disconnected.")

def sendMessage(message):    
    if not is_connected:
        addToLog("System> Connect to a server first!")
        return
    conn = socket.socket()
    conn.connect((server_ip, server_port))
    conn.send(("1" + username + "> " + message).encode("utf-8"))             
    conn.close()
    
    return

#COMMANDS--------------------------------------------------------------COMMANDS#
def checkCommand(*args):
    text = getText() + "  "
    if len(text) != 0 and text[0] == '/':
        command = text[1:text.index(" ")]
        value   = text[text.index(" ") + 1:]
        if command not in command_list.keys():
            addToLog("System> Unknown command. Type /command_list to see" +
                                    " avaliable commands.")
            return
        command_list[command](value)        
        
    else:
        sendMessage(text)

def connectToServer(addr):
    global server_ip
    global server_port
    global is_connected
    if not username:
        addToLog("System> Set a username first! (/set_username)")
        return
    if ":" not in addr: 
        addToLog("System> You forgot about the port!")
        return
    ip = addr.split(":")
    server_ip = ip[0]
    server_port = int(ip[1])
    try:
        conn = socket.socket()
        conn.connect((server_ip, server_port))
        conn.send(("0" + username).encode("utf-8"))
        data = conn.recv(1024)
        if not data:
            addToLog("System> Connection failed!")
        elif data == "Ban":
            addToLog("Server> Your IP was banned from this server.")
        else:
            addToLog("Server> " + data.decode("utf-8"))
            is_connected = True
    except:
        addToLog("System> Connection failed!")
    conn.close()

def disconnect(*args):
    global is_connected
    global users
    conn = socket.socket()
    conn.connect((server_ip, server_port))
    conn.send(("3" + username).encode("utf-8"))
    if conn.recv(1024).decode("utf-8") == "Disconnected":
        addToLog("Server> Disconnected.")
        is_connected = False
    else:
        addToLog("Server> Error.")
    conn.close()
    users.delete(0, END)
    users.insert(END, "Not connected")

def commandList(*args):
    addToLog("System> Avaliable commands: ")
    for cmd in command_list.keys():
        addToLog("System>  /" + cmd)

def setUsername(new_username):
    global username
    if is_connected:
        addToLog("System> Disconnect first!")
        return
    addToLog("System> Username set: " + new_username)
    username = new_username[:-2]
        
command_list = {
    "connect"      : connectToServer,
    "disconnect"   : disconnect,
    "command_list" : commandList,
    "set_username" : setUsername
    }
#COMMANDS_END------------------------------------------------------COMMANDS_END#


root.wm_title("Python Chat")
root.protocol("WM_DELETE_WINDOW", on_closing)
message_field.bind("<Return>", checkCommand)
message_button.config(command=checkCommand)

server_ip = "localhost"
server_port = 14000
is_connected = False
last_idx = -1
username = None

welcome_message = '''Welcome to Fullmetal Chat v0.0!
Type /connect [ip]:[port] to connect to a chat room.
'''
log.insert(END, welcome_message)  # Welcome message.
users.insert(END, "Not connected")

start = time.time()
WINDOW_EXISTS = True  # For the correct turn-off.
while WINDOW_EXISTS:  # Mainloop.
    updateData()
    setStatus("Ping: " + str(int((time.time() - start) * 1000)) + " ms.")
    update()

# root.mainloop() doesn't work, so we need to update the window
# manually with root.update().