import os

from PySimpleGUI import *

from Client2 import Client


class GUI:
    def __init__(self):
        self.gui = PySimpleGUI
        self.window: PySimpleGUI.Window = None
        self.window_length = 1024
        self.window_height = 768
        self.user: Client = Client()

    def file_Browser(self):
        file_list_column = [
            [
                self.gui.Text("Image Folder"),
                self.gui.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
                self.gui.FolderBrowse(),
            ],
            [
                self.gui.Listbox(
                    values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
                )
            ],
        ]

        image_viewer_column = [
            [self.gui.Text("Choose an image from list on left:")],
            [self.gui.Text(size=(40, 1), key="-TOUT-")],
            [self.gui.Image(key="-IMAGE-")],
        ]

        layout = [
            [
                self.gui.Column(file_list_column),
                self.gui.VSeperator(),
                self.gui.Column(image_viewer_column),
            ]
        ]

        window = self.gui.Window("Image Viewer", layout)

        while True:
            event, values = window.read()
            if event == "Exit" or event == self.gui.WIN_CLOSED:
                break

            # Folder name was filled in, make a list of files in the folder
            if event == "-FOLDER-":
                folder = values["-FOLDER-"]
                try:
                    # Get list of files in folder
                    file_list = os.listdir(folder)

                except:
                    file_list = []

                fnames = [
                    f
                    for f in file_list
                    if os.path.isfile(os.path.join(folder, f))
                       and f.lower().endswith((".png", ".gif"))
                ]
                window["-FILE LIST-"].update(fnames)

            elif event == "-FILE LIST-":  # A file was chosen from the listbox
                try:
                    filename = os.path.join(
                        values["-FOLDER-"], values["-FILE LIST-"][0]
                    )
                    window["-TOUT-"].update(filename)
                    window["-IMAGE-"].update(filename=filename)

                except:
                    pass

    def test_func(self):
        layout = [[[self.gui.Text("A1")], [self.gui.Text("A2", size=(15, 3))]],
                  [[self.gui.Text("B1", size=(15, 3))], [self.gui.Text("B2", size=(15, 3))]],
                  [[self.gui.Text("C1", size=(15, 15))], [self.gui.Text("C2", size=(15, 15))]]]

        window = self.gui.Window("Test", layout, size=(1024, 768))

        while True:
            event, values = window.read()
            if event == "OK" or event == self.gui.WINDOW_CLOSED:
                break

    def show_data(self, data):
        layout = [[self.gui.Text(data)]]

        message = self.gui.Window("Message", layout, size=(self.window_length, self.window_height))

        while True:
            event, values = message.read()
            if event == "OK" or event == self.gui.WINDOW_CLOSED:
                break

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
                self.user = Client()
                if self.user.connect() == 1:
                    self.window.close()
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
                    logged = self.user.login(user_name, address)
                    if logged[0] == 1:
                        self.update_login()
                    else:
                        self.gui.popup_error("Couldnt login: " + logged[1])

            if event == "showFiles":
                files: list = self.user.ask_files_list()
                self.window["-FILE LIST2-"].update(values=files)

            if event == "-FILE LIST2-":
                file_name = values["-FILE LIST2-"][0]
                self.window["in3"].update(file_name)
                self.window["in4"].update(file_name)

            if event == "-DOWNLOAD-":
                file_name = self.window["in3"].get()
                self.user.client_sock.send(f"file,{file_name}".encode())
                ans = self.user.client_sock.recv(1024).decode()

                if ans == "OK":
                    self.gui.popup("File Found Starting Download")
                    with open(self.window["in4"].get(), 'wb') as file:
                        print("File Opened")
                        data = 1
                        while True:
                            data = self.user.client_sock.recv(1024)
                            if data.endswith("-@end@-".encode()):
                                file.write(data[:-7])
                                file.flush()
                                file.close()
                                print("File Closed")
                                break

                            file.write(data)

                    print("File Written")

            if event == "-USERS-":
                data = self.user.ask_users_list()
                self.window["-USERS LIST-"].update(values=data, visible=True)

            if event == "-USERS LIST-":
                user_name = values["-USERS LIST-"][0]
                self.window["in1"].update(user_name)

    def update_login(self):
        self.window["__Status__"].update("Online", text_color="green")
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
                    self.gui.Button("Show Online Users", disabled=True ,key="-USERS-", size=(15,), pad=(10,0))

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
                    self.gui.Input("", size=(25,),key="in4"),
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


if __name__ == '__main__':
    gui = GUI()
    gui.welcome_screen()
