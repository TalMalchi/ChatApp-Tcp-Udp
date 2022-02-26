import Client
from Model import connWrite, connRead, Model
from Client import Gui
import socket


class Controller:
    def __init__(self):
        self.model = Model(self)
        self.view = Gui(self)

    def start(self):
        self.model.start()
        self.model


if __name__ == '__main__':
    client = Controller()
    client.start()