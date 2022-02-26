import os
import socket
import threading

SERVERADDR = ("", 55000)
SIZE = 1024

# clients = []
active_sockets = {}


# remove a user when he disconnect
def remove_socket(cl):
    for name, sock in active_sockets.items():
        if cl is sock:
            # update all the users that this client has left
            broadcast(f"Notice@{name} left the chat.\n")
            # remove the client from active_sockets dict
            del active_sockets[name]


# send a message to all activities users
def broadcast(msg):
    #  all over the active sockets, and send the message
    for v in active_sockets.values():
        v.send(msg.encode('utf-8'))


def client_main(client_sock: socket.socket, client_addr):

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
                remove_socket(client_sock)
                client_sock.close()
                break
            # connect the client to the chat
            elif cmd == "LOGIN":
                name = data.split("@")[0]
                if name in active_sockets.keys():
                    client_sock.send("Error@User name already exists in the system\n".encode('utf-8'))
                else:
                    client_sock.send("LOGGEDIN@Logged In Succesfully\n".encode('utf-8'))
                    active_sockets[name] = client_sock

            # gives all the files in server
            elif cmd == "SHOWFILES":
                msg = "SHOWFILES@"
                msg += '\n'.join(file for file in os.listdir("files"))
                client_sock.send(msg.encode('utf-8'))

            # shows all logged in users
            elif cmd == "SHOWUSERS":
                msg = "SHOWUSERS@"
                msg += '\n'.join(c for c in active_sockets.keys())
                client_sock.send(msg.encode('utf-8'))

            # download a file selected by the client
            elif cmd == "DOWNLOAD":
                pass
            # send a public message to all activities users using "broadcast" function
            elif cmd == "MSG":
                sender = data[0:data.find("@")]
                rest = data[data.find("@") + 1:]
                broadcast(f"MSG@{sender}@{rest}")

            # send a private message to another user
            elif cmd == "PMSG":
                sender = data[0:data.find("@")]
                rest = data[data.find("@") + 1:]
                sendto = rest[0:rest.find("@")]
                new_msg = rest[rest.find("@") + 1:]
                active_sockets[sendto].send(f"PMSG@{sender}@{new_msg}".encode('utf-8'))
                active_sockets[sender].send(f"PMSG_S@{sendto}@{new_msg}".encode('utf-8'))


        except:
            print(f"{addr} Disconnected from server.\n")
            for k, v in active_sockets.items():
                if v is client_sock:
                    del active_sockets[k]
            break


if __name__ == '__main__':
    # server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(SERVERADDR)

    server.listen(15)

    while True:
        # server thread
        client, addr = server.accept()
        thread = threading.Thread(target=client_main, args=(client, addr))
        thread.start()
