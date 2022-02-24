import socket
import threading
import os

serverAddr = ("10.0.0.15", 55000)
SIZE = 1024
messageList: list = []

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(serverAddr)


def conn_read():
    while True:
        try:
            msg = sock.recv(SIZE).decode('utf-8')
            cmd = msg[:msg.find("@")]
            data = msg[msg.find("@") + 1:]

            if cmd == "LOGIN":
                print(data)
                messageList.append("LOGIN")
                print(messageList)

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
            sock.close()
            print(e)
            exit(-1)


def conn_write():
    print("Write Conn working\n")
    while True:
        if messageList.__len__() > 0:
            cmd = messageList.pop(0)

            if cmd == "LOGIN":
                a = input()
                print(a)
                msg = f"LOGIN@{input()}".encode('utf-8')
                sock.send(msg)

            elif cmd == "LOGGEDIN":
                pass

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


if __name__ == '__main__':
    read_trd = threading.Thread(target=conn_read())
    read_trd.start()
    print("Got \n")
    write_trd = threading.Thread(target=conn_write())
    write_trd.start()
    print("Tread should work\n")