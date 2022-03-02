from socket import *

if __name__ == '__main__':
    msg = None
    addr = None
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(("", 55015))

    while True:
        msg, addr = sock.recvfrom(1024)
        print(msg, addr)


