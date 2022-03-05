import collections
import math
import os
import socket
import time
from threading import Thread
from PySimpleGUI import *

ChatSize = 20
serverAddr = ("127.0.0.1", 55000)


class GUI:
    def __init__(self):
        self.readtrd: read_trd = None
        self.gui = PySimpleGUI
        self.sock: socket.socket = None
        self.window: PySimpleGUI.Window = None
        self.window_length = 1024
        self.window_height = 768
        self.message_queue: list = []

    # the initial screen before the connection to the server is established
    def welcome_screen(self):
        welcome = [
            [
                self.gui.Button(size=(25, 1), button_text="Start", key="startBtn")

            ]
        ]

        self.window = self.gui.Window("Launcher", welcome, grab_anywhere=True)
        # when the connection to the server is established "helloScreen" opens
        while True:
            event, values = self.window.read()
            if event == "OK" or event == self.gui.WINDOW_CLOSED:
                break
            if event == "startBtn":
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect(serverAddr)
                self.readtrd = read_trd(self)
                self.readtrd.start()
                self.helloScreen()

            else:
                self.gui.popup_error("Couldnt connect to server, try again.")

    # the screen opens when new client connects to the server, and can start using the chat
    def helloScreen(self):
        self.set_layout()

        # all the commands the client can choose from the screen.
        while True:
            event, values = self.window.read()
            if event == "OK" or event == self.gui.WINDOW_CLOSED:
                self.close()
                break

            if event == "login":
                # save the user name and the address of the client
                user_name = self.window["user_name"].get()
                address = self.window["address"].get()
                if not user_name or not address:
                    self.gui.popup_error("Please enter valid username and address")
                else:
                    # send all the details to the server
                    self.sock.send(f"LOGIN@{user_name}@{address}".encode('utf-8'))

            # show all the possible files in the server
            if event == "showFiles":
                self.sock.send("SHOWFILES@Give me all files in server".encode('utf-8'))

            # choose a specific file from the list
            if event == "-FILE LIST2-":
                if len(values["-FILE LIST2-"]) > 0:
                    file_name = values["-FILE LIST2-"][0]
                    self.window["in3"].update(file_name)
                    self.window["in4"].update(file_name)

            # download a specific file from the list
            if event == "-DOWNLOAD-":
                file_name = self.window["in3"].get()
                new_file_name = self.window["in4"].get()
                self.sock.send(f"DOWNLOAD@{file_name}".encode('utf-8'))
                udp_trd = handle_udp_client(new_file_name)
                udp_trd.start()

            if event == "PAUSE":
                if not udp_trd.pause:
                    udp_trd.pause = True
                    self.window["PAUSE"].update(text="Resume")
                else:
                    udp_trd.pause = False
                    self.window["PAUSE"].update(text="Pause")

            if event == "LOGOUT":
                try:
                    self.sock.send("LOGOUT@Logging out\n".encode())
                    self.sock.close()
                except:
                    pass
                self.window.close()
                self.welcome_screen()

            # show all logges in users
            if event == "-USERS-":
                self.sock.send("SHOWUSERS@".encode('utf-8'))

            if event == "-USERS LIST-":
                if len(values["-USERS LIST-"]) > 0:
                    user_name = values["-USERS LIST-"][0]
                    self.window["in1"].update(user_name)

            # send a message
            if event == "btn_send":
                if len(values["in2"]) > 0:
                    sender = values["user_name"]
                    msg = values["in2"]
                    if len(values["in1"]) > 0:
                        send_to = values["in1"]
                        # send a private message to another user
                        self.sock.send(f"PMSG@{sender}@{send_to}@{msg}".encode('utf-8'))
                    else:
                        # send a message to all the activities users
                        self.sock.send(f"MSG@{sender}@{msg}".encode('utf-8'))

    # update the gui when new client logged in successfully
    def update_login(self):
        self.window["__Status__"].update("Online", text_color="green")
        self.window["user_name"].update(disabled=True)
        self.window["address"].update(disabled=True)
        self.window["showFiles"].update(disabled=False)
        self.window["-DOWNLOAD-"].update(disabled=False)
        self.window["btn_send"].update(disabled=False)
        self.window["in1"].update(disabled=False)
        self.window["in2"].update(disabled=False)
        self.window["in3"].update(disabled=True)
        self.window["-USERS-"].update(disabled=False)
        self.window["LOGOUT"].update(disabled=False)
        self.window["PAUSE"].update(disabled=False)

    # "helloScreen" - opens when new client connects to the server
    def set_layout(self):
        layout = \
            [
                [self.gui.Button("login", size=(15,), pad=((0, 10), 0)),
                 self.gui.Text("name", size=(5,), pad=((0, 10), 0)),
                 self.gui.In("", (15,), pad=((0, 10), 0), key="user_name"),
                 self.gui.Text("address", pad=((0, 10), 0)),
                 self.gui.In("", size=(15,), pad=((0, 10), 0), key="address"),
                 self.gui.Text("status:", pad=((0, 10), 0)),
                 self.gui.Text("offline", text_color="red", font=('MS Sans Serif', 10, 'bold'), key="__Status__",
                               pad=((0, 10), 0)),
                 self.gui.Button("Logout", key="LOGOUT", size=(15,), disabled=True, pad=((320, 0), 0))
                 ],

                [
                    self.gui.Button("Show Server Files", disabled=True, key="showFiles"),
                    self.gui.Button("Show Online Users", disabled=True, key="-USERS-", size=(15,), pad=(10, 0))

                ],
                [
                    self.gui.Text("Chat"),
                    self.gui.Text("Server Files", pad=((550, 0), 0)),
                    self.gui.Text("Online", pad=((235, 0), 0))
                ]
                ,
                [
                    self.gui.Listbox(
                        values=[], enable_events=True, size=(80, 30), key="-Chat-",
                    ),
                    self.gui.Listbox(
                        values=[], enable_events=True, size=(40, 30), key="-FILE LIST2-"
                    ), self.gui.Listbox(
                    values=[], enable_events=True, size=(20, 30), key="-USERS LIST-"
                )
                ],

                [
                    self.gui.Text("To (blank to all)", size=(25,), pad=((0, 15), 0)),
                    self.gui.Text("Message", pad=((0, 15), 0))
                ],

                [
                    self.gui.Input(disabled=True, size=(25,), disabled_readonly_background_color="grey", key="in1"),
                    self.gui.Input(disabled=True, size=(100,), disabled_readonly_background_color="grey", key="in2")
                    , self.gui.Button("Send", disabled=True, size=(25,), key="btn_send")
                ],

                [
                    self.gui.Text("Server File Name", size=(25,), pad=((0, 15), 0)),
                    self.gui.Text("Client File Name (save as..)", pad=((0, 15), 0))
                ],

                [
                    self.gui.Input("", disabled=True, disabled_readonly_background_color="grey",
                                   size=(25,), key="in3"),
                    self.gui.Input("", size=(25,), key="in4"),
                    self.gui.Button("Download", disabled=True, size=(25,), key="-DOWNLOAD-"),
                    self.gui.Button("Pause", disabled=True, size=(25,), key="PAUSE")

                ]
                ,
                [
                    self.gui.Text("Progress Bar"),
                    self.gui.ProgressBar(100, size=(20, 10))
                ]
            ]
        self.window.close()
        self.window = self.gui.Window("Launcher", layout, size=(1024, 768), grab_anywhere=True)

    # close the chat when client logged out or disconnected
    def close(self):
        try:
            self.sock.send("DISCONNECT@LOGGEDOUT".encode('utf-8'))
            self.sock.close()
            exit(-1)
        except:
            exit(-1)


# download a file with UDP connection
class handle_udp_client(Thread):
    def __init__(self, filename):
        Thread.__init__(self)
        self.windowrate = 2
        self.packets = {}
        self.packets_ack = []
        self.expected = 0
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # init new UDP socket
        self.udp_server = None
        self.pause = False
        self.filename = filename
        self.windowSize = 1
        self.windowLen = 0
        self.currpac = 0
        self.timeout_time = 0.2
        self.timer = time.time()

    # main run thread function

    def run(self):
        self.udp_sock.bind(("", 55014))
        self.udp_sock.setblocking(0)
        self.get_packets_len()

        start = datetime.datetime.now()
        print(start)
        while self.currpac < self.expected:
            self.timer = time.time()
            while self.packets_ack.__len__() < self.windowSize and not self.timeout():
                try:
                    data = self.udp_sock.recv(1024)
                    if data:
                        ack, packet = self.packet_info(data)
                        if ack not in self.packets.keys():
                            self.packets[ack] = packet
                            self.currpac += 1
                        self.packets_ack.append(str(ack))
                    else:
                        time.sleep(0.01)
                except:
                    time.sleep(0.01)
            self.timer = time.time()


            while self.packets_ack.__len__() > 0 and not self.timeout():
                for ack in self.packets_ack:
                    self.udp_sock.sendto(ack.encode('utf-8'), self.udp_server)

                    self.packets_ack.remove(ack)

            if self.packets_ack.__len__() > 0:
                self.windowrate = 1
                self.update_window()
            else:
                self.update_window()

        print(self.currpac)
        # writes the file
        with open(self.filename, 'wb') as f:
            for p in sorted(self.packets.keys()):
                print("Writing file part num - " , p)
                data = self.packets[p]
                f.write(data)
                f.flush()

        f.close()
        self.udp_sock.close()
        end = datetime.datetime.now()
        print(end)
        print(end-start)
        # self.end_connection()


    def update_window(self):
        if self.windowrate == 1 and not self.windowSize > min(math.pow(2, 31),self.expected):
            self.windowSize += 1
        elif self.windowrate == 2 and not self.windowSize > min(math.pow(2, 31),self.expected):
            self.windowSize *= 2

    def handle_duplicates(self, packets):
        i = 0
        while i < len(packets) - 1:
            if packets[i][0] == packets[i + 1][0]:
                del packets[i + 1]
            else:
                i += 1
        return packets

    def send_filename(self, filename):
        return self.udp_sock.sendto(filename.encode(), self.udp_server)

        # def end_connection(self):
        #     self.udp_sock.close()

    def make_packet(self, acknum, data=b''):  # איפה משתמשים בזה?????
        ackbytes = acknum.to_bytes(4, byteorder='little', signed=True)
        return ackbytes + data

        # extract packet's information from bytes to int

    def packet_info(self, packet):
        num = int.from_bytes(packet[0:4], byteorder='little', signed=True)
        return num, packet[4:]

    def get_packets_len(self):
        while True:
            time.sleep(0.5)
            try:
                data, self.udp_server = self.udp_sock.recvfrom(64)
                if data:
                    self.expected = int(data.decode('utf-8'))
                    print(self.expected)
                    self.udp_sock.sendto(data, self.udp_server)
                    time.sleep(1)
                    break

            except BlockingIOError:
                pass

    def timeout(self):
        return (time.time() - self.timer) > (min(self.windowSize*0.5, 0.5))


# read_thread class. Gets all the "answers" from the server according to client's commands
class read_trd(Thread):
    def __init__(self, Gui: GUI):
        Thread.__init__(self)
        self.gui = Gui
        self.sock = Gui.sock

    def run(self):
        while True:
            try:
                # receive the server's response. split it to command and data
                msg = self.sock.recv(1024).decode('utf-8')
                cmd = msg[:msg.find("@")]
                data = msg[msg.find("@") + 1:]

                if cmd == "LOGIN":
                    pass

                # when new client has logged in, change the gui
                elif cmd == "LOGGEDIN":
                    self.gui.update_login()

                # show all the files we get from the server in the gui
                elif cmd == "SHOWFILES":
                    files = [x for x in data.split('\n')]
                    self.gui.window["-FILE LIST2-"].update(values=files)

                # show all the users we get from the server in the gui
                elif cmd == "SHOWUSERS":
                    users = [x for x in data.split('\n')]
                    self.gui.window["-USERS LIST-"].update(values=users, visible=True)

                # download a file selected by the client
                elif cmd == "DOWNLOAD":
                    pass

                # show a public message in the chat, sent from one client to all connected users
                elif cmd == "MSG":
                    name = data[:data.find("@")]
                    chat_msg = data[data.find("@") + 1:]
                    new_msg = "".join([chat_msg[i:i + 30] + "\n" for i in range(0, len(chat_msg), 30)])
                    if self.gui.message_queue.__len__() >= ChatSize:
                        self.gui.message_queue.pop(0)
                    self.gui.message_queue.append(f"{name} : {new_msg}")
                    self.gui.window["-Chat-"].update(values=self.gui.message_queue)

                # show a private message in the chat, sent from one client to another
                elif cmd == "PMSG":
                    name = data[:data.find("@")]
                    chat_msg = data[data.find("@") + 1:]
                    if self.gui.message_queue.__len__() >= ChatSize:
                        self.gui.message_queue.pop(0)
                    self.gui.message_queue.append(f"(Private) {name} : {chat_msg}")
                    self.gui.window["-Chat-"].update(values=self.gui.message_queue)

                elif cmd == "PMSG_S":
                    name = data[:data.find("@")]
                    chat_msg = data[data.find("@") + 1:]
                    if self.gui.message_queue.__len__() >= ChatSize:
                        self.gui.message_queue.pop(0)
                    self.gui.message_queue.append(f"(Private to) {name} : {chat_msg}")
                    self.gui.window["-Chat-"].update(values=self.gui.message_queue)

                elif cmd == "Notice":
                    if self.gui.message_queue.__len__() >= ChatSize:
                        self.gui.message_queue.pop(0)
                    self.gui.message_queue.append(data)
                    self.gui.window["-Chat-"].update(values=self.gui.message_queue)

            except os.error as e:
                self.sock.close()
                exit(-1)


if __name__ == '__main__':
    gui = GUI()
    gui.welcome_screen()

# TODO צריך לבדוק לגבי אלגוריתם CC 1.
# TODO לבדוק קוד ואינפוטים יש עטויות
# TODO בדיקות קצה
# TODO לדאוג למחיקת משתמש ב Signals מסויימים
