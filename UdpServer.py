from socket import *
import os
from aioquic.quic import stream
import asyncio
import http3
from aioquic.h3 import connection
if __name__ == '__main__':
    socket = socket(AF_INET, SOCK_DGRAM)
    socket.bind(("",443))



