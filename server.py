import socket

sock = socket.socket()
sock.bind(("", 14090))

sock.listen(1000)

while True:
    conn, addr = sock.accept()
    
    data = conn.recv(16384)
    
    print("Received a message:\n>" + addr[0] + "\n>" + data.decode("utf-8"))
    
    conn.close()