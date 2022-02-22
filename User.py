import os
import socket

serveraddr = ("127.0.0.1", 45800)


class Client:
    def __init__(self):
        self.sock = socket.socket()
        self.status = "OFFLINE"
        self.name = ""


if __name__ == '__main__':
    client = Client()
    client.sock.connect(serveraddr)

    while True:
        msg = client.sock.recv(1024).decode('utf-8').split()
        print(msg)
        