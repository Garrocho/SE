# -*- coding: utf-8 -*-

import numpy as np
import socket

from time import time

TCP_IP = '127.0.0.1'
TCP_PORT = 6671
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

# Link lengths
a = np.array([[6.9], [10.5], [7.6], [14.5]], dtype=float)
# Link displacements
d = np.array([[2.0], [0.0], [3.0]], dtype=float)
# Mechanical limits
q_min = np.array([[-84.0 * np.pi / 180.0], [17.0 * np.pi / 180.0],
                  [-90.0 * np.pi / 180.0], [-90.0 * np.pi / 180.0]],
                 dtype=float)
q_max = np.array([[66.0 * np.pi / 180.0], [159.0 * np.pi / 180.0],
                  [0.0 * np.pi / 180.0], [-45.0 * np.pi / 180.0]],
                 dtype=float)


while True:
    conn, addr = s.accept()
    data = conn.recv(BUFFER_SIZE)
    if not data:
        continue
    coords = data.decode('utf-8').split(' ')
    length = len(coords)
    if length != 3:
        print('Wrong Format! Coords has length equal to {}, its length must be equal to 3'.format(length))
        conn.send('-1')
        conn.close()
        continue
    coords = [float(c.replace('\x00', '')) for c in coords]
    print(coords)
    # Initial joint configuration
    q = np.array([[0], [0], [-90], [0]], dtype=float)
    q = np.deg2rad(q)
    # Expected end-effector coordinates
    xd = np.array([[coords[0]], [coords[1]], [coords[2]]], dtype=float)
    # Expected end-effector velocities
    xd_d = np.array([[0], [0], [0]], dtype=float)
    e_abs = 100000
    count = 0
    t0 = time()
    while True:
        count += 1
        # Direct kinematics
        xe = np.array([
            [d[0, 0] * np.cos(q[0, 0]) + a[1, 0] * np.cos(q[0, 0]) * np.cos(q[1, 0]) + a[2, 0] * np.cos(q[0, 0]) * np.cos(q[1, 0] + q[2, 0]) + d[2, 0]
             * np.cos(q[0, 0]) * np.cos(q[1, 0] + q[2, 0] + q[3, 0] + np.pi / 2) + a[3, 0] * np.cos(q[0, 0]) * np.cos(q[1, 0] + q[2, 0] + q[3, 0])],
            [d[0, 0] * np.sin(q[0, 0]) + d[2, 0] * np.sin(q[0, 0]) * np.cos(q[1, 0] + q[2, 0] + q[3, 0] + np.pi / 2) + a[1, 0] * np.sin(q[0, 0]) * np.cos(
                q[1, 0]) + a[2, 0] * np.sin(q[0, 0]) * np.cos(q[1, 0] + q[2, 0]) + a[3, 0] * np.sin(q[0, 0]) * np.cos(q[1, 0] + q[2, 0] + q[3, 0])],
            [a[0, 0] + a[1, 0] * np.sin(q[1, 0]) + a[2, 0] * np.sin(q[1, 0] + q[2, 0]) + d[2, 0] * np.sin(
                q[1, 0] + q[2, 0] + q[3, 0] + np.pi / 2) + a[3, 0] * np.sin(q[1, 0] + q[2, 0] + q[3, 0])]
        ], dtype=float)
        # Position error
        e = xd - xe
        # Euclidean distance
        e_abs = np.sqrt(np.sum(e ** 2))
        if e_abs <= 1e-2 or count >= 1000:
            break
        # Controller gain matrix
        K = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=float)
        # Jacobian
        J = np.array([
            [-np.sin(q[0, 0]) * (d[0, 0] + a[1, 0] * np.cos(q[1, 0]) + a[2, 0] * np.cos(q[1, 0] + q[2, 0]) + d[2, 0] * np.cos(q[1, 0] + q[2, 0] + q[3, 0] + np.pi / 2) + a[3, 0] * np.cos(q[1, 0] + q[2, 0] + q[3, 0])), -np.cos(q[0, 0]) * (a[1, 0] * np.sin(q[1, 0]) + a[2, 0] * np.sin(q[1, 0] + q[2, 0]) + d[2, 0] * np.sin(q[1, 0] + q[2, 0] + q[3, 0] + np.pi / 2) + a[3, 0] * np.sin(q[1, 0] + q[2, 0] + q[3, 0])), -np.cos(q[0, 0]) * (a[2, 0] * np.sin(q[1, 0] + q[2, 0]) + d[2, 0] * np.sin(q[1, 0] + q[2, 0] + q[3, 0] + np.pi / 2) + a[3, 0] * np.sin(q[1, 0] + q[2, 0] + q[3, 0])), -np.cos(q[0, 0]) * (d[2, 0] * np.sin(q[1, 0] + q[2, 0] + q[3, 0] + np.pi / 2) + a[3, 0] * np.sin(q[1, 0] + q[2, 0] + q[3, 0]))],
            [np.cos(q[0, 0]) * (d[0, 0] + a[1, 0] * np.cos(q[1, 0]) + a[2, 0] * np.cos(q[1, 0] + q[2, 0]) + d[2, 0] * np.cos(q[1, 0] + q[2, 0] + q[3, 0] + np.pi / 2) + a[3, 0] * np.cos(q[1, 0] + q[2, 0] + q[3, 0])), -np.sin(q[0, 0]) * (a[1, 0] * np.sin(q[1, 0]) + a[2, 0] * np.sin(q[1, 0] + q[2, 0]) + d[2, 0] * np.sin(q[1, 0] + q[2, 0] + q[3, 0] + np.pi / 2) + a[3, 0] * np.sin(q[1, 0] + q[2, 0] + q[3, 0])), -np.sin(q[0, 0]) * (a[2, 0] * np.sin(q[1, 0] + q[2, 0]) + d[2, 0] * np.sin(q[1, 0] + q[2, 0] + q[3, 0] + np.pi / 2) + a[3, 0] * np.sin(q[1, 0] + q[2, 0] + q[3, 0])), -np.sin(q[0, 0]) * (d[2, 0] * np.sin(q[1, 0] + q[2, 0] + q[3, 0] + np.pi / 2) + a[3, 0] * np.sin(q[1, 0] + q[2, 0] + q[3, 0]))],
            [0,  a[1, 0] * np.cos(q[1, 0]) + a[2, 0] * np.cos(q[1, 0] + q[2, 0]) + d[2, 0] * np.cos(q[1, 0] + q[2, 0] + q[3, 0] + np.pi / 2) + a[3, 0] * np.cos(q[1, 0] + q[2, 0] + q[3, 0]),  a[2, 0] * np.cos(q[1, 0] + q[2, 0]) + d[2, 0] * np.cos(q[1, 0] + q[2, 0] + q[3, 0] + np.pi / 2) + a[3, 0] * np.cos(q[1, 0] + q[2, 0] + q[3, 0]), d[2, 0] * np.cos(q[1, 0] + q[2, 0] + q[3, 0] + np.pi / 2) + a[3, 0] * np.cos(q[1, 0] + q[2, 0] + q[3, 0])],
        ], dtype=float)
        # Jacobian's pseudo-inverse
        Jps = np.matmul(J.transpose(),
                        np.linalg.inv(np.matmul(J, J.transpose())))
        # Joint velocities
        q_d = np.matmul(Jps, xd_d + np.matmul(K, e))
        # New joint configuration
        q = q + q_d
        # Mechanical limits verification
        for i in range(len(q)):
            q[i, 0] = q_min[i, 0] if q[i, 0] < q_min[i, 0] else q[i, 0]
            q[i, 0] = q_max[i, 0] if q[i, 0] > q_max[i, 0] else q[i, 0]
    dt = time() - t0
    q = np.rad2deg(q)
    print(q)
    print(e_abs)
    print(dt)
    result = ' '.join([angle[0].astype(str) for angle in q])
    conn.send(result.encode('utf-8'))
    conn.close()
