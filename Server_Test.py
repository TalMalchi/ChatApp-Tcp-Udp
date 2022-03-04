import os
import socket
import threading
import time
import Server
from unittest import TestCase


class ServerTest(TestCase):
    def test1(self):
        self.trd = threading.Thread(target=self.trd, args=[])
        self.trd.start()
        ServerAddr = ("127.0.0.1", 55000)
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSock.connect(ServerAddr)
        msg1 = self.clientSock.recv(1024).decode('utf-8')
        print(msg1 + "msg")
        self.assertEqual(msg1, "LOGIN@Connected Succesfully.\n")
        self.clientSock.send(f"LOGIN@tal@abc".encode('utf-8'))
        msg2 = self.clientSock.recv(1024).decode('utf-8')
        print(msg2 + "msg2")
        self.assertEqual("LOGGEDIN@Logged In Succesfully\n", msg2)
        self.clientSock.send("SHOWFILES@Give me all files in server".encode('utf-8'))
        msg4= self.clientSock.recv(1024).decode('utf-8')
        self.assertEqual(msg4, "SHOWFILES@")
        # self.clientSock.send("SHOWUSERS@".encode('utf-8'))
        # msg3 = self.clientSock.recv(1024).decode('utf-8')
        # print(msg3)
        # self.assertEqual("SHOWUSERS@tal", msg3)
        self.clientSock.close()

    def tearDown(self) -> None:
        self.clientSock.close()

    def trd(self):
        server_check = Server.Server()
        server_check.start()

    def test_SHOWUSERS(self):
        self.clientSock.send("SHOWUSERS@xxx".encode('utf-8'))
        msg = self.clientSock.recv(1024).decode('utf-8')
        print(msg + "MOM")
        self.assertEqual("SHOWUSERS@tal",msg)

    def test_LOGOUT(self):
        pass
        # self.assertEqual(msg, "LOGOUT")


