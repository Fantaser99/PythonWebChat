import socket
import json
import os
import configparser 


config = configparser.ConfigParser()
config.read("config.ini")
server_port = int(config['DEFAULT']['default_port'])
server_name = config['DEFAULT']['server_name']

user_list = []
with open("saved_data.txt") as fin:
    message_list, colors, highlight_patterns = json.loads(fin.read())
print("Successfully loaded saved data:")
print("  " + str(len(message_list)) + " messages, ")
print("  " + str(len(colors)) + " colors, ")
print("  " + str(len(highlight_patterns)) + " highlight patterns.")

input("Start server?")

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

show_received_messages = False
show_connections       = True

while True:
    conn, addr = sock.accept()
    print(highlight_patterns)
    
    # All data, that this server receives, consists of a command and a value.
    # A command tells the server, what the client is sending and what he wants
    # to receive, and the value - is the main information (last_idx, msg, etc.)
    command, value = json.loads(conn.recv(16384).decode("utf-8"))
    
    if command == "check_connection":
        conn.send(server_name.encode("utf-8"))
        if value:
            username, username_color = value
            user_list.append(username)
            highlight_patterns.append(value)
            colors.append(username_color)
            message_list.append("Server> " + username + " connected!")
            if show_connections:
                print("Connected: \n      IP: " + addr[0] + 
                                                 "\nUsername: " + username + "\n")
    elif command == "send_message":
        if show_received_messages:
            print("Received a message:\n>" + addr[0] + "\n>" + value + "\n")
        message_list.append(value)
    elif command == "update_data":
        last_idx = int(value)
        messages_to_send = []
        if last_idx < len(message_list):
            messages_to_send = message_list[last_idx + 1:]
        send_data = [messages_to_send, user_list, colors, highlight_patterns]
        conn.send(json.dumps(send_data).encode("utf-8"))
    elif command == "disconnect":
        if value in user_list: user_list.pop(user_list.index(value))
        message_list.append("Server> " + value + " disconnected.")
        if show_connections:
            print("Disconnected: \n      IP: " + addr[0] + 
                                                 "\nUsername: " + value + "\n")
    elif command == "save_data":
        with open("saved_data.txt", 'w') as fout:
            fout.write(json.dumps([message_list, colors, highlight_patterns]))
    
    conn.close()