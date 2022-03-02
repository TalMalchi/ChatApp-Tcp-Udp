import os.path
import socket
import sys
import pickle as pk
from threading import *

online_users = {}
server_files = {}


def isUserExists(name):
    if name in online_users.keys():
        return True
    else:
        return False


def sendFile(file_name):
    with open(file_name, 'rb') as file:
        while True:
            data = file.read(SIZE)
            while data:
                client.send(data)
                data = file.read(SIZE)
            if not data:
                client.send("-@end@-".encode())
                file.close()
                return


class ClientThread(Thread):

    def __init__(self, ip, port):
        Thread.__init__(self)
        self.ip: str = ip
        self.port: int = port
        self.name = ""
        self.addr = ""
        print("Server Created Successfully addr : " + self.ip + ":" + str(port))

    def run(self) -> None:
        try:
            while True:
                data = client.recv(SIZE).decode()
                command = data.split(',')

                if command[0] == "login":
                    name = command[1]
                    if not isUserExists(name):
                        client.send("Connected".encode())
                        print("Good")
                        self.name = name
                        self.addr = command[2]
                        online_users[self.name] = [self.ip, self.port, self.addr]
                    else:
                        client.send("User Name Already Exits.".encode())

                elif command[0] == "connection closed":
                    del client_thread[self]
                    del online_users[self.name]
                    client.close()

                elif command[0] == "show files":
                    print(sys.platform.__str__())
                    folder = os.listdir("/Share/Networking/Final_Task/files") \
                        if sys.platform.startswith("win") \
                        else os.listdir("/home/itay/Desktop/Share/Networking/Final_task/files")
                    print(folder)
                    data = pk.dumps(folder)

                    client.send(data)

                elif command[0] == "file":
                    file_name = "files/" + command[1]
                    if os.path.exists(file_name):
                        client.send("OK".encode())
                        sendFile(file_name)
                        print("Hello")

                elif command[0] == "show users":
                    data = [x for x in online_users.keys()]
                    data = pk.dumps(data)
                    client.send(data)

                # client.send("Got Message Successfully".encode())
                # print("Received data:\t From: "+self.ip+":"+str(self.port), data.decode())

        except:
            try:
                client.send("Error in MultiThreadServer".encode())
                del online_users[self.name]
                print()
                return
            except ConnectionError as e:
                print(e)
                del online_users[self.name]
                return


if __name__ == '__main__':

    IP = '127.0.0.1'
    PORT = 55000
    SIZE = 1024

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((IP, PORT))

    clients = []
    server_files["abc.txt"] = "abc goed home"
    server_files["example.txt"] = "example"
    server_files["aaaa.txt"] = "mama"
    server_files["abc.png"] = "papa"

    while True:
        server.listen(15)
        client, addr = server.accept()
        client.send("logged in successfully".encode('utf-8'))
        client_thread = ClientThread(addr[0], addr[1])
        client_thread.start()
        clients.append(client_thread)
        print(clients.__len__())
