import os
import socket
import fcntl
import errno
import select

serveraddr = ("10.0.0.5", 55000)


class Client:
    def __init__(self):
        self.sock = socket.socket()
        self.status = "OFFLINE"
        self.name = ""


if __name__ == '__main__':
    client = Client()
    client.sock.connect(serveraddr)
    # Setting client socket as non blocking socket using fcntl lib
    flag = fcntl.fcntl(client.sock, fcntl.F_GETFL)
    flag = flag | os.O_NONBLOCK
    fcntl.fcntl(client.sock, fcntl.F_SETFL, flag)

    # Connecting to Server.

    while True:
        try:
            msg = client.sock.recv(1024).decode('utf-8').split('@')
            print(msg)
        except socket.error as e:
            print(True if e.errno in [errno.EAGAIN,errno.EWOULDBLOCK] else False)
            pass



