import socket

sock = socket.socket()
sock.bind(("", 14000))

sock.listen(100)

server_ip = socket.gethostbyname(socket.gethostname())
print("Server IP: " + server_ip)

while True:
    conn, addr = sock.accept()
    
    # On the first symbol of the received data there is always a number,
    # which tells the server, what it will receive:
    # 0 - connection check
    # 1 - message 
    # 2 - index of the last client's message
    data = conn.recv(16384).decode("utf-8")
    if data[0] == "0":
        conn.send(("Connected to " + server_ip + "!").encode("utf-8"))
    elif data[0] == "1":
        data = data[1:]
        print("Received a message:\n>" + addr[0] + "\n>" + data)
    
    conn.close()
    
    print()