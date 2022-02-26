from socket import *
import os
from aioquic.quic import stream
import asyncio
import http3
from aioquic.h3 import connection
if __name__ == '__main__':
    sock = socket(AF_INET, SOCK_DGRAM)
    while True:
        sock.sendto(b"This is msg", ("10.0.0.19", 55015))


