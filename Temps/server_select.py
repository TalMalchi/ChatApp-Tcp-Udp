import socket
import select
import queue
import os

SERVERADDR = ("", 55000)
SIZE = 1024

in_sock: list = []
out_sock: list = []
message_queue: dict = {}
users: dict = {}


def remove_socket(sock):
    in_sock.remove(sock)
    for k, v in users:
        if v is sock:
            del users[k]
    del message_queue[sock]
    if sock in out_sock:
        out_sock.remove(sock)


def handle_msg(data):
    cmd = data.split("@")[0]



if __name__ == '__main__':

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(0)  # means non-blocking
    server.bind(SERVERADDR)
    server.listen()
    in_sock.append(server)

    while True:
        for sock in in_sock:
            print(sock)
        read_sock, write_sock, except_sock = select.select(in_sock, out_sock, in_sock)

        for r in read_sock:
            if r is server:
                client_sock, client_addr = r.accept()  # (socket,(ip,port))
                client_sock: socket.socket  # Just for convinice
                client_sock.setblocking(0)
                in_sock.append(client_sock)
                message_queue[client_sock] = []

                message_queue[client_sock].append("OK@SUCCESS\n")
                out_sock.append(client_sock)

            else:
                data = r.recv(1024).decode('utf-8')

                if data:
                    cmd = data.split("@")[0]


                else:
                    print("Client Diconnected")
                    r.close()
                    remove_socket(r)

        for w in write_sock:  # client socket
            for msg in message_queue[w]:  # לעבור על כל ההודעות בסוקט של הלקוח ולשלוח אותן
                w.send(msg.encode('utf-8'))

                # TODO check if the message sent succesfully
                # remove the message from thr queue
                message_queue[w].remove(msg)

            out_sock.remove(w)  # remove the sock_cilent from out_sock list

        for e in except_sock:
            print("Exception happend\n")
            remove_socket(e)
