import rbc
import threading
import socket

def new_client(conn, addr):
    print 'Connection address:', addr
    
    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        print "received data:", data
    
        MUTEX.acquire()
        caps = rbc.get_caps()
        MUTEX.release()
        
        print "received data:", data
        conn.send(caps)  # echo

    conn.close()

MUTEX = threading.Lock()
TCP_IP = '192.168.0.152'
TCP_PORT = 5006
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

while True:
    t = threading.Thread(target=new_client, args=(s.accept()))
    t.start()
