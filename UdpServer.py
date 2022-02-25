from socket import *
import os
import aioquic

if __name__ == '__main__':
    socket = socket(AF_INET, SOCK_DGRAM)
    socket.bind(("",443))

    aioquic.__version__

