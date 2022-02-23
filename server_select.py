import socket
import select
import queue
import os

SERVERADDR = ("", 55000)
SIZE = 1024

in_sock = []
out_sock=[]
message_queue = {}
users={}


if __name__ == '__main__':

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(0) #means non-blocking
    server.bind(SERVERADDR)
    server.listen()
    in_sock.append(server)

    while True:
        read_sock, write_sock, except_sock= select.select(in_sock,out_sock, in_sock)

        for r in read_sock:
            if r is server:
                client_sock , client_addr = r.accept() #(socket,(ip,port))
                client_sock.setblocking(0)
                in_sock.append(client_sock)
                message_queue[client_sock] = queue.Queue()

            else:
                pass

        for w in write_sock: #client socket
            for msg in message_queue[w]: #לעבור על כל ההודעות בסוקט של הלקוח ולשלוח אותן
                w.send(msg)
                #check if the message sent succesfully
                message_queue[w].get(msg) # remove the message from thr queue

            out_sock.pop(w) # remove the sock_cilent from out_sock list


        for e in except_sock :
















