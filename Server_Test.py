import os
import signal
import socket
import threading
import time
import Server
from unittest import TestCase


def waitmessage(sock):
    while True:
        data = sock.recv(1024)
        if data:
            msg = data.decode('utf-8')
            return msg
        else:
            time.sleep(0.1)


class ServerTest(TestCase):
    trd: threading.Thread = None
    clientSock = None
    ServerAddr = None
    server_check = None

    # each time we run this test class we connect "default client"
    # LOGIN+LOGGEDIN test
    @classmethod
    def setUpClass(cls):
        cls.trd = threading.Thread(target=cls.trd, args=[])
        cls.trd.start()
        ServerAddr = ("127.0.0.1", 55000)
        cls.clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.clientSock.connect(ServerAddr)
        msg1 = cls.clientSock.recv(1024).decode('utf-8')
        cls.clientSock.send(f"LOGIN@tal@abc".encode('utf-8'))
        msg2 = cls.clientSock.recv(1024).decode('utf-8')
        # cls.assertEqual( "LOGIN@Connected Succesfully.\n", msg1)
        # cls.assertEqual("LOGGEDIN@Logged In Succesfully\n", msg2)

    # when the tests end, we close the client's socket
    @classmethod
    def tearDownClass(cls) -> None:
        cls.clientSock.close()
        cls.server_check = None
        cls.trd = None
        cls.clientSock = None
        cls.ServerAddr = None

    def test_SHOW_FILES(self):
        self.clientSock.send("SHOWFILES@Give me all files in server".encode('utf-8'))
        msg4 = waitmessage(self.clientSock)
        self.assertEqual(msg4.split('@')[0], "SHOWFILES")

    def test_SHOW_USERS(self):
        self.clientSock.send("SHOWUSERS@".encode('utf-8'))
        msg3 = waitmessage(self.clientSock)
        self.assertEqual("SHOWUSERS@tal", msg3)

    def test_MSG(self):
        ServerAddr = ("127.0.0.1", 55000)
        another_clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        another_clientSock.connect(ServerAddr)
        msg = waitmessage(another_clientSock)
        another_clientSock.send(f"LOGIN@itay@abc".encode('utf-8'))
        msg1 = waitmessage(another_clientSock)
        another_clientSock.send(f"PMSG@itay@tal@hii".encode('utf-8'))
        msg3 = waitmessage(self.clientSock)
        msg2 = waitmessage(another_clientSock)
        self.assertEqual("PMSG_S@tal@hii", msg2)
        self.assertEqual("PMSG@itay@hii", msg3)
        another_clientSock.send("DISCONNECT@itay".encode('utf-8'))
        msg4 = waitmessage(self.clientSock)
        another_clientSock.close()

    # server's thread
    @classmethod
    def trd(cls):
        cls.server_check = Server.Server()
        cls.server_check.start()
