import os
import socket
import threading

SERVERADDR = ("127.0.0.1", 55000)
SIZE = 1024

clients = []
active_sockets = {}


def client_main(client_sock: socket.socket, client_addr):
    global clients
    global active_sockets

    print(f"New Connection {client_addr} connected successfully.\n")
    client_sock.send("OK@Connected Succesfully.\n".encode('utf-8'))

    # LOGIN@Itay
    while True:
        msg = client_sock.recv(SIZE).decode('utf-8').split("@")
        cmd = msg[0]

        if cmd == "DISCONNECT":
            break

        elif cmd == "LOGIN":
            name = msg[1]
            if name in clients:
                client_sock.send("Error@User name already exists in the sistem\n".encode('utf-8'))
            else:
                client_sock.send("OK@Logged In\n".encode('utf-8'))
                clients.append(name)
                active_sockets[name] = client_sock

        elif cmd == "SHOWFILES":
            msg = "OK@"
            msg += '\n'.join(file for file in os.listdir(""))
            client_sock.send(msg.encode('utf-8'))

        elif cmd == "SHOWUSERS":
            msg = "OK@"
            msg += '\n'.join(c for c in clients)
            client_sock.send(msg.encode('utf-8'))

        elif cmd == "DOWNLOAD":
            pass

        elif cmd == "MSG":
            for curr in clients:
                sock: socket.socket = active_sockets[curr[0]]
                sock.send("MSG@".join(m + "@" for m in msg[1:]).encode('utf-8'))

        elif cmd == "PMSG":
            name = msg[1]
            active_sockets[name].send("PMSG@".join(m + "@" for m in msg[2:]).encode('utf-8'))

    print(f"{addr} Disconnected from server.\n")


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(SERVERADDR)

    server.listen()

    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=client_main, args=(client, addr))
