from tkinter import *
import datetime
import time
import socket
import json
from gui import *
import configparser


def onClosing():
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

def checkServer(ip, port, timeout=999):
    try:
        conn = socket.socket()
        conn.settimeout(timeout)
        conn.connect((ip, port))
        conn.close()
    except:
        return False
    return True

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
    global server_name
    global is_connected
    if username == 'None':
        addToLog("System> Set a username first! (/set_username)")
        return
    if ":" not in addr: 
        addr += ":" + str(server_port)
    addr = addr.replace(' ', '')
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
            server_name = data.decode("utf-8")
            addToLog("Server> " + "Connected to " + server_name + ".")
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
    global config
    if is_connected:
        addToLog("System> Disconnect first!")
        return
    addToLog("System> Username set: " + new_username)
    username = new_username[:-2]
    config['DEFAULT']['username'] = username
    with open("config.ini", 'w') as fout: config.write(fout)
    fout.close()

def scanServers(timeout):
    global saved_servers
    global config
    global stop_scan
    stop_scan = False
    self_ip = socket.gethostbyname(socket.gethostname()).split('.')
    addToLog("System> Scaning the network for avaliable servers...")
    addToLog("System> You can see the progress in the status bar below.")
    update()
    
    progress_str = list("[=========================], Done: ")
    i = -1
    for s in saved_servers:
        i += 1
        prc = round(i / len(saved_servers) * 100)
        progress_str[1:round(prc / 100 * 25) + 1] = "#" * round(prc / 100 * 25)
        setStatus("Scaning saved servers: " + 
                  ''.join(progress_str) + str(s) + " (" + str(prc) + "%)")        
        self_ip[-1] = str(s)
        str_ip = '.'.join(self_ip)
        try:
            conn = socket.socket()
            conn.settimeout(float(timeout))
            conn.connect((str_ip, server_port))
            conn.send(b'0')
            addToLog("  " + str_ip + " - " + conn.recv(4096).decode("utf-8"))
            conn.close()
        except:
            pass     
        update()
    progress_str = list("[=========================], Done: ")
    found_server = False    
    for s in range(256):
        if stop_scan: 
            addToLog("System> Stopped.")
            break
        if s in saved_servers: continue
        prc = round(s / 255 * 100)
        progress_str[round(prc / 100 * 25) + 1] = "#"
        setStatus("Scaning the network: " + 
                  ''.join(progress_str) + str(s) + " (" + str(prc) + "%)")
        
        self_ip[-1] = str(s)
        str_ip = '.'.join(self_ip)
        try:
            conn = socket.socket()
            conn.settimeout(float(timeout))
            conn.connect((str_ip, server_port))
            conn.send(b'0')
            addToLog("  " + str_ip + " - " + conn.recv(4096).decode("utf-8"))
            conn.close()
            if i not in saved_servers:
                saved_servers.add(i)
                found_server = True
        except:
            pass
        if found_server:
            u_list = list(saved_servers)
            config['SAVED DATA']['saved_servers'] = json.dumps(u_list)
            with open("config.ini", 'w') as fout: config.write(fout)
            fout.close()
        update()      

def stopScan(*args):
    global stop_scan
    stop_scan = True
        
command_list = {
    "connect"      : connectToServer,
    "disconnect"   : disconnect,
    "command_list" : commandList,
    "set_username" : setUsername,
    "scan_servers" : scanServers,
    "stop_scan"    : stopScan
    }
#COMMANDS_END------------------------------------------------------COMMANDS_END#


root.wm_title("Python Chat")
root.protocol("WM_DELETE_WINDOW", onClosing)
message_field.bind("<Return>", checkCommand)
message_button.config(command=checkCommand)

config = configparser.ConfigParser()
config.read('config.ini')

server_ip = "localhost"
server_port = int(config['DEFAULT']['default_port'])
server_name = ""
is_connected = False
last_idx = -1
username = config['DEFAULT']['username']
stop_scan = False  # If it is true, the server scaning will stop.
saved_servers = set(json.loads(config['SAVED DATA']['saved_servers']))
 
welcome_message = '''  Welcome to Fullmetal Chat v0.0!
  Type /connect [ip]:[port] to connect to a chat room.
'''
if username != 'None': welcome_message = username + ',\n' + welcome_message
log.insert(END, welcome_message) 
users.insert(END, "Not connected")

start = time.time()
WINDOW_EXISTS = True  # For the correct turn-off.
while WINDOW_EXISTS:  # Mainloop.
    updateData()
    if is_connected:
        setStatus("Connected to " + server_name + " (" + server_ip + ":" + 
                  str(server_port) + ")  Ping: " + 
                  str(int((time.time() - start) * 1000)) + " ms.")
    else:
        setStatus("Not connected")
    update()

# root.mainloop() doesn't work, so we need to update the window
# manually with root.update().