import socket
from threading import Thread
import os

serverAddr = ("10.0.0.5", 55000)
SIZE = 1024


class Model:
    def __init__(self , control):
        self.controller = control
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.read_trd = connRead(self)
        self.write_trd = connWrite(self)
        self.messageList: list = []

    def start(self):
        self.sock.connect(serverAddr)
        self.read_trd.start()
        print("Got \n")
        self.write_trd.start()
        print("Tread should work\n")


class connRead(Thread):
    def __init__(self, model):
        Thread.__init__(self)
        self.model = model
        self.sock = model.sock

    def run(self):
        while True:
            try:
                msg = self.sock.recv(SIZE).decode('utf-8')
                cmd = msg[:msg.find("@")]
                data = msg[msg.find("@") + 1:]
                if msg or data or cmd is True:
                    print(f"{msg}\n")

                if cmd == "LOGIN":
                    self.model.(data)

                elif cmd == "LOGGEDIN":
                    print(data)

                elif cmd == "SHOWFILES":
                    print("Got Files Successfully.\n")
                    print(data)

                elif cmd == "SHOWUSERS":
                    print("Got Users Successfully.\n")
                    print(data)

                elif cmd == "DOWNLOAD":
                    pass

                elif cmd == "MSG":
                    print(data)
                elif cmd == "PMSG":
                    pass

            except os.error as e:
                print("An Error Occured please connect again.\n")
                self.sock.close()
                print(e)
                exit(-1)


class connWrite(Thread):
    def __init__(self, soc , model):
        Thread.__init__(self)
        self.sock = soc
        self.model = model


    def run(self):
        print("Write Conn working\n")
        while True:
            if messageList.__len__() > 0:
                cmd = messageList.pop(0)

                if cmd == "LOGIN":
                    name = input("enter your user name\n")
                    msg = f"LOGIN@{name}".encode('utf-8')
                    self.sock.send(msg)

                elif cmd == "SHOWFILES":
                    print("Got Files Successfully.\n")

                elif cmd == "SHOWUSERS":
                    print("Got Users Successfully.\n")

                elif cmd == "DOWNLOAD":
                    pass

                elif cmd == "MSG":
                    pass

                elif cmd == "PMSG":
                    pass
