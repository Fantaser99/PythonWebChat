import socket

sock = socket.socket()
sock.bind(("", 14000))

sock.listen(100)

print("Server IP: " + socket.gethostbyname(socket.gethostname()))

while True:
    conn, addr = sock.accept()
    
    data = conn.recv(16384)
    
    print("Received a message:\n>" + addr[0] + "\n>" + data.decode("utf-8"))
    
    conn.send(b'Success')
    
    conn.close()
    
    print()