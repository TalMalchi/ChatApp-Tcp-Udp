import socket
from unittest import TestCase


class MyTestCase(TestCase):
    def setUp(self) -> None:
        serverAddr = ("127.0.0.1",55000)
        serverSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        serverSock.bind(serverAddr)

    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
