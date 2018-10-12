import threading
import socket

def new_client(conn, addr):
    print 'Connection address:', addr
    
    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data: break
    
        pontos = open('caps.txt').read().split('(8*8)')

        if '0' in data:
            conn.send(pontos[0])
        else:
            conn.send(pontos[1])

    conn.close()

MUTEX = threading.Lock()
TCP_IP = '0.0.0.0'
TCP_PORT = 5005
BUFFER_SIZE = 20

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

while True:
    t_c = threading.Thread(target=new_client, args=(s.accept()))
    t_c.start()
