import socket
import pickle as pk


class Client:

    def __init__(self, name=""):
        self.name = name
        self.connected = False
        self.serverAddr = ("127.0.0.1", 55000)
        self.client_sock = socket.socket()

    def __str__(self):
        return f"Client name = {self.name} , Client connected {self.connected} , server address is {self.serverAddr}"

    def __repr__(self):
        return f"Client name = {self.name} , Client connected {self.connected} , server address is {self.serverAddr}"

    def connect(self) -> int:
        try:
            self.client_sock.connect(self.serverAddr)

            data = self.client_sock.recv(1024)
            print('Received from the server :', str(data.decode()))
            return 1

        except ConnectionError as e:
            print(e.__str__())
            return -1

    def login(self, name, addr):
        self.client_sock.send(f"login,{name},{addr}".encode())
        data = self.client_sock.recv(1024).decode()
        if data == "Connected":
            self.connected = True
            return 1, None
        else:
            return -1, data

    def ask_files_list(self) -> list:
        try:
            self.client_sock.send("show files".encode())
            data = self.client_sock.recv(4096)
            try:
                data = pk.loads(data)
            except EOFError as e:
                print(e)
                data = ["error getting files list"]
            print(data, " This is data")
            return data

        except:
            print("Error Reciving files list")

    def ask_users_list(self):
        self.client_sock.send("show users".encode())
        try:
            data = self.client_sock.recv(4096)
            data = pk.loads(data)
        except (EOFError,TimeoutError) as e:
            data = ["error getting users list"]
            print(e)

        return data
# if __name__ == '__main__':
#     a = Client("Itay")
#     a.connect()
#     b = Client("David")
#     b.connect()