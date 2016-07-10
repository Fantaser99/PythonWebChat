import socket
import json
import os
import configparser 


config = configparser.ConfigParser()
config.read("config.ini")
server_port = int(config['DEFAULT']['default_port'])
server_name = config['DEFAULT']['server_name']

sock = socket.socket()
try:
    sock.bind(("", server_port))
except:
    print("Port is already used.")
    input()
    os._exit(0)

sock.listen(100)

server_ip = socket.gethostbyname(socket.gethostname())
print("Started server on " + server_ip + ":" + str(server_port) + "!")

message_list = []
user_list = []
ban_list = []

show_received_messages = False
show_new_users         = False

while True:
    conn, addr = sock.accept()
    
    # On the first symbol of the received data there is always a number,
    # which tells the server, what it will receive:
    # 0 - connection check
    # 1 - message 
    # 2 - index of the last client's message
    # 3 - disconnection
    data = conn.recv(16384).decode("utf-8")
    if len(data) == 0: pass
    elif data[0] == "0":
        if addr[0] in ban_list:
            conn.send("Ban")
        else:
            conn.send(server_name.encode("utf-8"))
            if len(data) != 1:
                user_list.append(data[1:])
                if show_new_users:
                    print("New user connected: \n      IP: " + addr[0] + 
                                              "\nUsername: " + data[1:] + "\n")
    elif data[0] == "1":
        data = data[1:]
        if show_received_messages:
            print("Received a message:\n>" + addr[0] + "\n>" + data + "\n")
        message_list.append(data)
    elif data[0] == "2":
        last_idx = int(data[1:])
        messages_to_send = []
        if last_idx < len(message_list):
            messages_to_send = message_list[last_idx + 1:]
        send_data = [messages_to_send, user_list]
        conn.send(json.dumps(send_data).encode("utf-8"))
    elif data[0] == "3":
        if data[1:] in user_list: user_list.pop(user_list.index(data[1:]))
        conn.send(b'Disconnected')
    
    conn.close()