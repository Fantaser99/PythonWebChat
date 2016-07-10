from tkinter import *
from gui import *
import datetime
import time
import socket
import json
import configparser


def onClosing():
    global WINDOW_EXISTS
    if True or messagebox.askokcancel("Quit", "Do you want to quit?"):
        if is_connected: disconnect()
        root.destroy()
        WINDOW_EXISTS = False  # For the correct turn-off

def decodeText(encoded_bytes, key):
    text = ""
    for i in range(len(encoded_bytes)):
        text += chr(encoded_bytes[i] ^ ord(key[i % len(key)]))
    return text
        
def updateUsers(active_users):
    global users
    users.delete(0, END)
    for user in active_users: users.insert(END, user)

def updateMessages(new_messages):
    for msg in new_messages: 
        addToLog(decodeText(msg, cipher_key))   

def updateColors(new_colors):
    global colors 
    for i in range(len(colors), len(new_colors)):
        log.addColorTag(new_colors[i], new_colors[i])
    colors = new_colors

def updatePatterns(new_patterns):
    global highlight_patterns
    highlight_patterns = new_patterns

def colorLog():
    for pattern, color in highlight_patterns:
        log.highlightPattern(pattern, color)

def updateData():
    global last_connection
    global is_connected
    global last_idx
    last_connection = time.time()
    if not is_connected:
        return
    try:  # Checking, if the client can get response from the server.
        conn = socket.socket()
        conn.connect((server_ip, server_port))
        
        send_data = ["update_data", last_idx]
        conn.send(json.dumps(send_data).encode("utf-8"))
        
        rec_data = json.loads(conn.recv(16384).decode("utf-8"))
        conn.close()
        
        new_messages = rec_data[0]
        active_users = rec_data[1]
        new_colors   = rec_data[2]
        new_patterns = rec_data[3]
        last_idx += len(new_messages)
        
        updateUsers(active_users)       
        updateColors(new_colors)  
        updatePatterns(new_patterns)
        updateMessages(new_messages)    
    except:  # If he can't, he disconnects.
        is_connected = False
        addToLog("System> You were disconnected.")

def sendMessage(message):    
    if not is_connected:
        addToLog("System> Connect to a server first!")
        return
    conn = socket.socket()
    conn.connect((server_ip, server_port))
    send_data = ["send_message", username + "> " + message]
    conn.send(json.dumps(send_data).encode("utf-8"))             
    conn.close()
    return

def checkServer(addr, value='', timeout=5):
    try:
        conn = socket.socket()
        conn.settimeout(timeout)
        conn.connect(addr)
        conn.send(json.dumps(["check_connection", value]).encode("utf-8"))
        response = conn.recv(4096)
        conn.close()
        return response
    except:
        return False

#COMMANDS--------------------------------------------------------------COMMANDS#
def checkCommand(*args):
    text = getText() + "  "
    if text[0] == '/':
        command = text[1:text.index(" ")]
        value   = text[text.index(" ") + 1:].replace(' ', '')
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
    ip = addr.split(":")
    server_ip = ip[0]
    server_port = int(ip[1])
    send_val = [username, username_color]
    response = checkServer((server_ip, server_port), send_val)
    if response:
        is_connected = True
        server_name = response.decode("utf-8")
        addToLog("System> Connected to " + server_name + "!")
    else:
        addToLog("System> Connection error.")

def disconnect(*args):
    global is_connected
    global users
    if not is_connected:
        addToLog("System> Not connected.")
        return
    conn = socket.socket()
    conn.connect((server_ip, server_port))
    conn.send(json.dumps(["disconnect", username]).encode("utf-8"))
    conn.close()
    addToLog("System> Disconnected.")
    is_connected = False
    users.delete(0, END)
    users.insert(END, "Not connected")

def commandList(*args):
    addToLog("System> Avaliable commands: ")
    for cmd in command_list.keys():
        addToLog("    /" + cmd)

def setUsername(new_username):
    global username
    global config
    if is_connected:
        addToLog("System> Disconnect first!")
        return
    addToLog("System> Username set: " + new_username)
    username = new_username
    config['DEFAULT']['username'] = username
    with open("config.ini", 'w') as fout: config.write(fout)

def setUsernameColor(new_color):
    global username_color
    global confing
    if is_connected:
        addToLog("System> Disconnect first!")
        return    
    if new_color[0] != "#" or len(new_color) != 7:
        addToLog("System> Wrong color.")
        return
    addToLog("System> Username color set: " + new_color)
    addToLog("System> Reconnect or relog to update it.")
    username_color = new_color
    config['DEFAULT']['username_color'] = username_color
    with open("config.ini", 'w') as fout: config.write(fout)

def scanSavedServers(timeout):
    global stop_scan
    stop_scan = False
    if not timeout: timeout = 1
    
    self_ip = socket.gethostbyname(socket.gethostname()).split('.')
    addToLog("System> Scaning the saved servers...")
    addToLog("System> You can see the progress in the status bar below.")
    update()
    
    progress_str = list("[=========================], Done: ")
    for i, ip in enumerate(saved_servers):
        if stop_scan: 
            addToLog("System> Stopped.")
            break
        prc = round(i / len(saved_servers) * 100)
        progress_str[1:round(prc / 100 * 25) + 1] = "#" * round(prc / 100 * 25)
        setStatus("Scaning saved servers: " + 
                  ''.join(progress_str) + str(i) + " (" + str(prc) + "%)")     
        
        response = checkServer((ip, server_port), '', float(timeout))
        if response:
            status = "online: " + response.decode("utf-8")
        else:
            status = "offline"
        addToLog(ip + ":" + str(server_port) + " - " + status)
        colorLog()
        update()

def scanLocalServers(timeout): 
    global stop_scan
    global saved_servers
    stop_scan = False
    if not timeout: timeout = 1
    
    self_ip = socket.gethostbyname(socket.gethostname()).split('.')
    addToLog("System> Scaning the network...")
    addToLog("System> You can see the progress in the status bar below.")
    update() 
    
    progress_str = list("[=========================], Done: ")
    found_server = False    
    for ip in range(256):
        if stop_scan: 
            addToLog("System> Stopped.")
            break
        prc = round(ip / 255 * 100)
        progress_str[round(prc / 100 * 25) + 1] = "#"
        setStatus("Scaning the network: " + 
                  ''.join(progress_str) + str(ip) + " (" + str(prc) + "%)")
        
        self_ip[-1] = str(ip)       # e.g. ['192', '168', '1', str(ip)]
        str_ip = '.'.join(self_ip)  # ---> '192.168.1.1'
        response = checkServer((str_ip, server_port), '', float(timeout))
        if response:
            status = "online: " + response.decode("utf-8")
            addToLog(str_ip + ":" + str(server_port) + " - " + status)
            if str_ip not in saved_servers:
                saved_servers.append(str_ip)
                found_server = True
        colorLog()
        update()      
    if found_server:
        with open("saved_servers.txt", 'w') as ss:
            ss.write(json.dumps(saved_servers))   

def stopScan(*args):
    global stop_scan
    stop_scan = True

def clearSavedServers(*args):
    with open("saved_servers.txt", 'w') as ss: ss.write("[]")
    addToLog("System> Cleared saved servers.")

def savedServersList(*args):
    addToLog("System> Saved servers: (type /scan_saved_servers to check them)")
    for s in saved_servers: addToLog("  " + s)

def saveServerLog(*args):
    if not is_connected:
        addToLog("System> Not connected.")
    conn = socket.socket()
    conn.connect((server_ip, server_port))
    conn.send(json.dumps(["save_data", '']).encode("utf-8"))
    addToLog("Server> " + conn.recv(4096).decode("utf-8"))
    conn.close()
        
command_list = {
    "connect"             : connectToServer,
    "disconnect"          : disconnect,
    "command_list"        : commandList,
    "set_username"        : setUsername,
    "set_username_color"  : setUsernameColor,
    "scan_saved_servers"  : scanSavedServers,
    "scan_local_servers"  : scanLocalServers,
    "stop_scan"           : stopScan,
    "clear_saved_servers" : clearSavedServers,
    "saved_servers_list"  : savedServersList,
    "save_server_log"    : saveServerLog
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
username_color = config['DEFAULT']['username_color']
cipher_key = config['DEFAULT']['cipher_key']
stop_scan = False  # If it is true, the server scaning will stop.
with open("saved_servers.txt") as ss: 
    saved_servers = json.loads(ss.read())

colors = []
updateColors(["blue", "red", "green", username_color])  # Sort of duct tape here.
highlight_patterns = [["Server", "blue"],
                      ["System", "red"],
                      ["online", "green"],
                      ["offline", "red"],
                      [username, username_color]]
 
welcome_message = '''  Welcome to Fullmetal Chat v0.0!
  Type /connect [ip]:[port] to connect to a chat room.
'''
if username != 'None': welcome_message = username + ',\n' + welcome_message
log.insert(END, welcome_message) 
users.insert(END, "Not connected")

last_connection = time.time()
WINDOW_EXISTS = True  # For the correct turn-off.
while WINDOW_EXISTS:  # Mainloop.
    updateData()
    if is_connected:
        setStatus("Connected to " + server_name + " (" + server_ip + ":" + 
                  str(server_port) + ")  Ping: " + 
                  str(int((time.time() - last_connection) * 1000)) + " ms.")
    else:
        setStatus("Not connected")
    colorLog()
    update()

# root.mainloop() doesn't work, so we need to update the window
# manually with root.update().