#import rbc
import threading
import socket

'''global black, red
black = []
red = []

MUTEX = threading.Lock()

def camera():
    global red, black
    while True:
        print 'Get Caps...', red, black
        r, b = rbc.get_caps()
        #MUTEX.acquire()
        red, black = r, b
        #MUTEX.release()
'''
def new_client(conn, addr):
    #global red, black
    print 'Connection address:', addr
    
    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data: break
    
        pontos = open('caps.txt').read().split('(8*8)')

        if '0' in data:
            conn.send(pontos[0])
            #if len(red) > 0:
                #MUTEX.acquire()
                #conn.send(str(red[0][0]) + " " + str(red[0][1]) + " 0")
                #MUTEX.release()
            #else:
                #conn.send("0 0 0")
        else:
            conn.send(pontos[1])
            #if len(black) > 0:
                #MUTEX.acquire()
                #conn.send(str(black[0][0]) + " " + str(black[0][1]) + " 0")
                #MUTEX.release()
            #else:
                #conn.send("0 0 0")

    conn.close()

MUTEX = threading.Lock()
TCP_IP = '192.168.0.153'
TCP_PORT = 5005
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

#c = threading.Thread(target=camera, args=())
#c.start()

while True:
    t_c = threading.Thread(target=new_client, args=(s.accept()))
    t_c.start()
