import socket
import json
import os


server_port = int(input("Server port: "))

sock = socket.socket()
try:
    sock.bind(("", server_port))
except:
    print("Port is already used.")
    os._exit(0)

sock.listen(100)

server_ip = socket.gethostbyname(socket.gethostname())
print("Started server on " + server_ip + ":" + str(server_port) + "!")

message_list = []

show_received_messages = True

while True:
    conn, addr = sock.accept()
    
    # On the first symbol of the received data there is always a number,
    # which tells the server, what it will receive:
    # 0 - connection check
    # 1 - message 
    # 2 - index of the last client's message
    data = conn.recv(16384).decode("utf-8")
    if len(data) == 0: pass
    elif data[0] == "0":
        conn.send(("Connected to " + server_ip + ":" + 
                   str(server_port) + "!").encode("utf-8"))
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
        conn.send(json.dumps(messages_to_send).encode("utf-8"))
    
    conn.close()