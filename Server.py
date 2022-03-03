import os
import socket
from threading import Thread
import time

SERVERADDR = ("", 55000)
SIZE = 1024

# clients = []
active_sockets = {}


class Server:
    def __init__(self, Serveraddr=("127.0.0.1", 55000)):
        self.serverAddr = Serveraddr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active_clients = {}
        self.udpsocks = {}

    def client_main(self, client_sock: socket.socket, client_addr):
        global active_sockets
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
                    msg += '\n'.join(file for file in os.listdir("files"))
                    client_sock.send(msg.encode('utf-8'))

                # shows all logged in users
                elif cmd == "SHOWUSERS":
                    msg = "SHOWUSERS@"
                    msg += '\n'.join(c for c in active_sockets.keys())
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
                self.broadcast(f"Notice@{name} left the chat.\n")
                # remove the client from active_sockets dict
                del self.active_clients[name]

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


class handle_udp(Thread):
    def __init__(self, address, file_name):
        Thread.__init__(self)
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_udp = (address[0], 55015)
        self.window_size = 8
        self.start_time = -1
        self.wait_time = 0.5
        self.filename = file_name

    def run(self):
        packets = []
        num = 0
        print("GOT HERE")
        # open the file with binary
        with open(self.filename, 'rb') as file:
            while True:
                # read chunck of 1020 bytes from file, to build packets with 1024 bytes (+4 bytes- ack's num)
                file_contents = file.read(978)
                print(file_contents)
                while file_contents:
                    # init packets array
                    packets.append(num.to_bytes(4, byteorder="little", signed=True) + file_contents)
                    num += 1
                    # read the next file bytes
                    file_contents = file.read(978)
                file.close()

                pack_len = len(packets)
                print(pack_len)
                next_pack = 0
                counter_packets = 0
                window = self.set_window(pack_len, counter_packets)

                while counter_packets < pack_len:
                    while next_pack < counter_packets + window and next_pack < pack_len:
                        print(self.client_udp)
                        # (data,(ip,port))
                        self.udp_sock.sendto(packets[next_pack], self.client_udp)
                        next_pack += 1
                    self.timer_start()
                    while self.timer_running() and not self.timer_timeout():
                        data = self.udp_sock.recvfrom(64)  # data= (msg, (ip, port)) #ack
                        if data:
                            ack = data[0].decode()
                            if int(ack) >= counter_packets:
                                counter_packets = int(ack) + 1
                                self.stop_timer()
                            else:
                                counter_packets = int(ack)
                                next_pack = counter_packets
                                self.stop_timer()
                    if self.timer_timeout():
                        self.stop_timer()
                        next_pack = counter_packets

                    else:
                        print("shifting window")
                        self.window_size = self.set_window(pack_len, counter_packets)
                break

    def timer_start(self):
        if self.start_time == -1:
            self.start_time = time.time()

    def set_window(self, num_packets, base):
        return min(self.window_size, num_packets - base)

    def timer_running(self):
        return self.start_time != -1

    def timer_timeout(self):
        if not self.timer_running():
            return False
        else:
            return time.time() - self.start_time >= self.wait_time

    def stop_timer(self):
        if self.start_time != -1:
            self.start_time = -1


if __name__ == '__main__':
    server = Server()
    server.start()
