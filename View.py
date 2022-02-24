import os
import socket
import threading

from PySimpleGUI import *


serverAddr = ("10.0.0.5", 55000)


class GUI:
    def __init__(self):
        self.gui = PySimpleGUI
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.window: PySimpleGUI.Window = None
        self.window_length = 1024
        self.window_height = 768


    def welcome_screen(self):
        welcome = [
            [
                self.gui.Button(size=(25, 1), button_text="Start", key="startBtn")

            ]
        ]

        self.window = self.gui.Window("Launcher", welcome, grab_anywhere=True)

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

    def helloScreen(self):
        self.set_layout()

        while True:
            event, values = self.window.read()
            if event == "OK" or event == self.gui.WINDOW_CLOSED:
                self.close()
                break

            if event == "login":
                user_name = self.window["user_name"].get()
                address = self.window["address"].get()
                if not user_name or not address:
                    self.gui.popup_error("Please enter valid username and address")
                else:
                    self.sock.send(f"LOGIN@{user_name}@{address}".encode('utf-8'))

            if event == "showFiles":
                self.sock.send("SHOWFILES@Give me all files in server".encode('utf-8'))

            if event == "-FILE LIST2-":
                if len(values["-FILE LIST2-"]) > 0:
                    file_name = values["-FILE LIST2-"][0]
                    self.window["in3"].update(file_name)
                    self.window["in4"].update(file_name)

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

            if event == "-USERS-":
                data = self.sock.send("SHOWUSERS@".encode('utf-8'))

            if event == "-USERS LIST-":
                if len(values["-USERS LIST-"]) > 0 :
                    user_name = values["-USERS LIST-"][0]
                    self.window["in1"].update(user_name)

            if event == "btn_send":
                if len(values["in1"]) > 0:
                    self.sock.send(f"PMSG@{values[in1]}@{values[in2]}".encode('utf-8'))
                else:
                    self.sock.send(f"MSG@{values[in2]}".encode('utf-8'))


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
                    self.gui.Listbox(
                        values=[], enable_events=True, size=(90, 30), key="-FILE LIST2-"
                    ),
                    self.gui.Listbox(
                        values=[], enable_events=True, size=(40, 30), key="-USERS LIST-"
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


def close(self):
    self.user.client_sock.send("connection closed".encode())
    self.user.client_sock.close()
    exit()


class read_trd(threading.Thread):
    def __init__(self, Gui: GUI):
        threading.Thread.__init__(self)
        self.gui = Gui
        self.sock = Gui.sock

    def run(self):
        while True:
            try:
                msg = self.sock.recv(1024).decode('utf-8')
                cmd = msg[:msg.find("@")]
                data = msg[msg.find("@") + 1:]
                if msg or data or cmd is True:
                    print(f"{msg}\n")

                if cmd == "LOGIN":
                    pass

                elif cmd == "LOGGEDIN":
                    self.gui.update_login()

                elif cmd == "SHOWFILES":
                    print(data)
                    files = [x for x in data.split('\n')]
                    print(files)
                    self.gui.window["-FILE LIST2-"].update(values=files)

                elif cmd == "SHOWUSERS":
                    print("Got Users Successfully.\n")
                    users = [x.split("@")[0] for x in data.split('\n')]
                    print(users)
                    self.gui.window["-USERS LIST-"].update(values=users, visible=True)
                    print(data)

                elif cmd == "DOWNLOAD":
                    pass

                elif cmd == "MSG":
                    print(data)
                elif cmd == "PMSG":
                    pass

            except os.error as e:
                print("An Error Occured please connect again.\n")
                self.sock.close()
                print(e)
                exit(-1)





if __name__ == '__main__':
    gui = GUI()
    gui.welcome_screen()
