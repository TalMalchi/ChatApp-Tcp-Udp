import os
import socket
import threading

SERVERADDR = ("", 55000)
SIZE = 1024

# clients = []
active_sockets = {}


def remove_socket(cl):
    for name, sock in active_sockets:
        if cl is sock:
            broadcast(f"{name} left the chat.\n")
            del active_sockets[name]


def broadcast(msg):
    for v in active_sockets.values():
        v.send(msg.encode('utf-8'))


def client_main(client_sock: socket.socket, client_addr):
    global active_sockets

    print(f"New Connection {client_addr} connected successfully.\n")
    client_sock.send("LOGIN@Connected Succesfully.\n".encode('utf-8'))

    # LOGIN@Itay
    while True:
        try:
            msg = client_sock.recv(SIZE).decode('utf-8')
            cmd = msg[:msg.find("@")]
            data = msg[msg.find("@")+1:]
            print(msg,cmd,data)

            if cmd == "DISCONNECT":
                client_sock.close()
                remove_socket(client_sock)
                break

            elif cmd == "LOGIN":
                name = data
                if name in active_sockets.keys():
                    client_sock.send("Error@User name already exists in the system\n".encode('utf-8'))
                else:
                    client_sock.send("OK@Logged In\n".encode('utf-8'))
                    active_sockets[name] = client_sock

            elif cmd == "SHOWFILES":
                msg = "SHOWFILES@"
                msg += '\n'.join(file for file in os.listdir(""))
                client_sock.send(msg.encode('utf-8'))

            elif cmd == "SHOWUSERS":
                msg = "SHOWUSERS@"
                msg += '\n'.join(c for c in active_sockets.keys())
                client_sock.send(msg.encode('utf-8'))

            elif cmd == "DOWNLOAD":
                pass

            elif cmd == "MSG":
                broadcast(msg[1:])

            elif cmd == "PMSG":
                name = msg[1]
                active_sockets[name].send("PMSG@".join(m + "@" for m in msg[2:]).encode('utf-8'))

        except:
            print(f"{addr} Disconnected from server.\n")


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(SERVERADDR)

    server.listen(15)

    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=client_main, args=(client, addr))
        thread.start()

