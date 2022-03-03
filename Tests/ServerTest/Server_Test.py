import socket
import unittest
import Server

class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        server = Server()


    def tearDown(self) -> None:

    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
