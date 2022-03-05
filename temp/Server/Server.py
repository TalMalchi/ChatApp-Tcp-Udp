import math
import os
import socket
from threading import Thread
import time

SIZE = 1024


class Server:
    def __init__(self, Serveraddr=("127.0.0.1", 55000)):
        self.serverAddr = Serveraddr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active_clients = {}
        self.udpsocks = {}

    def client_main(self, client_sock: socket.socket, client_addr):
        # new client logged in successfully
        print(f"New Connection {client_addr} connected successfully.\n")
        client_sock.send("LOGIN@Connected Succesfully.\n".encode('utf-8'))

        # all possible server's responses to commands that a client can execute
        # LOGIN@Itay
        while True:
            try:
                msg = client_sock.recv(SIZE).decode('utf-8')
                cmd = msg[:msg.find("@")]
                data = msg[msg.find("@") + 1:]

                if cmd == "DISCONNECT":
                    self.remove_socket(client_sock)
                    client_sock.close()
                    break
                # connect the client to the chat
                elif cmd == "LOGIN":
                    name = data.split("@")[0]
                    if name in self.active_clients.keys():
                        client_sock.send("Error@User name already exists in the system\n".encode('utf-8'))
                    else:
                        client_sock.send("LOGGEDIN@Logged In Succesfully\n".encode('utf-8'))
                        self.active_clients[name] = client_sock

                elif cmd == "LOGOUT":
                    self.remove_socket(client_sock)
                    break

                # gives all the files in server
                elif cmd == "SHOWFILES":
                    msg = "SHOWFILES@"
                    try:
                        msg += '\n'.join(file for file in os.listdir("files"))
                    except os.error:
                        print("File Dir doesnt Exist")
                    client_sock.send(msg.encode('utf-8'))

                # shows all logged in users
                elif cmd == "SHOWUSERS":
                    print("IN HERE")
                    msg = "SHOWUSERS@"
                    msg += '\n'.join(c for c in self.active_clients.keys())
                    print(msg)
                    client_sock.send(msg.encode('utf-8'))

                # download a file selected by the client
                elif cmd == "DOWNLOAD":
                    data = "files/" + data
                    if os.path.isfile(data):
                        print("file exist")
                        udp_conn = handle_udp(client_sock.getpeername(), data)
                        udp_conn.start()
                        # file_trd = threading.Thread(target=handle_file, args=(data, client_sock.getpeername()[0]))
                        # file_trd.start()

                # send a public message to all activities users using "broadcast" function
                elif cmd == "MSG":
                    sender = data[0:data.find("@")]
                    rest = data[data.find("@") + 1:]
                    self.broadcast(f"MSG@{sender}@{rest}")

                # send a private message to another user
                elif cmd == "PMSG":
                    sender = data[0:data.find("@")]
                    rest = data[data.find("@") + 1:]
                    sendto = rest[0:rest.find("@")]
                    new_msg = rest[rest.find("@") + 1:]
                    self.active_clients[sendto].send(f"PMSG@{sender}@{new_msg}".encode('utf-8'))
                    self.active_clients[sender].send(f"PMSG_S@{sendto}@{new_msg}".encode('utf-8'))

            except:
                print(f"{client_addr} Disconnected from server.\n")
                for k, v in self.active_clients.items():
                    if v is client_sock:
                        self.remove_socket(v)
                        break
                break

    # remove a user when he disconnect
    def remove_socket(self, cl):
        for name, sock in self.active_clients.items():
            if cl is sock:
                # update all the users that this client has left
                del self.active_clients[name]
                self.broadcast(f"Notice@{name} left the chat.\n")
                print(name + "Left the Chat")
                # remove the client from active_sockets dict
                try:
                    cl.close()
                    break
                except socket.error:
                    pass
                break

    # send a message to all activities users
    def broadcast(self, msg):
        #  all over the active sockets, and send the message
        for v in self.active_clients.values():
            v.send(msg.encode('utf-8'))

    def start(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.serverAddr)

        self.sock.listen(15)

        while True:
            # server thread
            client, addr = self.sock.accept()
            thread = Thread(target=self.client_main, args=(client, addr))
            thread.start()


# this class handle with file download with UDP protocol


class handle_udp(Thread):
    def __init__(self, address, file_name):
        Thread.__init__(self)
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_udp = (address[0], 55014)
        self.window_size = 1
        self.window_grow = 2
        self.window = {}
        self.wait_time = 0.5
        self.timeout = 1
        self.filename = file_name
        self.packets_acks = []
        self.packets = []
        self.currPack = 0
        self.timer = time.time()

    def run(self):
        self.prepare_packets()
        self.update_client()
        self.packets_acks = [False for i in range(self.packets.__len__())]
        i = 0
        ack_recv = 0
        pack = 0
        while self.currPack < self.packets.__len__() or self.window.__len__() > 0:

            if self.window.__len__() < self.window_size:
                self.prepare_window()
            for packet in self.window:
                self.udp_sock.sendto(self.window[packet], self.client_udp)
                pack += 1
            print("Total packs sent so far" , pack)
            print("Before Acks recivied - " , self.window.__len__())
            self.timer = time.time()
            self.timeout = min(self.window_size * 0.5, 0.5)
            while not time.time() - self.timer >= self.timeout and self.window.__len__() > 0:
                try:
                    data = self.udp_sock.recvfrom(64)
                    if data:
                        ack = int(data[0].decode('utf-8'))
                        print("ACK : ", ack, ", Ack So Far - ", ack_recv)
                        ack_recv += 1
                        if not self.packets_acks[ack]:
                            self.packets_acks[ack] = True
                        self.window.pop(ack)
                    else:
                        time.sleep(0.1)
                except:
                    time.sleep(0.1)
            print(" window size after pop:" , self.window.__len__())
            print(f"i = {i}")
            i += 1

            # Timout Occured can tell by window size is not 0 (Didnt get all acks)
            if self.window.__len__() > 0:
                self.window_size /= 2
                self.window_grow = 1

            self.update_window()


    def prepare_window(self):
        while self.window.__len__() < self.window_size and self.currPack < self.packets.__len__():
            print("Curr pack = ", self.currPack)
            if not self.packets_acks[self.currPack]:
                self.window[self.currPack] = self.packets[self.currPack]
                self.currPack += 1
            else:
                self.currPack += 1

    def prepare_packets(self):
        num = 0
        # open the file with binary
        with open(self.filename, 'rb') as file:
            while True:
                # read chunck of 1020 bytes from file, to build packets with 1024 bytes (+4 bytes- ack's num)
                file_contents = file.read(978)
                while file_contents:
                    # init packets array
                    self.packets.append(num.to_bytes(4, byteorder="little", signed=True) + file_contents)
                    num += 1
                    # read the next file bytes
                    file_contents = file.read(978)
                file.close()
                return

    def update_window(self):
        if self.window_grow == 1 and not self.window_size > min(math.pow(2, 31),self.packets.__len__()):
            self.window_size += 1
        elif self.window_grow == 2 and not self.window_size > min(math.pow(2, 31),self.packets.__len__()):
            self.window_size *= 2

    def update_client(self):
        while True:
            msg = self.packets.__len__().__str__().encode('utf-8')
            print(msg)
            self.udp_sock.sendto(msg, self.client_udp)
            start = time.time()
            print(time.time() - start)
            while time.time() - start < self.timeout:
                data = self.udp_sock.recv(64)
                if data:
                    len_packets = int(data.decode('utf-8'))
                    if len_packets == self.packets.__len__():
                        return


if __name__ == '__main__':
    server = Server()
    server.start()
