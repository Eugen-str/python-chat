import socket
import random

IP = "192.168.1.117"
PORT = 5050
FORMAT = "utf-8"

MSG_DISC = "!disc"

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((IP, PORT))

def send_msg(msg):
    msg = msg.encode(FORMAT)
    client_sock.sendall(msg)

def receive_msg():
    while True:
        msg = client_sock.recv(1024).decode(FORMAT)
        if msg == MSG_DISC:
            send_msg("!disc")
            break
        if msg:
            print(msg)

send_msg("v" + str(random.randint(10000,50000)))

receive_msg()