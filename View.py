import os
import socket
import threading

from PySimpleGUI import *

ChatSize = 20
serverAddr = ("10.0.0.21", 55000)


class GUI:
    def __init__(self):
        self.gui = PySimpleGUI
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                self.sock.connect(serverAddr)
                read = read_trd(self)
                read.start()
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
                self.sock.send(f"DOWNLOAD@{file_name}".encode('utf-8'))

                # ans = self.sock.recv(1024).decode()
                #
                # if ans == "OK":
                #     self.gui.popup("File Found Starting Download")
                #     with open(self.window["in4"].get(), 'wb') as file:
                #         print("File Opened")
                #         data = 1
                #         while True:
                #             data = self.user.client_sock.recv(1024)
                #             if data.endswith("-@end@-".encode()):
                #                 file.write(data[:-7])
                #                 file.flush()
                #                 file.close()
                #                 print("File Closed")
                #                 break
                #
                #             file.write(data)
                #
                #     print("File Written")

            # show all logges in users
            if event == "-USERS-":
                self.sock.send("SHOWUSERS@".encode('utf-8'))
                self.sock.setsockopt()
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
        self.window["in3"].update(disabled=False)
        self.window["-USERS-"].update(disabled=False)

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
                 self.gui.Button("Clear", 'right', key="clear", size=(15,), disabled=False, pad=((320, 0), 0))
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
                    self.gui.Button("Download", disabled=True, size=(25,), key="-DOWNLOAD-")
                ]
                ,
                [
                    self.gui.Text("Progress Bar"),
                    self.gui.ProgressBar(100, size=(20, 10))
                ]
            ]

        self.window = self.gui.Window("Launcher", layout, size=(1024, 768), grab_anywhere=True)

    # close the chat when client logged out or disconnected
    def close(self):
        self.sock.send("DISCONNECT@LOGGEDOUT".encode('utf-8'))
        self.sock.close()
        exit()

# read_thread class. Gets all the "answers" from the server according to client's commands
class read_trd(threading.Thread):
    def __init__(self, Gui: GUI):
        threading.Thread.__init__(self)
        self.gui = Gui
        self.sock = Gui.sock

    def run(self):
        while True:
            try:
                # receive the server's response. split it to command and data
                msg = self.sock.recv(1024).decode('utf-8')
                cmd = msg[:msg.find("@")]
                data = msg[msg.find("@") + 1:]
                if msg or data or cmd is True:
                    print(f"{msg}\n")

                if cmd == "LOGIN":
                    pass

                # when new client has logged in, change the gui
                elif cmd == "LOGGEDIN":
                    self.gui.update_login()

                # show all the files we get from the server in the gui
                elif cmd == "SHOWFILES":
                    print(data)
                    files = [x for x in data.split('\n')]
                    print(files)
                    self.gui.window["-FILE LIST2-"].update(values=files)

                # show all the users we get from the server in the gui
                elif cmd == "SHOWUSERS":
                    print("Got Users Successfully.\n")
                    users = [x.split("@")[0] for x in data.split('\n')]
                    print(users)
                    self.gui.window["-USERS LIST-"].update(values=users, visible=True)
                    print(data)

                # download a file selected by the client
                elif cmd == "DOWNLOAD":
                    pass

                # show a public message in the chat, sent from one client to all connected users
                elif cmd == "MSG":
                    name = data[:data.find("@")]
                    chat_msg = data[data.find("@") + 1:]
                    if self.gui.message_queue.__len__() >= ChatSize:
                        self.gui.message_queue.pop(0)
                    self.gui.message_queue.append(f"{name} : {chat_msg}")
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

            except os.error as e:
                print("An Error Occured please connect again.\n")
                self.sock.close()
                print(e)
                exit(-1)


if __name__ == '__main__':
    gui = GUI()
    gui.welcome_screen()

# TODO צריך לבדוק לגבי אלגוריתם CC 1.
# TODO להוסיף טרדים לסוקט UDP לשליחת קבצים
# TODO לבדוק קוד ואינפוטים יש טעויות
# TODO בדיקות קצה
