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
show_new_users         = True

while True:
    conn, addr = sock.accept()
    
    # All data, that this server receives, consists of a command and a value.
    # A command tells the server, what the client is sending and what he wants
    # to receive, and the value - is the main information (last_idx, msg, etc.)
    command, value = json.loads(conn.recv(16384).decode("utf-8"))
    
    if command == "check_connection":
        conn.send(server_name.encode("utf-8"))
        if value:
            user_list.append(value)
            if show_new_users:
                print("New user connected: \n      IP: " + addr[0] + 
                                            "\nUsername: " + value + "\n")
    elif command == "send_message":
        if show_received_messages:
            print("Received a message:\n>" + addr[0] + "\n>" + value + "\n")
        message_list.append(value)
    elif command == "update_data":
        last_idx = int(value)
        messages_to_send = []
        if last_idx < len(message_list):
            messages_to_send = message_list[last_idx + 1:]
        send_data = [messages_to_send, user_list]
        conn.send(json.dumps(send_data).encode("utf-8"))
    elif command == "disconnect":
        if value in user_list: user_list.pop(user_list.index(value))
    
    conn.close()