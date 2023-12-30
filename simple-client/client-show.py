import socket
import random

HEADER = 8
IP = "192.168.1.117"
PORT = 5050
FORMAT = "utf-8"

MSG_DISC = "!disc"

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((IP, PORT))

def send_msg(msg):
    msg_len = len(bytes(msg.encode(FORMAT)))
    client_sock.sendall(str(msg_len).encode(FORMAT) + b' ' * (HEADER - len(str(msg_len))))
    msg = msg.encode(FORMAT)
    client_sock.sendall(msg)

def receive_msg():
    while True:
        msg_len = client_sock.recv(HEADER).decode(FORMAT)
        if msg_len:
            msg = client_sock.recv(int(msg_len)).decode(FORMAT)
            if msg == MSG_DISC:
                # not actually necessary to send "!disc", 
                # this is to stop the thread waiting for a message on shutdown
                send_msg("!disc")
                break
            
            print(msg)

token = input("Enter your token: ")
send_msg("!token " + token)

receive_msg()