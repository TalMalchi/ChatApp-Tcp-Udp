import os
import socket
import fcntl
import errno
import select

serveraddr = ("10.0.0.5", 55000)


class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.status = "OFFLINE"
        self.name = ""


if __name__ == '__main__':
    client = Client()
    client.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.sock.connect(serveraddr)

    # Connecting to Server.

    while True:
        try:
            msg = client.sock.recv(1024).decode('utf-8').split('@')
            print(msg)
        except socket.error as e:
            pass



