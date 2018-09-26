# -*- coding: utf-8 -*-

import socket
import sys

from time import time

if len(sys.argv) > 1:
    coords = ' '.join(sys.argv[1:])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 6670))
    t0 = time()
    s.send(coords.encode('ascii'))
    response = s.recv(512)
    response = response.decode('ascii')
    s.close()
    dt = time() - t0
    print(response)
    print(dt)
else:
    print('Error! Correct usage is "python test.py x y z", where x, y, and z are the desired coordinates')
